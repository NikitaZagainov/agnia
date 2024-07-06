import json
import base64
import uuid

import requests
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from src.settings import todoist_auth_settings
from src.utils.base import strip_url


def authorize(user_id: uuid.UUID, return_url=False):
    try:
        todoist_oauth_api_url = todoist_auth_settings.todoist_oauth_api_url
        client_id = todoist_auth_settings.todoist_client_id
        scope = todoist_auth_settings.todoist_scope
        state = todoist_auth_settings.todoist_state

        custom_state = json.dumps({"state": state, "user_id": str(user_id)})
        encoded_state = base64.urlsafe_b64encode(custom_state.encode()).decode()

        authorization_url = (
            f"{strip_url(todoist_oauth_api_url)}?"
            f"client_id={client_id}&"
            f"scope={scope}&"
            f"state={encoded_state}"
        )
        if return_url:
            return authorization_url
        else:
            return RedirectResponse(url=authorization_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


def callback(code: str = None, state: str = None, error: str = None):
    if state != todoist_auth_settings.todoist_state:
        raise HTTPException(status_code=400, detail="State parameter mismatch")

    token_params = {
        "client_id": todoist_auth_settings.todoist_client_id,
        "client_secret": todoist_auth_settings.todoist_client_secret,
        "code": code,
        "redirect_uri": todoist_auth_settings.todoist_redirect_url,
    }
    try:
        response = requests.post(
            strip_url(todoist_auth_settings.todoist_token_exchange_api_url),
            data=token_params,
        )
        response.raise_for_status()
        response_data = response.json()

        return response_data["access_token"]
    except requests.HTTPError:
        error_data = response.json()
        # This could happen if the code is used more than once, or if it has expired.
        if error_data.get("error") == "bad_authorization_code":
            raise HTTPException(status_code=400, detail="Bad authorization code")
        # client_id or client_secret parameters are incorrect:
        elif error_data.get("error") == "incorrect_application_credentials":
            raise HTTPException(
                status_code=401, detail="Incorrect application credentials"
            )
        else:
            raise HTTPException(status_code=500, detail="Token exchange failed")
    except requests.RequestException as req_err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Todoist: {str(req_err)}",
        )
