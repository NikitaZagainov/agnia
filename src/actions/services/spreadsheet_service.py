from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pandas.io.json._table_schema import build_table_schema
from src.settings import google_auth_settings
from src.external_services.llm import LLM
from pandasql import sqldf
import re
import asyncio
from sqlite3 import connect


class SpreadSheetService:
    def __init__(self):
        self._is_authenticated: bool = False
        self._llm = LLM()

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
            data_frame = pd.DataFrame(dataset['values'])
            data_frame.columns = data_frame.iloc[0]
            data_frame.drop(data_frame.index[0], inplace=True)
            data_frame.columns = [col.replace(" ", "_") for col in data_frame.columns]
            return data_frame

    def infer_schema(self, data_frame: pd.DataFrame) -> str:
        df_schema = build_table_schema(data_frame)
        del df_schema['pandas_version']
        return df_schema

    def generate_sql_query(self, user_query: str, data_frame: pd.DataFrame, schema: str) -> str:
        example_data = self.__df_to_str(
            data_frame.head(min(data_frame.shape[0], 10)))
        prompt: str = f"""
        Give SQL query for the following -

        Use only functions available in SQLite
        Write apostroph as double quotes ''

        Question:
        {user_query}

        Table Schema:  {schema}
        Table Name : df

        Some rows in the table looks like this:
        {example_data}
        """

        with ThreadPoolExecutor(max_workers=1) as executor:

            future = executor.submit(
                lambda: asyncio.run(
                    self._llm.get_response({"prompt": prompt})
                )
            )
            response = future.result()

        sql_query: str = response.split(r"```sql")[1]
        sql_query = sql_query.split(r"```")[0]
        sql_query = sql_query.replace(r"\'", "''")
        return sql_query

    def postprocess_result(self, user_query: str, extracted_data: str) -> str:
        prompt = "Generate an understandable report on this message: {}, given this result: {}"
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: asyncio.run(
                self.llm.get_response({"prompt": prompt.format(user_query, extracted_data)})))
            return future.result()

    def query_table(self, df: pd.DataFrame, query: str) -> str:
        conn = connect(':memory:')
        df.to_sql(name='df', con=conn)
        query_res: pd.DataFrame = pd.read_sql(query, conn)
        return self.__df_to_str(query_res)

    def __df_to_str(self, data_frame: pd.DataFrame) -> str:
        df_str = data_frame.to_csv(
            header=None, index=False).strip('\n').split('\n')
        df_str = '\n'.join(df_str)
        return df_str

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
