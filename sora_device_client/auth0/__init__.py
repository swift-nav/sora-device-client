import requests
import time

from dataclasses import dataclass
from http import HTTPStatus
from rich import print
from typing import TypedDict

from . import jwt
from .info import Auth0AuthServerInfo


class DeviceCodeResponse(TypedDict):
    device_code: str
    expires_in: int
    interval: int  # interval with which to poll the api
    verification_uri_complete: str
    verification_uri: str
    user_code: str


class OauthTokenReponse(TypedDict):
    access_token: str


@dataclass(frozen=True)
class Auth0Client:
    info: Auth0AuthServerInfo

    def _get_device_code(self) -> DeviceCodeResponse:
        payload = {
            "audience": self.info.audience,
            "client_id": self.info.client_id,
            "scope": "",  # NOTE: scopes are space delimited
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }
        r = requests.post(
            f"https://{self.info.host}/oauth/device/code", payload, headers
        )
        if r.status_code != HTTPStatus.OK:
            raise Exception(f"Failed to get device code: {r.status_code}")

        return r.json()

    def _poll_for_tokens(
        self, device_code: str, interval: int, expires_in: int
    ) -> OauthTokenReponse:
        time_estimate = 0
        delay = interval
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": self.info.client_id,
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }

        while time_estimate < expires_in:
            # for information on how this endpoint is rate limited.
            r = requests.post(f"https://{self.info.host}/oauth/token", payload, headers)
            if r.status_code != HTTPStatus.OK:
                error = r.json()["error"]
                if error == "slow_down":
                    delay *= interval
                elif error == "expired_token":
                    raise Exception("Token expired")
                elif error == "access_denied":
                    raise Exception("Access denied")

                time_estimate += delay
                time.sleep(delay)
                continue

            return r.json()

        raise Exception("Took too long to authenticate in the browser")

    # See https://auth0.com/docs/get-started/authentication-and-authorization-flow/call-your-api-using-the-device-authorization-flow
    def register_device(self) -> jwt.ExtractedData:
        device_code_data = self._get_device_code()
        print(
            f"Continue login at: {device_code_data['verification_uri_complete']} and verify that the code matches {device_code_data['user_code']}"
        )
        token_data = self._poll_for_tokens(
            device_code_data["device_code"],
            device_code_data["interval"],
            device_code_data["expires_in"],
        )

        access_token = token_data["access_token"]

        return jwt.extract_data_from_token(access_token)
