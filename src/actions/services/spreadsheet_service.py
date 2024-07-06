from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pandas.io.json._table_schema import build_table_schema
from src.settings import google_auth_settings
from src.external_services.llm import LLM
from src.models.prompts import SQL_GENERATION_PROMPT, CONSOLIDATION_AND_REPORT_PROMPT
import re
import asyncio
from sqlite3 import connect


def convert_dtypes(col):
    """
    Convert column data types to appropriate types.

    Args:
        col (pandas.Series): Column to convert.

    Returns:
        pandas.Series: Column with converted data types.
    """
    col = col.str.strip()
    if col.dtype == "object":
        try:
            col_new = pd.to_numeric(col, errors="ignore")
            return col_new
        except Exception:
            try:
                col_new = pd.to_datetime(col, errors="ignore")
                return col_new
            except Exception:
                return col
    else:
        return col.dtype


class SpreadSheetService:
    """
    Service for interacting with Google Sheets.

    This service provides methods for extracting document IDs from URLs,
    authenticating with Google Sheets, and executing SQL queries.
    """

    def __init__(self):
        """
        Initialize SpreadSheetService.

        This method initializes the service by setting the authentication
        status to False and creating an instance of the LLM class.
        """
        self._is_authenticated: bool = False
        self._llm = LLM()

    def extract_id_from_message(self, url):
        """
        Extract document ID from URL.

        Args:
            url (str): URL to extract document ID from.

        Returns:
            str or None: Document ID if found, None otherwise.
        """
        urls = self.extract_urls(url)
        ids = list(
            filter(
                lambda x: x is not None,
                [self.__extract_document_id(url) for url in urls],
            )
        )

        if len(ids) == 1:
            return ids[0]
        return None

    def authenticate(self, token: dict) -> None:
        """
        Authenticates the service with the provided token.

        Args:
            token (dict): Authorized user information containing credentials.

        Raises:
            Exception: If the service is not authenticated.

        Returns:
            None
        """
        creds = Credentials.from_authorized_user_info(token)
        if not creds.valid and creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        self._access_service = build(
            google_auth_settings.api_service_name,
            google_auth_settings.api_version,
            credentials=creds,
        )
        self._is_authenticated = True

    def extract_data_from_google_sheet(self, doc_id: str) -> pd.DataFrame:
        """
        Extracts data from a Google Sheet using the provided document ID.

        Args:
            doc_id (str): The ID of the Google Sheet.

        Raises:
            Exception: If the service is not authenticated.

        Returns:
            pd.DataFrame: The extracted data from the Google Sheet.
        """
        if not self._is_authenticated:
            raise Exception(
                "Service is not authenticated. User authenticate method first."
            )

        gsheets = (
            self._access_service.spreadsheets().get(spreadsheetId=doc_id).execute()
        )

        for sheet in gsheets["sheets"]:
            if sheet["properties"]["title"] == "master":
                continue
            dataset = (
                self._access_service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=doc_id,
                    range=sheet["properties"]["title"],
                    majorDimension="ROWS",
                )
                .execute()
            )
            cols = dataset["values"][0]
            data_frame = pd.DataFrame(dataset["values"][1:], columns=cols)
            data_frame.columns = [
                col.replace(" ", "_").strip() if col.strip() else f"col-{idx}"
                for idx, col in enumerate(data_frame.columns)
            ]
            # Try to infer the data types of the columns
            data_frame = data_frame.apply(convert_dtypes)
            return data_frame

    def infer_schema(self, data_frame: pd.DataFrame) -> str:
        """
        Infer the schema of a given DataFrame.

        Args:
            data_frame (pd.DataFrame): The DataFrame to infer the schema from.

        Returns:
            str: The inferred schema of the DataFrame as a string representation.
        """
        df_schema = build_table_schema(data_frame)
        del df_schema["pandas_version"]
        return str(df_schema)

    def query_table(self, df: pd.DataFrame, query: str) -> str:
        """
        Execute a SQL query on a given DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to execute the query on.
            query (str): The SQL query to execute.

        Returns:
            str: The result of the query as a string representation.
        """
        conn = connect(":memory:")
        df.to_sql(name="df", con=conn)
        query_res: pd.DataFrame = pd.read_sql(query, conn)
        return self.__df_to_str(query_res)

    def generate_n_queries(
        self, user_query: str, data_frame: pd.DataFrame, schema: str, n: int = 10
    ) -> list[str]:
        """
        Generate a list of SQL queries by executing a LLm model.

        Args:
            user_query (str): The human query to generate SQL queries for.
            data_frame (pd.DataFrame): The DataFrame to generate queries on.
            schema (str): The schema of the DataFrame.
            n (int): The number of queries to generate (default: 10).

        Returns:
            list[str]: A list of SQL queries generated by the LLm model.
        """
        example_data = self.__df_to_str(data_frame.head(min(data_frame.shape[0], 10)))
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
                        self._llm.get_response({"prompt": prompt, "temperature": i})
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

    def run_queries(
        self, data_frame: pd.DataFrame, generated_queries: list[str]
    ) -> list[str]:
        """
        Run SQL queries on a given DataFrame and return the results.

        Args:
            data_frame (pd.DataFrame): The DataFrame to run queries on.
            generated_queries (list[str]): The SQL queries to run.

        Returns:
            list[str]: The results of the queries.
        """
        query_results = []
        for query in generated_queries:
            try:
                query_result = self.query_table(data_frame, query)
            except Exception:
                query_result = None
            query_results.append(query_result)
        return query_results

    def postprocess_result(self, user_query: str, results_list: str) -> str:
        """
        Post-process the results of a query and generate a report.

        Args:
            user_query (str): The human query to generate a report for.
            results_list (str): The results of the queries.

        Returns:
            str: The generated report.
        """
        prompt = f"""
        <|im_start|>system\n{CONSOLIDATION_AND_REPORT_PROMPT}<|im_end|>\n
        <|im_start|>user\n[Human Query]\n{user_query}\n[Results]\n{results_list}<|im_end|>\n
        <|im_start|>assistant\n
        """

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                lambda: asyncio.run(self._llm.get_response({"prompt": prompt}))
            )
            return future.result()

    def __df_to_str(self, data_frame: pd.DataFrame) -> str:
        """
        Convert a pandas DataFrame to a string.

        Args:
            data_frame (pd.DataFrame): The DataFrame to convert.

        Returns:
            str: The DataFrame as a string.
        """
        df_str = data_frame.to_csv(header=None, index=False).strip("\n").split("\n")
        df_str = "\n".join(df_str)
        return df_str

    def extract_urls(self, text):
        """
        Extract URLs from a string.

        Args:
            text (str): The string to extract URLs from.

        Returns:
            list[str]: The extracted URLs.
        """
        url_pattern = r"(https?://[^\s]+)"
        urls = re.findall(url_pattern, text)
        return urls

    def __extract_document_id(self, url):
        """
        Extract the document ID from a URL.

        Args:
            url (str): The URL to extract the document ID from.

        Returns:
            Optional[str]: The document ID, or None if not found.
        """
        pattern = r"/d/([^/]+)"
        match = re.search(pattern, url)
        if match:
            document_id = match.group(1)
            return document_id
        else:
            return None
