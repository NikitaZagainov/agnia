import requests

from src.authorizations.exceptions import (
    UserAuthorizationError,
    ServerAuthorizationError,
    InvalidCredentialsError,
)
from src.utils.base import strip_url


def authorize_in_git_flame(username: str, password: str) -> dict:
    url = f"{strip_url('https://api.gitflame.ru/api/v1/')}/sign_in"
    try:
        resp = requests.post(url, json={"username": username, "password": password})
    except requests.ConnectionError:
        raise ServerAuthorizationError("GitFlame is currently unavailable")
    except requests.exceptions.RequestException:
        raise ServerAuthorizationError(
            "Unexpected error occurred when sending request to GitFlame"
        )

    try:
        response_data = resp.json()
    except requests.exceptions.JSONDecodeError:
        raise ServerAuthorizationError("Error in decoding response from GitFlame")

    if resp.status_code == 200:
        return response_data

    if resp.status_code == 404:
        raise InvalidCredentialsError("Provided GitFlame credentials are incorrect.")

    if resp.status_code == 422:
        raise UserAuthorizationError(
            f"One of the provided fields cannot be processed. Details: {response_data}"
        )

    if resp.status_code == 500:
        raise ServerAuthorizationError(
            f"Internal server error occurred in GitFlame. Details: {response_data}"
        )

    raise ServerAuthorizationError(
        f"Unexpected error occurred in GitFlame. Details: {response_data}"
    )
