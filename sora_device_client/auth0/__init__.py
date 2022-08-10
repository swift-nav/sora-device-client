import requests
import time

from dataclasses import dataclass
from http import HTTPStatus
from rich import print
from rich.console import Console


@dataclass
class Auth0Client:
    host: str
    client_id: str
    audience: str

    def _get_device_code(self) -> dict:
        payload = {
            "client_id": self.client_id,
            "scope": "send:device_state,send:events,offline_access",
            "audience": "",
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        r = requests.post(f"https://{self.host}/oauth/device/code", payload, headers)
        if r.status_code != HTTPStatus.OK:
            raise Exception(f"Failed to get device code: {r.status_code}")

        return r.json()

    def _poll_for_token(self, device_code: str, interval: int) -> dict:
        delay = interval
        while True:
            payload = {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
                "client_id": self.client_id,
            }
            headers = {"content-type": "application/x-www-form-urlencoded"}
            r = requests.post(f"https://{self.host}/oauth/token", payload, headers)
            if r.status_code != HTTPStatus.OK:
                error = r.json()["error"]
                if error == "slow_down":
                    delay *= interval
                elif error == "expired_token":
                    raise Exception("Token expired")
                elif error == "access_denied":
                    raise Exception("Access Denied")

                time.sleep(delay)
                continue

            return r.json()

    def register_device(self):
        data = self._get_device_code()
        print(f"Navigate to: {data['verification_uri_complete']}")
        console = Console()
        console.input("Press enter to confirm you have logged in via the uri")

        token = self._poll_for_token(data["device_code"], data["interval"])
        return token
