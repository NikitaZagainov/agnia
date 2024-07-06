from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pandas.io.json._table_schema import build_table_schema
from src.settings import google_auth_settings
from src.external_services.llm import LLM
from pandasql import sqldf
from src.models.prompts import SQL_GENERATION_PROMPT, CONSOLIDATION_AND_REPORT_PROMPT
import re
import asyncio
from sqlite3 import connect, OperationalError


def convert_dtypes(col):
    col = col.str.strip()
    if col.dtype == "object":
        try:
            col_new = pd.to_numeric(col, errors='ignore')
            return col_new
        except:
            try:
                col_new = pd.to_datetime(col, errors='ignore')
                return col_new
            except:
                return col
    else:
        return col.dtype


class SpreadSheetService:
    def __init__(self):
        self._is_authenticated: bool = False
        self._llm = LLM()

    def extract_id_from_message(self, url):
        urls = self.extract_urls(url)
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
            cols = dataset["values"][0]
            data_frame = pd.DataFrame(dataset['values'][1:], columns=cols)
            data_frame.columns = [col.replace(
                " ", "_").strip() if col.strip() else f"col-{idx}" for idx, col in enumerate(data_frame.columns)]
            # Try to infer the data types of the columns
            data_frame = data_frame.apply(convert_dtypes)
            return data_frame

    def infer_schema(self, data_frame: pd.DataFrame) -> str:
        df_schema = build_table_schema(data_frame)
        del df_schema['pandas_version']
        return str(df_schema)

    def postprocess_result(self, user_query: str, extracted_data: str) -> str:
        prompt = "Generate an understandable report on this message: {}, given this result: {}. "
        "Construct your response as short as possible and do not mention links."
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: asyncio.run(
                self._llm.get_response({"prompt": prompt.format(user_query, extracted_data)})))
            return future.result()

    def query_table(self, df: pd.DataFrame, query: str) -> str:
        conn = connect(':memory:')
        df.to_sql(name='df', con=conn)
        query_res: pd.DataFrame = pd.read_sql(query, conn)
        return self.__df_to_str(query_res)

    def generate_n_queries(self, user_query: str, data_frame: pd.DataFrame, schema: str, n: int = 10) -> list[str]:
        example_data = self.__df_to_str(
            data_frame.head(min(data_frame.shape[0], 10)))
        prompt = f"""
        <|im_start|>system\n{SQL_GENERATION_PROMPT}<|im_end|>\n
        <|im_start|>user\n[Human Query]\n{user_query}\n[Data Schema]\n{schema}\n[Sample Data]{example_data}<|im_end|>\n
        <|im_start|>assistant\n
        """
        generated_queries: list[str] = []
        with ThreadPoolExecutor(max_workers=1) as executor:
            for i in range(n):
                future = executor.submit(
                    lambda: asyncio.run(
                        self._llm.get_response(
                            {"prompt": prompt, "temperature": i})
                    )
                )
                response = future.result()
                generated_queries.append(response)

        for idx, query in enumerate(generated_queries):
            try:
                sql_query: str = query.split(r"```sql")[1]
                sql_query = sql_query.split(r"```")[0]
                sql_query = sql_query.replace(r"\'", "''")
            except Exception:
                sql_query: str = query
            generated_queries[idx] = sql_query

        return generated_queries

    def run_queries(self, data_frame: pd.DataFrame, generated_queries: list[str]) -> list[str]:
        query_results = []
        for query in generated_queries:
            try:
                query_result = self.query_table(data_frame, query)
            except Exception as e:
                query_result = None
            query_results.append(query_result)
        return query_results

    def postprocess_result(self, user_query: str, results_list: str) -> str:
        prompt = f"""
        <|im_start|>system\n{CONSOLIDATION_AND_REPORT_PROMPT}<|im_end|>\n
        <|im_start|>user\n[Human Query]\n{user_query}\n[Results]\n{results_list}<|im_end|>\n
        <|im_start|>assistant\n
        """

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: asyncio.run(
                self._llm.get_response({"prompt": prompt})))
            return future.result()

    def __df_to_str(self, data_frame: pd.DataFrame) -> str:
        df_str = data_frame.to_csv(
            header=None, index=False).strip('\n').split('\n')
        df_str = '\n'.join(df_str)
        return df_str

    def extract_urls(self, text):
        url_pattern = r"(https?://[^\s]+)"
        urls = re.findall(url_pattern, text)
        return urls

    def __extract_document_id(self, url):
        pattern = r"/d/([^/]+)"
        match = re.search(pattern, url)
        if match:
            document_id = match.group(1)
            return document_id
        else:
            return None
