from src.models.spreadsheet_params import (
    SheetIdExtractorOutputParams,
    SheetIdExtractorInputParams,
    SheetQueryInputParams,
    SheetQueryOutputParams,
)
from src.actions.registry import register_action
from src.actions.user_messages.spreadsheet_messages import form_extract_id_message, form_query_sheet_message
from src.actions.utils import extract_id_from_message


@register_action(
    SheetIdExtractorInputParams,
    SheetIdExtractorOutputParams,
    system_name="GoogleSheets",
    action_name="extract_id",
    result_message_func=form_extract_id_message,
)
def extract_id(
    auth_data: dict, input_params: SheetIdExtractorInputParams
) -> SheetIdExtractorOutputParams:
    doc_id = extract_id_from_message(input_params.message)

    return SheetIdExtractorOutputParams(doc_id=doc_id)

@register_action(
    SheetQueryInputParams,
    SheetQueryOutputParams,
    system_name="GoogleSheets",
    action_name="query_sheet",
    result_message_func=form_query_sheet_message,
)
def query_sheet(
    auth_data: dict, input_params: SheetQueryInputParams
) -> SheetQueryOutputParams:
    return SheetQueryOutputParams(report="Чувак, ты думал здесь что-то будет? нет")
