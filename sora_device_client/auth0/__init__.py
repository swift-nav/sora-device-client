# Copyright (C) 2022 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>

# This source is subject to the license found in the file 'LICENCE' which must
# be be distributed together with this source. All other rights reserved.

import requests
import time

from typing import *
from dataclasses import dataclass
from http import HTTPStatus
from rich import print

from sora_device_client.auth0.info import Auth0AuthServerInfo
from sora_device_client.config.device import DeviceConfig, extract_claims


class DeviceCodeResponse(TypedDict):
    device_code: str
    expires_in: int
    interval: int  # interval with which to poll the api
    verification_uri_complete: str
    verification_uri: str
    user_code: str


class OauthTokenResponse(TypedDict):
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

        return cast(DeviceCodeResponse, r.json())

    def _poll_for_tokens(
        self, device_code: str, interval: int, expires_in: int
    ) -> OauthTokenResponse:
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

            return cast(OauthTokenResponse, r.json())

        raise Exception("Took too long to authenticate in the browser")

    # See https://auth0.com/docs/get-started/authentication-and-authorization-flow/call-your-api-using-the-device-authorization-flow
    def register_device(self) -> DeviceConfig:
        device_code_data = self._get_device_code()
        print(
            f"Continue login at: {device_code_data['verification_uri_complete']} and verify that the code matches {device_code_data['user_code']}"
        )
        token_data = self._poll_for_tokens(
            device_code_data["device_code"],
            device_code_data["interval"],
            device_code_data["expires_in"],
        )

        device_access_token = extract_claims(token_data["access_token"])[
            "device_access_token"
        ]

        return DeviceConfig(device_access_token)
