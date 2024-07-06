
import uvicorn
from fastapi import HTTPException, FastAPI

from src.authorizations.google_sheets import GoogleSheetsAuthManager
from src.authorizations.utils import save_authorization_data

app = FastAPI()
google_sheets_manager = GoogleSheetsAuthManager()


@app.get("/authorize/google-sheets")
def authorize_in_google_sheets():

    return {"url": google_sheets_manager.authorize(return_url=True)}


@app.get("/get/token/google-sheets", include_in_schema=False)
def get_google_sheets_token(state: str, code: str, scope: str):
    authorization_data = google_sheets_manager.callback(code, state, scope)
    return save_authorization_data(authorization_data, "GoogleSheets")


if __name__ == "__main__":
    uvicorn.run(app, port=8845)
