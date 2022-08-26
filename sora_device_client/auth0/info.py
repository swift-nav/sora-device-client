import logging

from dataclasses import dataclass

from rich import print

from sora.device.v1beta.service_pb2 import AuthServerInfoRequest
from sora.device.v1beta.service_pb2_grpc import DeviceServiceStub

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Auth0AuthServerInfo:
    host: str
    client_id: str
    audience: str


def auth0_auth_server_info(stub: DeviceServiceStub) -> Auth0AuthServerInfo:
    resp = stub.AuthServerInfo(AuthServerInfoRequest())
    auth0 = resp.auth0
    return Auth0AuthServerInfo(
        host=auth0.host, client_id=auth0.client_id, audience=auth0.audience
    )
