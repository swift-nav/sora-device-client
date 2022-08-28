from urllib.parse import urlparse

# TODO(triarius): replace with a production url when there is a production
# environment.
DEFAULT_SERVER_URL = "https://grpc.staging.sora.swiftnav.com"
DEFAULT_PORT = 443


class ServerConfig:
    def __init__(self, url: str):
        parsed = urlparse(url)
        self.host = parsed.netloc
        self.port = parsed.port or DEFAULT_PORT
        self.disable_tls = parsed.scheme != "https"

    def target(self) -> str:
        return f"{self.host}:{self.port}"
