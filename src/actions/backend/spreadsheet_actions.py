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
    doc_id = input_params.doc_id
    if doc_id is None:
        return DownloadAndQuerySheetOutputParams(
            query_result="You did not provide link to document.",
            error_code=1
        )
    token = json.loads(auth_data[SYSTEM_NAME])
    user_query = input_params.user_query
    link = service.extract_urls(user_query)[0]
    if link == user_query.strip(" \n\t"):
        return DownloadAndQuerySheetOutputParams(
            query_result="You did not provide any query.",
            error_code=1
        )
    service.authenticate(token)
    try:
        data_frame = service.extract_data_from_google_sheet(
            input_params.doc_id)
    except Exception as e:
        return DownloadAndQuerySheetOutputParams(query_result="invalid link to doc", error_code=1)
    df_schema = service.infer_schema(data_frame)
    queries = service.generate_n_queries(
        input_params.user_query, data_frame, df_schema, 2)
    query_results = service.run_queries(data_frame, queries)
    chosen_result = service.choose_result(
        input_params.user_query, query_results)
    return DownloadAndQuerySheetOutputParams(query_result=chosen_result, error_code=0)


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
    return SheetPostprocessingOutputParams(report=input_params.query_result)
    # if input_params.error_code == 1:
    #     return SheetPostprocessingOutputParams(
    #         report="Report is not generated due to the error from above."
    #     )
    # return SheetPostprocessingOutputParams(
    #     report=service.postprocess_result(
    #         input_params.user_query, input_params.query_result
    #     )
    # )
