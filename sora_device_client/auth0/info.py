import grpc
import logging

from dataclasses import dataclass
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp

import sora.v1beta.common_pb2 as common_pb
import sora.device.v1beta.service_pb2_grpc as device_grpc
import sora.device.v1beta.service_pb2 as device_pb2

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Auth0AuthServerInfo:
    host: str
    client_id: str
    audience: str


def auth0_auth_server_info(channel) -> Auth0AuthServerInfo:
    try:
        resp: device_pb2.AuthServerInfoResponse = channel.AuthServerInfo(
            device_pb2.AuthServerInfoRequest()
        )
        info = resp.info
        auth0 = info.auth0
        auth_server_url = auth0.auth_server_url
        client_id = auth0.client_id
        audience = auth0.audience
    except:
        raise

    channel.close()

    return Auth0AuthServerInfo(
        auth_server_url=auth_server_url, client_id=client_id, audience=audience
    )
