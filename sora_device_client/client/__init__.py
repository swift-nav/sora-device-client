import math
import grpc
import signal
import threading
import time
import persistqueue

from typing import *
from numbers import Number
from abc import ABC
from contextlib import contextmanager
from dataclasses import dataclass
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp
from logging import getLogger, Logger
from persistqueue import SQLiteAckQueue
from rich import print

import sora.v1beta.common_pb2 as common_pb
import sora.device.v1beta.service_pb2_grpc as device_grpc
import sora.device.v1beta.service_pb2 as device_pb2

from sora_device_client.config.device import DeviceConfig
from sora_device_client.config.server import ServerConfig
from sora_device_client.config import DATA_DIR


class ExitMain(Exception):
    pass


def _device_service_channel(cfg: ServerConfig) -> grpc.Channel:
    """
    Creates a GRPC channel to the device service.
    """
    logger = getLogger(__name__ + ".grpc_channel")

    server_opts = [
        ("grpc.keepalive_time_ms", 30_000),
        ("grpc.keepalive_timeout_ms", 10_000),
    ]
    if cfg.disable_tls:
        chan = grpc.insecure_channel(cfg.target(), server_opts)
    else:
        creds = grpc.ssl_channel_credentials()
        chan = grpc.secure_channel(cfg.target(), creds, server_opts)

    def chan_health_listener(state: grpc.ChannelConnectivity) -> None:
        if state in {
            grpc.ChannelConnectivity.TRANSIENT_FAILURE,
            grpc.ChannelConnectivity.SHUTDOWN,
        }:
            logger.warn("GRPC channel state: %s", state)
        else:
            logger.debug("GRPC channel state: %s", state)

    chan.subscribe(chan_health_listener)

    return chan


@contextmanager
def device_service_channel(cfg: ServerConfig) -> Generator[grpc.Channel, None, None]:
    chan = _device_service_channel(cfg)
    grpc.channel_ready_future(chan).result(timeout=10)
    try:
        yield chan
    finally:
        chan.close()


T = TypeVar("T")


class SizedIterable(ABC, Generic[T], Iterable[T], Sized):
    pass


@dataclass
class SoraDeviceClient:
    device_config: DeviceConfig
    server_config: ServerConfig
    state_queue_depth: int = 0
    event_queue_depth: int = 0
    logger: Logger = getLogger(__name__)

    def __post_init__(self) -> None:
        """
        SORA-412: To save device_client data on to disk instead of in-memory.
        When there is any issue connecting to server, the data on disk can be retrieved later
        when the connectivity is restored and sent to server.
        """
        self._state_queue = SQLiteAckQueue(
            DATA_DIR.joinpath("states"), multithreading=True, auto_commit=True
        )
        self._event_queue = SQLiteAckQueue(
            DATA_DIR.joinpath("events"), multithreading=True, auto_commit=True
        )
        self.metadata = [("authorization", f"Bearer {self.device_config.access_token}")]
        self._state_worker = threading.Thread(
            target=self._state_stream_sender,
            args=(self._state_queue,),
            daemon=True,
        )
        self._event_worker = threading.Thread(
            target=self._event_stream_sender,
            args=(self._event_queue,),
            daemon=True,
        )
        self._stop = threading.Event()
        self._chan: Optional[grpc.Channel] = None
        self._stub: Optional[device_grpc.DeviceServiceStub] = None

    def connect(self) -> None:
        target = self.server_config.target()
        self.logger.info(f"Connecting to Sora server @ {target}")

        self._chan = _device_service_channel(self.server_config)

        try:
            grpc.channel_ready_future(self._chan).result(timeout=10)
            self._stub = device_grpc.DeviceServiceStub(self._chan)
            self.logger.info("Connected")
        except:
            self._chan.close()
            self._chan = None
            self._stub = None
            self.logger.info("Disconnected")
            raise

    def start(self) -> None:
        def signal_handler(signal: int, frame: Any) -> None:
            """
            Ignore the signal and frame and just exit the process.
            It is expected that the process will be restarted by a external orchestration system.
            """
            raise ExitMain()

        signal.signal(signal.SIGUSR1, signal_handler)
        self.connect()
        self._state_worker.start()
        self._event_worker.start()
        print(f"Sending state as device {self.device_config.device_name} to project.")
        # TODO: print urls of all projects the device is sending state to

    def stop(self, timeout: int) -> None:
        try:
            self._stop.set()
            zero = time.monotonic()

            self._state_worker.join(timeout)
            if self._state_worker.is_alive():
                raise TimeoutError(f"Failed to finish requests in {timeout} seconds!")

            elapsed = time.monotonic() - zero
            remaining = max(timeout - elapsed, 0)
            self._event_worker.join(timeout=remaining)
            if self._event_worker.is_alive():
                raise TimeoutError(f"Failed to finish requests in {timeout} seconds!")
        finally:
            states = self._state_queue.ready_count() + self._state_queue.unack_count()
            events = self._event_queue.ready_count() + self._event_queue.unack_count()
            if states + events > 0:
                self.logger.warn(
                    "There are %d states and %d events that may not have been received. "
                    "They will be re-tried next time you run `sora`.",
                    states,
                    events,
                )

    """ 
    SQLiteAckQueue status
        inited = '0'
        ready = '1'
        unack = '2'
        acked = '5'
        ack_failed = '9'
    """

    @contextmanager
    def iter_ack_queue(
        self,
        que: SQLiteAckQueue,
        max_pending_acks: Union[int, float] = math.inf,
    ) -> Generator[SizedIterable[Any], None, None]:
        """
        This is used to iterate through items in an queue.
        It is to be used as a `with` statement: if the contents of the `with` block
        complete successfully, the items will be acknowledged as successful. Example:
        ```
            with iter_ack_queue(queue) as items:
                for item in items:
                    stream.push(item)
                stream.close() # maybe this will raise BadConnection()

            # if the block finished, then the items are acknowledged on the queue,
            # and the count is available in len(items)
            assert len(items) > 0

            # if the block threw, then the items are not acknowledged, (and the thrown
            # exception will propagate as normal for you to deal with)
        ```

        If you pass `max_pending_acks`, then at most `max_pending_acks` items will
        be yielded from the queue, to give whatever success-ensuring functions you have
        in your `with` block a chance to execute.
        """
        # Change any status='UNACK' to status='READY'. Without this, UNACK'd items would not be
        # picked up until we restart the process, and this would result in devicestates being sent
        # out-of-order.
        que.resume_unack_tasks()
        # Clear any acked data from disk, we don't need it anymore.
        que.clear_acked_data(keep_latest=500)

        yielded: List[int] = []

        def iterator() -> Iterator[Any]:
            while len(yielded) < max_pending_acks and not self._stop.is_set():
                try:
                    entry = que.get(raw=True, timeout=1)
                except persistqueue.Empty:
                    # could just .get() and block with no timeout, but then
                    # it's hard to stop cleanly because we can't wait for
                    # self._stop.
                    continue
                id: int
                id, x = entry["pqid"], entry["data"]
                yielded.append(id)
                # if there is an error in stream, this yield will never complete.
                yield x

        # this might be overcomplicating things.. I want the consumer to be able
        # to call len(items) to get how many things got acked, just for logging
        # purposes.

        class WithLen(SizedIterable[T]):
            def __init__(self, it: Iterable[T]):
                self.it = it
                self.acked: Optional[int] = None

            def __len__(self) -> int:
                if self.acked is None:
                    raise Exception(
                        "tried to read len(iter_ack_queue) before your with: block was finished!"
                    )
                return self.acked

            def __iter__(self) -> Generator[T, None, None]:
                yield from self.it

        it = WithLen(iterator())

        yield it

        # if we reach here, no exception has occured, so we ack everything.
        for id in yielded:
            que.ack(id=id)
            self.logger.debug(f"Acknowledged queue itemId: {id}")
        it.acked = len(yielded)

    def _state_stream_sender(self, que: SQLiteAckQueue) -> None:
        assert self._stub is not None
        while not self._stop.is_set():
            self.logger.debug("opening StreamDeviceState")
            try:
                with self.iter_ack_queue(que, max_pending_acks=50) as items:

                    def log_items() -> Generator[Any, None, None]:
                        for x in items:
                            self.logger.info(
                                "Sending state for device %s:",
                                self.device_config.device_id,
                            )
                            yield x

                    self._stub.StreamDeviceState(log_items(), metadata=self.metadata)
                self.logger.info(
                    "Confirmed receipt of %d states for device %s",
                    len(items),
                    self.device_config.device_id,
                )

            except grpc.RpcError as e:
                self.logger.error(
                    "Could not connect to server %s. Status code: %s",
                    f"{self.server_config.host}:{self.server_config.port}",
                    e.code(),
                )
                self.logger.debug("grpc exception:", exc_info=e)

            except Exception as e:
                self.logger.error(
                    "Unexpected error when streaming state to server %s",
                    f"{self.server_config.host}:{self.server_config.port}",
                    exc_info=e,
                )

            else:
                # finished with no error, this is expected so we loop with no wait
                continue
            self.logger.warn(
                "StreamDeviceState finished (probably because of connection problems), retrying after 5 seconds..."
            )
            time.sleep(5)

    def _event_stream_sender(self, que: SQLiteAckQueue) -> None:
        assert self._stub is not None
        while not self._stop.is_set():
            # a naive person might think we could ack immediately after AddEvent finishes without error,
            # but then that person wouldn't have spent four hours of horror reading through the grpc github
            # issue tracker.
            try:
                with self.iter_ack_queue(que, max_pending_acks=10) as items:
                    for x in items:
                        self.logger.info(
                            "Sending event for device %s:", self.device_config.device_id
                        )
                        self._stub.AddEvent(x, metadata=self.metadata)
                self.logger.info(
                    "Confirmed receipt of %d events for device %s",
                    len(items),
                    self.device_config.device_id,
                )
            except grpc.RpcError as e:
                self.logger.error(
                    "Could not connect to server %s. Status code: %s",
                    f"{self.server_config.host}:{self.server_config.port}",
                    e.code(),
                )
                self.logger.debug("grpc exception:", exc_info=e)
            except Exception as e:
                self.logger.error(
                    "Unexpected error when sending events to server %s",
                    f"{self.server_config.host}:{self.server_config.port}",
                    exc_info=e,
                )
            else:
                # finished with no error, this is expected so we loop with no wait
                continue
            self.logger.warn(
                "AddEvent loop finished (probably because of connection problems), retrying after 5 seconds..."
            )
            time.sleep(5)

    def add_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> None:
        payload = payload or {}
        timestamp = Timestamp()
        payload_pb = Struct()
        payload_pb.update(payload)
        timestamp.GetCurrentTime()
        event = common_pb.Event(
            device_id=str(self.device_config.device_id),
            time=timestamp,
            pos=common_pb.Position(lat=lat or 0, lon=lon or 0),
            type=event_type,
            payload=payload_pb,
        )
        self.logger.debug("Queing event for device %s:", self.device_config.device_id)
        self.logger.debug(event)
        self._event_queue.put(device_pb2.StreamEventRequest(event=event))

    def send_state(
        self,
        state: Optional[Dict[str, Any]] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> None:
        state = state or {}
        timestamp = Timestamp()
        state_pb = Struct()
        state_pb.update(state or {})
        timestamp.GetCurrentTime()
        device_state = common_pb.DeviceState(
            # Note: this will be replaced the by the device_id claimed the JWT
            device_id=str(self.device_config.device_id),
            time=timestamp,
            orientation=None,
            pos=common_pb.Position(lat=lat or 0, lon=lon or 0),
            user_data=state_pb,
        )
        self.logger.debug("Queuing state for device %s:", self.device_config.device_id)
        self.logger.debug(device_state)
        self._state_queue.put(device_pb2.StreamDeviceStateRequest(state=device_state))
