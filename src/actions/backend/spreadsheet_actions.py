from src.models.spreadsheet_params import SheetIdExtractorOutputParams, SheetIdExtractorInputParams
from src.actions.registry import register_action
from src.actions.user_messages.spreadsheet_messages import form_test_message
from src.actions.utils import extract_id_from_message


@register_action(
    SheetIdExtractorInputParams,
    SheetIdExtractorOutputParams,
    system_name="GoogleSheets",
    action_name="extract_id",
    result_message_func=form_test_message,
)
def extract_id(auth_data: dict, input_params: SheetIdExtractorInputParams) -> SheetIdExtractorOutputParams:
    doc_id = extract_id_from_message(input_params.message)

    return SheetIdExtractorOutputParams(doc_id=str(doc_id))
