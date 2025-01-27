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
    """
    Extracts spreadsheet id from message.

    Args:
        auth_data (dict): Authorization data.
        input_params (SheetIdExtractorInputParams): Input parameters for the action.

    Returns:
        SheetIdExtractorOutputParams: Output parameters for the action.
    """
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
    """
    Performs SQL query on the sheet.

    Args:
        auth_data (dict): Authorization data.
        input_params (DownloadAndQuerySheetInputParams): Input parameters for the action.

    Returns:
        DownloadAndQuerySheetOutputParams: Output parameters for the action.
    """
    doc_id = input_params.doc_id
    if doc_id is None:
        return DownloadAndQuerySheetOutputParams(
            query_result="You did not provide link to document.", error_code=1
        )
    token = json.loads(auth_data[SYSTEM_NAME])
    user_query = input_params.user_query
    link = service.extract_urls(user_query)[0]
    if link == user_query.strip(" \n\t"):
        return DownloadAndQuerySheetOutputParams(
            query_result="You did not provide any query.", error_code=1
        )
    service.authenticate(token)
    try:
        data_frame = service.extract_data_from_google_sheet(input_params.doc_id)
    except Exception:
        return DownloadAndQuerySheetOutputParams(
            query_result="invalid link to doc", error_code=1
        )
    df_schema = service.infer_schema(data_frame)
    queries = service.generate_n_queries(
        input_params.user_query, data_frame, df_schema, 2
    )
    query_results = service.run_queries(data_frame, queries)
    query_results = "\n".join(
        ["{}. {}".format(i + 1, item) for i, item in enumerate(query_results)]
    )
    return DownloadAndQuerySheetOutputParams(query_result=query_results, error_code=0)


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
    """
    Postprocesses the sheet query result.

    Args:
        auth_data (dict): Authorization data.
        input_params (SheetPostprocessingInputParams): Input parameters for the action.

    Returns:
        SheetPostprocessingOutputParams: Output parameters for the action.
    """
    chosen_result = service.postprocess_result(
        input_params.user_query, input_params.query_result
    )

    return SheetPostprocessingOutputParams(report=chosen_result)
