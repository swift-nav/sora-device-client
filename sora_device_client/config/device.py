import json

from typing import *
from functools import cached_property
from base64 import b64decode
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeviceConfig:
    access_token: str

    @cached_property
    def _extracted_claims(self) -> Dict[str, Any]:
        dat = self.access_token
        return extract_claims(dat)

    @cached_property
    def app_url(self) -> str:
        return str(self._extracted_claims["app_url"])

    @cached_property
    def device_id(self) -> UUID:
        return UUID(self._extracted_claims["device_id"])

    @cached_property
    def device_name(self) -> str:
        return str(self._extracted_claims["device_name"])


def extract_claims(jwt: str) -> Dict[str, Any]:
    """
    Given a JWT from the Auth Server that is issued to this device as part of a
    Device Authorization Flow, this function will extract the claim
    `device_access_token`. This is also a JWT, but one that is issued by the
    backend. This function will also extract the `device_id` from
    `device_access_token`.

    Warning: this does not verify either JWT in any way. That is the
    responsibility of the sora backend. This JWT should have been received
    from the Auth Server on a secure channel. The backend will verify the
    signature of `device_access_token` so it must not be modifed when sent
    to the backend.
    """
    payload = jwt.split(".")[1]
    padded = pad_to_multiple_of(4, "=", payload)
    decoded = b64decode(padded)
    return dict(json.loads(decoded))


def pad_to_multiple_of(n: int, pad: str, input: str) -> str:
    """
    It is assumed that pad is of length 1 and that n > 0.

    Notice that we want:
        len(input) + lenPadding % n == 0
    basic algbra then gives:
    """
    lenPadding = -len(input) % n

    return input + pad * lenPadding
