import requests
import time

from dataclasses import dataclass
from http import HTTPStatus
from rich import print
from rich.console import Console
from typing import Tuple, TypedDict
from uuid import UUID

from . import jwt

AUTH0_DOMAIN = "nepa-test.au.auth0.com"
AUTH0_CLIENT_ID = "rg4u984ZG8OKaMUL44geh397QpX1ozcr"
AUTH0_AUDIENCE = "http://localhost:10000:/sora.device.v1beta.DeviceService"


class DeviceCodeData(TypedDict):
    device_code: str
    interval: int
    verification_uri_complete: str
    verification_uri: str
    user_code: str


class TokenReponse(TypedDict):
    access_token: str
    device_id: str


@dataclass
class Auth0Client:
    host: str
    client_id: str
    audience: str

    def _get_device_code(self) -> DeviceCodeData:
        payload = {
            "audience": self.audience,
            "client_id": self.client_id,
            "scope": "",  # NOTE: scopes are space delimited
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }
        r = requests.post(f"https://{self.host}/oauth/device/code", payload, headers)
        if r.status_code != HTTPStatus.OK:
            raise Exception(f"Failed to get device code: {r.status_code}")

        return r.json()

    def _poll_for_tokens(self, device_code: str, interval: int) -> TokenReponse:
        delay = interval
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": self.client_id,
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }
        while True:
            r = requests.post(f"https://{self.host}/oauth/token", payload, headers)
            if r.status_code != HTTPStatus.OK:
                error = r.json()["error"]
                if error == "slow_down":
                    delay *= interval
                elif error == "expired_token":
                    raise Exception("Token expired")
                elif error == "access_denied":
                    raise Exception("Access denied")

                time.sleep(delay)
                continue

            return r.json()

    def register_device(self) -> Tuple[UUID, str]:
        device_code_data = self._get_device_code()
        print(f"Continue login at: {device_code_data['verification_uri_complete']}")
        print(f"and verify that the code matches {device_code_data['user_code']}")
        console = Console()
        console.input("Press enter after you have logged in via the above URL.\n")

        token_data = self._poll_for_tokens(
            device_code_data["device_code"], device_code_data["interval"]
        )

        access_token = token_data["access_token"]
        device_id, device_access_token = jwt.extractDeviceIdAndAcessTokenFromJWT(
            access_token
        )

        return (device_id, device_access_token)
