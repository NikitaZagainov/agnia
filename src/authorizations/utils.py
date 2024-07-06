import json

import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from src.settings import team_auth_settings, endpoints_settings


def save_authorization_data(authorization_data, system_name: str) -> JSONResponse:
    header = {"Authorization": f"Bearer {team_auth_settings.access_token}"}

    data = {
        "system_name": system_name,
        "authorization_data_json": json.dumps(authorization_data),
    }

    try:
        resp = requests.post(
            endpoints_settings.save_auth_endpoint, json=data, headers=header
        )
        resp.raise_for_status()

        if resp.status_code == 200:
            return JSONResponse(
                status_code=200,
                content={"message": "Authorization successful and data saved."},
            )
        elif resp.status_code == 201:
            return JSONResponse(
                status_code=201,
                content={"message": "Authorization successful and new data created."},
            )
        else:
            return JSONResponse(
                status_code=resp.status_code,
                content={"message": f"Unexpected response: {resp.status_code}"},
            )

    except requests.exceptions.HTTPError as e:
        if resp.status_code == 400:
            raise HTTPException(
                status_code=400, detail="Bad request to save authorization data"
            )
        elif resp.status_code == 401:
            raise HTTPException(
                status_code=401, detail="Unauthorized to save authorization data"
            )
        elif resp.status_code == 403:
            raise HTTPException(
                status_code=403, detail="Forbidden to save authorization data"
            )
        elif resp.status_code == 404:
            raise HTTPException(
                status_code=404, detail="Endpoint to save authorization data not found"
            )
        elif resp.status_code >= 500:
            raise HTTPException(
                status_code=502, detail="Server error while saving authorization data"
            )
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=500, detail="Error occurred while saving authorization data"
        )
