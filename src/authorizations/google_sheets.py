from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from src.settings import google_auth_settings


class GoogleSheetsAuthManager:
    def __init__(self) -> None:
        config = {
            "web": {
                "client_id": google_auth_settings.client_id,
                "project_id": google_auth_settings.project_id,
                "auth_uri": google_auth_settings.auth_uri,
                "token_uri": google_auth_settings.token_uri,
                "auth_provider_x509_cert_url": google_auth_settings.auth_provider_x509_cert_url,
                "redirects_uris": google_auth_settings.redirect_uris,
                "client_secret": google_auth_settings.client_secret
            },
        }
        self.flow = InstalledAppFlow.from_client_config(
            config,
            scopes=google_auth_settings.scopes,
            redirect_uri=google_auth_settings.redirect_uris[0])

    def authorize(self, return_url=False):
        try:
            authorization_url = self.flow.authorization_url()[0]
            if return_url:
                return authorization_url
            else:
                return RedirectResponse(url=authorization_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

    def callback(self, code: str = None, state: str = None, error: str = None):
        try:
            self.flow.fetch_token(code=code)
            return self.flow.credentials.token
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            raise HTTPException(
                status_code=500, detail="Internal Server Error")
