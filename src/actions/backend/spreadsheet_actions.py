from src.actions.services.spreadsheet_service import SpreadSheetService
from src.models.spreadsheet_params import (
    SheetIdExtractorInputParams,
    SheetIdExtractorOutputParams,
    SheetQueryInputParams,
    SheetQueryOutputParams,
    SheetPostprocessingInputParams,
    SheetPostprocessingOutputParams,
)
from src.actions.registry import register_action
from src.actions.user_messages.spreadsheet_messages import form_extract_id_message, form_query_sheet_message
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


@register_action(
    SheetIdExtractorInputParams,
    SheetIdExtractorOutputParams,
    system_name=SYSTEM_NAME,
    action_name="extract_id",
    result_message_func=form_extract_id_message,
)
def extract_id(auth_data: dict, input_params: SheetIdExtractorInputParams) -> SheetIdExtractorOutputParams:
    doc_id = service.extract_id_from_message(input_params.message)
    return SheetIdExtractorOutputParams(doc_id=doc_id)


@register_action(
    SheetQueryInputParams,
    SheetQueryOutputParams,
    system_name=SYSTEM_NAME,
    action_name="query_sheet",
    result_message_func=form_query_sheet_message,
)
def query_sheet(auth_data: dict, input_params: SheetQueryInputParams) -> SheetQueryOutputParams:
    token = json.loads(auth_data[SYSTEM_NAME])
    service.authenticate(token)
    data_frame = service.extract_data_from_google_sheet(input_params.doc_id)
    print(data_frame)

@register_action(
    SheetPostprocessingInputParams,
    SheetPostprocessingOutputParams,
    system_name="GoogleSheets",
    action_name="postprocess_sheet",
    result_message_func=form_postprocess_sheet_message,
)
def postprocess_sheet(
    auth_data: dict, input_params: SheetPostprocessingInputParams
) -> SheetPostprocessingOutputParams:
    report = input_params.report
    message = input_params.message

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            lambda: asyncio.run(
                llm.get_response({"prompt": prompt.format(message, report)})
            )
        )
        response = future.result()

    return SheetPostprocessingOutputParams(report=response)
