# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

from urllib.parse import urlparse

DEFAULT_SERVER_URL = "https://grpc.sora.swiftnav.com"
DEFAULT_PORT = 443


class ServerConfig:
    def __init__(self, url: str):
        self._parsed_url = urlparse(url)
        self.host = self._parsed_url.hostname or "localhost"
        self.port = self._parsed_url.port or DEFAULT_PORT
        self.disable_tls = self._parsed_url.scheme != "https"

    def target(self) -> str:
        return f"{self.host}:{self.port}"

    def __repr__(self) -> str:
        return f"{self._parsed_url.geturl()}"
