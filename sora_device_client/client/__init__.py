import logging
import grpc
import os
import queue
import signal
import threading
from persistqueue import SQLiteAckQueue

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp
from logging import getLogger, Logger
from rich import print

import sora.v1beta.common_pb2 as common_pb
import sora.device.v1beta.service_pb2_grpc as device_grpc
import sora.device.v1beta.service_pb2 as device_pb2

from sora_device_client.config.device import DeviceConfig
from sora_device_client.config.server import ServerConfig


class ExitMain(Exception):
    pass


@contextmanager
def device_service_channel(cfg: ServerConfig) -> Generator[grpc.Channel, None, None]:
    if cfg.disable_tls:
        chan = grpc.insecure_channel(cfg.target())
    else:
        creds = grpc.ssl_channel_credentials()
        chan = grpc.secure_channel(cfg.target(), creds)
    grpc.channel_ready_future(chan).result(timeout=10)
    try:
        yield chan
    finally:
        chan.close()


@dataclass
class SoraDeviceClient:
    device_config: DeviceConfig
    server_config: ServerConfig
    state_queue_depth: int = 0
    event_queue_depth: int = 0
    logger: Logger = getLogger(__name__)

    def __post_init__(self):
        """
        SORA-412: To save device_client data on to disk instead of in-memory.
        When there is any issue connecting to server, the data on disk can be retrieved later
        when the connectivity is restored and sent to server.
        """
        self._state_queue = SQLiteAckQueue(
            "../state", multithreading=True, auto_commit=True
        )
        self._event_queue = SQLiteAckQueue(
            "../event", multithreading=True, auto_commit=True
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
        self._chan = None
        self._stub = None

    def connect(self):
        target = self.server_config.target()
        self.logger.info(f"Connecting to Sora server @ {target}")

        if self.server_config.disable_tls:
            self._chan = grpc.insecure_channel(target)
        else:
            creds = grpc.ssl_channel_credentials()
            self._chan = grpc.secure_channel(target, creds)

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

    def start(self):
        def signal_handler(signal, frame):
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

    """ 
    SQLiteAckQueue status
        inited = '0'
        ready = '1'
        unack = '2'
        acked = '5'
        ack_failed = '9'
    """

    def iter_ack_queue(self, que: SQLiteAckQueue):
        # Change any status='UNACK' to status='READY'. Without this, UNACK'd items would not be
        # picked up until we restart the process, and this would result in devicestates being sent
        # out-of-order.
        que.resume_unack_tasks()
        # Clear any acked data from disk, we don't need it anymore.
        que.clear_acked_data(keep_latest=500)
        while True:
            x = que.get()
            # if there is an error in stream, this yield will never complete.
            yield x
            preId = que.ack(x)
            self.logger.debug(f"Acknowledged queue itemId:  {preId}")

    def _state_stream_sender(self, que: SQLiteAckQueue):
        while True:
            self.logger.debug("opening StreamDeviceState")
            try:
                self._stub.StreamDeviceState(
                    self.iter_ack_queue(que), metadata=self.metadata
                )
            except grpc._channel._InactiveRpcError as e:
                self.logger.info(f"grpc StatusCode: {e.code}")
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    self.logger.error(
                        f"Server {self.server_config.host}:{self.server_config.port} unavailable. This is expected during a deploy or when server is down : {e}"
                    )
                else:
                    self.logger.error(
                        f"Could not connect to server {self.server_config.host}:{self.server_config.port}: {e}"
                    )

            except Exception as e:
                self.logger.error(
                    f"Unexpected error when streaming state to server {self.server_config.host}:{self.server_config.port} : {e}",
                    exc_info=e,
                )
            self.logger.warn("StreamDeviceState connection closed, retrying after 5 seconds...")
            time.sleep(5)

    def _event_stream_sender(self, que: SQLiteAckQueue):
        while True:
            try:
                for x in self.iter_ack_queue(que):
                    self._stub.AddEvent(x, metadata=self.metadata)
            except Exception as e:
                self.logger.error(
                    f"Unexpected error when streaming state to server {self.server_config.host}:{self.server_config.port} : {e}"
                )
            self.logger.warn("AddEvent loop finished (probably because of connection problems), retrying after 5 seconds...")
            time.sleep(5)

    def add_event(self, event_type, payload=None, lat=None, lon=None):
        payload = payload or {}
        timestamp = Timestamp()
        payload_pb = Struct()
        payload_pb.update(payload)
        timestamp.GetCurrentTime()
        event = common_pb.Event(
            device_id=str(self.device_config.device_id),
            time=timestamp,
            pos=common_pb.Position(lat=lat, lon=lon),
            type=event_type,
            payload=payload_pb,
        )
        self.logger.info("Sending event for device %s:", self.device_config.device_id)
        self.logger.debug(event)
        self._event_queue.put(device_pb2.StreamEventRequest(event=event))

    def send_state(self, state=None, lat=None, lon=None):
        timestamp = Timestamp()
        state_pb = Struct()
        state_pb.update(state or {})
        timestamp.GetCurrentTime()
        device_state = common_pb.DeviceState(
            # Note: this will be replaced the by the device_id claimed the JWT
            device_id=str(self.device_config.device_id),
            time=timestamp,
            orientation=common_pb.Orientation(
                pitch=0,
                yaw=(180 - state["bearing"] if "bearing" in state else 180),
                roll=90,
            ),
            pos=common_pb.Position(lat=lat, lon=lon),
            user_data=state_pb,
        )
        self.logger.info("Sending state for device %s:", self.device_config.device_id)
        self.logger.debug(device_state)
        self._state_queue.put(device_pb2.StreamDeviceStateRequest(state=device_state))
