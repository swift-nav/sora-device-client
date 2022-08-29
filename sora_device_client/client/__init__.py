import grpc
import logging
import os
import queue
import signal
import threading

from contextlib import contextmanager
from collections.abc import Generator
from dataclasses import dataclass
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp
from uuid import UUID

import sora.v1beta.common_pb2 as common_pb
import sora.device.v1beta.service_pb2_grpc as device_grpc
import sora.device.v1beta.service_pb2 as device_pb2

from sora_device_client.config.server import ServerConfig

log = logging.getLogger(__name__)


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
    device_uuid: UUID
    access_token: str
    server_config: ServerConfig
    state_queue_depth: int = 0
    event_queue_depth: int = 0

    def __post_init__(self):
        self.device_id = str(self.device_uuid)
        self._state_queue = queue.Queue(maxsize=self.state_queue_depth)
        self._event_queue = queue.Queue(maxsize=self.event_queue_depth)
        self._state_worker = threading.Thread(
            target=self._state_stream_sender,
            args=(iter(self._state_queue.get, None),),
            daemon=True,
        )
        self._event_worker = threading.Thread(
            target=self._event_stream_sender,
            args=(iter(self._event_queue.get, None),),
            daemon=True,
        )
        self._chan = None
        self._stub = None

    def connect(self):
        target = self.server_config.target()
        log.info(f"Connecting to Sora server @ {target}")

        if self.server_config.disable_tls:
            self._chan = grpc.insecure_channel(target)
        else:
            creds = grpc.ssl_channel_credentials()
            self._chan = grpc.secure_channel(target, creds)

        try:
            grpc.channel_ready_future(self._chan).result(timeout=10)
            self._stub = device_grpc.DeviceServiceStub(self._chan)
            log.info("Connected")
        except:
            log.info("Disconnected")
            self._chan.close()
            self._chan = None
            self._stub = None
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

    def _state_stream_sender(self, itr):
        metadata = [("authorization", f"Bearer {self.access_token}")]
        try:
            self._stub.StreamDeviceState(itr, metadata=metadata)
        except grpc._channel._InactiveRpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                logging.info(
                    "Server unavaliable so restarting client. This is expected during a a deploy."
                )
            else:
                logging.warn(
                    f"Could not connect to server for an unexpected reason: {e}"
                )
        except Exception as e:
            logging.warn(f"Unexpected error when streaming state to server: {e}")
        finally:
            os.kill(os.getpid(), signal.SIGUSR1)

    def _event_stream_sender(self, itr):
        metadata = [("authorization", f"Bearer {self.access_token}")]
        try:
            self._stub.StreamEvent(itr, metadata=metadata)
        except grpc._channel._InactiveRpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                logging.info(
                    "Server unavaliable so restarting client. This is expected during a a deploy."
                )
            else:
                logging.warn(
                    f"Could not connect to server for an unexpected reason: {e}"
                )
        except Exception as e:
            logging.warn(f"Unexpected error when streaming event to server: {e}")
        finally:
            os.kill(os.getpid(), signal.SIGUSR1)

    def add_event(self, event_type, payload=None, lat=None, lon=None):
        payload = payload or {}
        timestamp = Timestamp()
        payload_pb = Struct()
        payload_pb.update(payload)
        timestamp.GetCurrentTime()
        event = common_pb.Event(
            device_id=str(self.device_id),
            time=timestamp,
            pos=common_pb.Position(lat=lat, lon=lon),
            type=event_type,
            payload=payload_pb,
        )
        log.info("Sending event for device %s:", self.device_id)
        log.debug(event)
        self._event_queue.put(device_pb2.StreamEventRequest(event=event))

    def send_state(self, state=None, lat=None, lon=None):
        if state is None:
            state = {}
        timestamp = Timestamp()
        state_pb = Struct()
        state_pb.update(state)
        timestamp.GetCurrentTime()
        device_state = common_pb.DeviceState(
            device_id=str(self.device_id),
            time=timestamp,
            orientation=common_pb.Orientation(
                pitch=0,
                yaw=(180 - state["bearing"] if "bearing" in state else 180),
                roll=90,
            ),
            pos=common_pb.Position(lat=lat, lon=lon),
            user_data=state_pb,
        )
        log.info("Sending state for device %s:", self.device_id)
        log.debug(device_state)
        self._state_queue.put(device_pb2.StreamDeviceStateRequest(state=device_state))
