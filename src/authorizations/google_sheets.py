from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import InstalledAppFlow
from src.settings import google_auth_settings


class GoogleSheetsAuthManager:
    """
    This class is responsible for managing the authorization process for Google Sheets API.

    Attributes:
        flow (google_auth_oauthlib.flow.InstalledAppFlow): An instance of the 
            `InstalledAppFlow` class from the `google_auth_oauthlib` library. It is used
            to perform the authorization flow.

    """
    def __init__(self) -> None:
        """
        Initializes the `GoogleSheetsAuthManager` class.

        This method creates an instance of the `InstalledAppFlow` class from the
        `google_auth_oauthlib` library. The `InstalledAppFlow` class is used to perform
        the authorization flow. The `InstalledAppFlow` instance is configured with the
        necessary client credentials and scopes to authorize the Google Sheets API.

        Returns:
            None
        """
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
        """
        Authorizes the application to access the Google Sheets API.

        This method is responsible for generating the authorization URL that the user
        needs to visit to authorize the application. The user is redirected to this
        URL, which initiates the authorization process. After the user authorizes the
        application, they are redirected back to the application with an authorization
        code. This method then exchanges the authorization code for credentials and
        returns them in JSON format.

        Args:
            return_url (bool, optional): If set to True, the authorization URL is
                returned as a string instead of being redirected to. Defaults to False.

        Returns:
            str or RedirectResponse: If `return_url` is True, the authorization URL is
                returned as a string. Otherwise, a `RedirectResponse` instance is returned
                which redirects the user to the authorization URL.

        Raises:
            HTTPException: If there is an error during the authorization process, an
                `HTTPException` is raised with the appropriate status code and detail
                message.
        """
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
        """
        Fetches the token from the authorization code and returns the credentials
        in JSON format.

        Args:
            code (str): The authorization code obtained from the user after
                authorization.
            state (str): The state parameter obtained from the user after
                authorization.
            error (str): The error parameter obtained from the user after
                authorization.

        Returns:
            str: The credentials in JSON format.

        Raises:
            HTTPException: If there is an error during the authorization process, an
                `HTTPException` is raised with the appropriate status code and detail
                message.
        """
        try:
            self.flow.fetch_token(code=code)
            return self.flow.credentials.to_json()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            raise HTTPException(
                status_code=500, detail="Internal Server Error")

