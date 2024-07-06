import base64
import json

import requests
import uvicorn
from fastapi import HTTPException, FastAPI
from pydantic import BaseModel

from src.authorizations import todoist
from src.authorizations.git_flame import authorize_in_git_flame
from src.authorizations.utils import save_authorization_data
from src.authorizations.exceptions import (
    UserAuthorizationError,
    ServerAuthorizationError,
    InvalidCredentialsError,
)
from src.settings import team_auth_settings

app = FastAPI()


class GitFlameCredentials(BaseModel):
    username: str
    password: str


@app.get("/authorize/todoist")
def authorize_in_todoist():
    return {"url": todoist.authorize(team_auth_settings.team_id, return_url=True)}


@app.get("/get/token/todoist", include_in_schema=False)
def get_todoist_token(
    code: str = None,
    state: str = None,
    error: str = None,
):
    if error == "invalid_application_status":
        raise HTTPException(status_code=500, detail="Invalid application status")
    elif error == "invalid_scope":
        raise HTTPException(status_code=400, detail="Invalid scope")
    elif error == "access_denied":
        raise HTTPException(status_code=403, detail="User denied authorization")

    try:
        decoded_state = base64.urlsafe_b64decode(state.encode()).decode()
        state_data = json.loads(decoded_state)
        # user_id = state_data["user_id"]
        orginal_state = state_data["state"]
    except ValueError:
        raise HTTPException(status_code=400, detail="State parameter mismatch")

    authorization_data = todoist.callback(code, orginal_state, error)
    return save_authorization_data(authorization_data, "GitFlame")


@app.post("/authorize/git-flame")
async def authorize_in_git_flame_and_send(credentials: GitFlameCredentials):
    try:
        authorization_data = authorize_in_git_flame(
            credentials.username, credentials.password
        )

    except requests.ConnectionError:
        raise HTTPException(status_code=503, detail="GitFlame is currently unavailable")
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred when sending request to GitFlame",
        )
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Error in decoding response from GitFlame"
        )
    except ServerAuthorizationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except (InvalidCredentialsError, UserAuthorizationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return save_authorization_data(authorization_data, "GitFlame")


if __name__ == "__main__":
    uvicorn.run(app, port=8845)
