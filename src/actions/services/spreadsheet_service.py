from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
from src.settings import google_auth_settings
import re


class SpreadSheetService:
    _is_authenticated: bool = False

    def extract_id_from_message(self, url):
        urls = self.__extract_urls(url)
        ids = list(filter(lambda x: x is not None, [
            self.__extract_document_id(url) for url in urls]))

        if len(ids) == 1:
            return ids[0]
        return None

    def authenticate(self, token: dict) -> None:
        creds = Credentials.from_authorized_user_info(token)
        if not creds.valid and creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        self._access_service = build(google_auth_settings.api_service_name,
                                     google_auth_settings.api_version,
                                     credentials=creds)
        self._is_authenticated = True

    def extract_data_from_google_sheet(self, doc_id: str) -> pd.DataFrame:
        if not self._is_authenticated:
            raise Exception(
                'Service is not authenticated. User authenticate method first.')

        gsheets = self._access_service.spreadsheets().get(spreadsheetId=doc_id).execute()
        for sheet in gsheets['sheets']:
            if sheet['properties']['title'] == 'master':
                continue

            dataset = self._access_service.spreadsheets().values().get(
                spreadsheetId=doc_id,
                range=sheet['properties']['title'],
                majorDimension='ROWS').execute()
            df = pd.DataFrame(dataset['values'])
            df.columns = df.iloc[0]
            df.drop(df.index[0], inplace=True)
            return df

    def __extract_urls(self, text):
        url_pattern = r"(https?://[^\s]+)"
        urls = re.findall(url_pattern, text)
        return urls

    def __extract_document_id(self, url):
        pattern = r"/d/([^/]+)/"
        match = re.search(pattern, url)
        if match:
            document_id = match.group(1)
            return document_id
        else:
            return None
