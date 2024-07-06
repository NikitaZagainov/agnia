"""
API server for handling authorization with Google Sheets.

This server provides two endpoints:
- `/authorize/google-sheets`: returns the URL for authorization in Google Sheets.
- `/get/token/google-sheets`: takes the authorization code and state parameters and saves the authorization data.

"""

import uvicorn
from fastapi import FastAPI

from src.authorizations.google_sheets import GoogleSheetsAuthManager
from src.authorizations.utils import save_authorization_data

app = FastAPI()
google_sheets_manager = GoogleSheetsAuthManager()


@app.get("/authorize/google-sheets")
def authorize_in_google_sheets():
    """
    Returns the URL for authorization in Google Sheets.

    This endpoint starts the authorization flow in Google Sheets and returns the URL
    for the user to authorize the application.

    Returns:
        dict: The URL for authorization in Google Sheets.
    """
    return {"url": google_sheets_manager.authorize(return_url=True)}


@app.get("/get/token/google-sheets", include_in_schema=False)
def get_google_sheets_token(state: str, code: str, scope: str):
    """
    Saves the authorization data.

    This endpoint takes the authorization code and state parameters and saves the
    authorization data.

    Args:
        state (str): The state parameter obtained from the user after authorization.
        code (str): The authorization code obtained from the user after authorization.
        scope (str): The scope obtained from the user after authorization.

    Returns:
        dict: The saved authorization data.
    """
    authorization_data = google_sheets_manager.callback(code, state, scope)
    return save_authorization_data(authorization_data, "GoogleSheets")


if __name__ == "__main__":
    uvicorn.run(app, port=8845)
