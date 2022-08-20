import grpc
import logging
import os
import queue
import signal
import threading

from dataclasses import dataclass
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.struct_pb2 import Struct

import sora.v1beta.common_pb2 as common_pb
import sora.device.v1beta.service_pb2_grpc as device_grpc
import sora.device.v1beta.service_pb2 as device_pb2

log = logging.getLogger(__name__)


class ExitMain(Exception):
    pass


def signal_handler(signal, frame):
    raise ExitMain()


class SoraDeviceClient:
    def __init__(
        self,
        device_id,
        device_access_token,
        host,
        port,
        disable_tls=False,
        state_queue_depth=0,
        event_queue_depth=0,
    ):
        self._device_id = device_id
        log.info("Device ID: %s", self._device_id)
        self._device_access_token = device_access_token
        self._host = host
        self._port = port
        self._disable_tls = disable_tls
        self._state_queue = queue.Queue(maxsize=state_queue_depth)
        self._event_queue = queue.Queue(maxsize=event_queue_depth)
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
        target = self._host + ":" + str(self._port)
        log.info("Connecting to Sora server @ %s", target)

        if self._disable_tls:
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
        signal.signal(signal.SIGUSR1, signal_handler)
        self.connect()
        self._state_worker.start()
        self._event_worker.start()

    def _state_stream_sender(self, itr):
        try:
            self._stub.StreamDeviceState(itr)
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
        for x in itr:
            self._stub.AddEvent(x)

    def add_event(self, event_type, payload={}, device_id=None, lat=None, lon=None):
        timestamp = Timestamp()
        payload_pb = Struct()
        payload_pb.update(payload)
        timestamp.GetCurrentTime()
        if device_id is None:
            device_id = self._device_id
        event = common_pb.Event(
            device_id=str(device_id),
            time=timestamp,
            pos=common_pb.Position(lat=lat, lon=lon),
            type=event_type,
            payload=payload_pb,
        )
        log.info("Sending event for device %s:", device_id)
        log.debug(event)
        self._event_queue.put(event)

    def send_state(self, state=None, device_id=None, lat=None, lon=None):
        if state is None:
            state = {}
        timestamp = Timestamp()
        state_pb = Struct()
        state_pb.update(state)
        timestamp.GetCurrentTime()
        if device_id is None:
            device_id = self._device_id
        device_state = common_pb.DeviceState(
            device_id=str(device_id),
            time=timestamp,
            orientation=common_pb.Orientation(
                pitch=0,
                yaw=(180 - state["bearing"] if "bearing" in state else 180),
                roll=90,
            ),
            pos=common_pb.Position(lat=lat, lon=lon),
            user_data=state_pb,
        )
        log.info("Sending state for device %s:", device_id)
        log.debug(device_state)
        self._state_queue.put(device_pb2.StreamDeviceStateRequest(state=device_state))
