from src.actions.services.spreadsheet_service import SpreadSheetService
from src.actions.registry import register_action
from src.actions.user_messages.spreadsheet_messages import (
    form_extract_id_message,
    form_query_sheet_message,
    form_postprocess_sheet_message,
)
from src.models.spreadsheet_params import (
    SheetIdExtractorInputParams,
    SheetIdExtractorOutputParams,
    DownloadAndQuerySheetInputParams,
    DownloadAndQuerySheetOutputParams,
    SheetPostprocessingInputParams,
    SheetPostprocessingOutputParams,
)
import json

SYSTEM_NAME = "GoogleSheets"

service = SpreadSheetService()


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


@register_action(
    DownloadAndQuerySheetInputParams,
    DownloadAndQuerySheetOutputParams,
    system_name=SYSTEM_NAME,
    action_name="query_sheet",
    result_message_func=form_query_sheet_message,
)
def query_sheet(
    auth_data: dict, input_params: DownloadAndQuerySheetInputParams
) -> DownloadAndQuerySheetOutputParams:
    token = json.loads(auth_data[SYSTEM_NAME])
    service.authenticate(token)
    print("1"*50)
    data_frame = service.extract_data_from_google_sheet(input_params.doc_id)
    print("9"*50)
    df_schema = service.infer_schema(data_frame)
    query = service.generate_sql_query(input_params.user_query, data_frame, df_schema)
    query_result = service.query_table(data_frame, query)
    return DownloadAndQuerySheetOutputParams(query_result=query_result)


@register_action(
    SheetPostprocessingInputParams,
    SheetPostprocessingOutputParams,
    system_name=SYSTEM_NAME,
    action_name="postprocess_sheet",
    result_message_func=form_postprocess_sheet_message,
)
def postprocess_sheet(
    auth_data: dict, input_params: SheetPostprocessingInputParams
) -> SheetPostprocessingOutputParams:
    return SheetPostprocessingOutputParams(
        service.postprocess_results(input_params.message, input_params.report)
    )
