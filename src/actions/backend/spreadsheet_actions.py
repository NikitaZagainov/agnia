from src.actions.services.spreadsheet_service import SpreadSheetService

from src.actions.registry import register_action
from src.actions.user_messages.spreadsheet_messages import form_extract_id_message, form_query_sheet_message
from src.actions.utils import extract_id_from_message
from src.external_services.llm import LLM
from pandasql import sqldf, load_meat, load_births
from src.models.spreadsheet_params import (
    SheetIdExtractorInputParams,
    DownloadAndQuerySheetInputParams,
    DownloadAndQuerySheetOutputParams,
    SheetIdExtractorOutputParams,
    SheetQueryInputParams,
    SheetQueryOutputParams,
    SheetPostprocessingInputParams,
    SheetPostprocessingOutputParams,
)
from src.actions.registry import register_action
from src.actions.user_messages.spreadsheet_messages import (
    form_extract_id_message,
    form_query_sheet_message,
    form_postprocess_sheet_message,
)
from src.external_services.llm import LLM
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio

SYSTEM_NAME = "GoogleSheets"

service = SpreadSheetService()
llm = LLM()

prompt = (
    """Generate an understandable report on this message: {}, given this result: {}"""
)


import pandas as pd
from pandas.io.json._table_schema import build_table_schema
from concurrent.futures import ThreadPoolExecutor
import asyncio

@register_action(
    SheetIdExtractorInputParams,
    SheetIdExtractorOutputParams,
    system_name=SYSTEM_NAME,
    action_name="extract_id",
    result_message_func=form_extract_id_message,
)
def extract_id(
    auth_data: dict, input_params: SheetIdExtractorInputParams
) -> SheetIdExtractorOutputParams:
    doc_id = service.extract_id_from_message(input_params.message)
    return SheetIdExtractorOutputParams(doc_id=doc_id)


# @register_action(
# <<<<<<< query-table-and-generate-sql
#     DownloadAndQuerySheetInputParams,
#     DownloadAndQuerySheetOutputParams,
#     system_name="GoogleSheets",
#     action_name="download_and_query",
# )
# class DownloadAndQuerySheet:
#     def __df_to_str(self, df: pd.DataFrame) -> str:
#         df_str = df.head(10).to_csv(header=None, index=False).strip('\n').split('\n')
#         df_str = '\n'.join(df_str)
#         return df_str

#     def download_table(self, id: str) -> pd.DataFrame:
#         pass

#     def infer_schema(self, df: pd.DataFrame) -> str:
#         df_schema = build_table_schema(df)
#         del df_schema['pandas_version']
#         return df_schema
    
#     def generate_sql_query(self, user_query: str, df: pd.DataFrame, schema: str) -> str:
#         df_str = self.__df_to_str(df)

#         prompt: str = f"""
#         Give SQL query for the following -

#         Use only functions available in SQLite
#         Write apostroph as double quotes ''

#         Question:
#         {user_query}

#         Table Schema:  {schema}
#         Table Name : df

#         Some rows in the table looks like this:
#         {df_str}
#         """

#         with ThreadPoolExecutor(max_workers=1) as executor:
#             llm = LLM()
#             future = executor.submit(
#                 lambda: asyncio.run(
#                     llm.get_response({"prompt": prompt})
#                 )
#             )
#             response = future.result()
#         pass

#         sql_query: str = response.split(r"```sql")[1]
#         sql_query = sql_query.split(r"```")[0]
#         sql_query = sql_query.replace("'", '"')
#         return sql_query
    
#     def query_table(self, df: pd.DataFrame, query: str) -> str:
#         pysqldf = lambda q: sqldf(q, locals())
#         query_res: pd.DataFrame = pysqldf(query)
#         query_res_str = self.__df_to_str(query_res)
#         return query_res_str

#     async def execute(self, input_params: DownloadAndQuerySheetInputParams) -> DownloadAndQuerySheetOutputParams:
#         doc_id: str = input_params.doc_id
#         df: pd.DataFrame = self.download_table(doc_id)
#         df_schema: str = self.infer_schema(df)
#         query: str = self.generate_sql_query(input_params.message, df, df_schema)
#         query_result: str = self.query_table(df, query)
        
#         return DownloadAndQuerySheetOutputParams(query_result=query_result)
# =======
#     SheetQueryInputParams,
#     SheetQueryOutputParams,
#     system_name=SYSTEM_NAME,
#     action_name="query_sheet",
#     result_message_func=form_query_sheet_message,
# )
# def query_sheet(
#     auth_data: dict, input_params: SheetQueryInputParams
# ) -> SheetQueryOutputParams:
#     token = json.loads(auth_data[SYSTEM_NAME])
#     service.authenticate(token)
#     data_frame = service.extract_data_from_google_sheet(input_params.doc_id)
#     print(data_frame)


# @register_action(
#     SheetPostprocessingInputParams,
#     SheetPostprocessingOutputParams,
#     system_name="GoogleSheets",
#     action_name="postprocess_sheet",
#     result_message_func=form_postprocess_sheet_message,
# )
# def postprocess_sheet(
#     auth_data: dict, input_params: SheetPostprocessingInputParams
# ) -> SheetPostprocessingOutputParams:
#     report = input_params.report
#     message = input_params.message

#     with ThreadPoolExecutor(max_workers=1) as executor:
#         future = executor.submit(
#             lambda: asyncio.run(
#                 llm.get_response({"prompt": prompt.format(message, report)})
#             )
#         )
#         response = future.result()

#     return SheetPostprocessingOutputParams(report=response)
# >>>>>>> main
