# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

import logging

from dataclasses import dataclass

from sora.device.v1beta.service_pb2 import AuthServerInfoRequest
from sora.device.v1beta.service_pb2_grpc import DeviceServiceStub

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Auth0AuthServerInfo:
    host: str
    client_id: str
    audience: str


def auth0_auth_server_info(stub: DeviceServiceStub) -> Auth0AuthServerInfo:
    """
    Calls the AuthServerInfo RPC and parses the result into auth information
    for a Auth0 auth server.
    """
    resp = stub.AuthServerInfo(AuthServerInfoRequest())
    auth0 = resp.auth0
    return Auth0AuthServerInfo(
        host=auth0.host, client_id=auth0.client_id, audience=auth0.audience
    )
