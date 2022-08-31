import json

from base64 import b64decode
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ExtractedData:
    access_token: str
    app_url: str
    device_id: UUID
    device_name: str
    project_id: UUID
    project_name: str


def extract_data_from_token(jwt: str) -> ExtractedData:
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
    device_access_token = extract_claims(jwt)["device_access_token"]
    app_url = extract_claims(device_access_token)["app_url"]
    device_id = extract_claims(device_access_token)["device_id"]
    device_name = extract_claims(device_access_token)["device_name"]
    project_id = extract_claims(device_access_token)["sub"]
    project_name = extract_claims(device_access_token)["project_name"]

    return ExtractedData(
        access_token=device_access_token,
        app_url=app_url,
        device_id=device_id,
        device_name=device_name,
        project_id=project_id,
        project_name=project_name,
    )


def extract_claims(jwt: str) -> dict:
    payload = jwt.split(".")[1]
    padded = pad_to_multiple_of(4, "=", payload)
    decoded = b64decode(padded)
    return json.loads(decoded)


def pad_to_multiple_of(n: int, pad: str, input: str) -> str:
    """
    It is assumed that pad is of length 1 and that n > 0.

    Notice that we want:
        len(input) + lenPadding % n == 0
    basic algbra then gives:
    """
    lenPadding = -len(input) % n

    return input + pad * lenPadding
