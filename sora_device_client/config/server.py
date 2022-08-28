from urllib.parse import urlparse

# TODO(triarius): replace with a production url when there is a production
# environment.
DEFAULT_SERVER_URL = "https://grpc.staging.sora.swiftnav.com"
DEFAULT_PORT = 443


class ServerConfig:
    def __init__(self, url: str):
        self._parsed_url = urlparse(url)
        self.host = self._parsed_url.hostname or "localhost"
        self.port = self._parsed_url.port or DEFAULT_PORT
        self.disable_tls = self._parsed_url.scheme != "https"

    def target(self) -> str:
        return f"{self.host}:{self.port}"

    def __repr__(self):
        return f"{self._parsed_url.geturl()}"
