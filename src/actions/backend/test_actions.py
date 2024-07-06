from src.models.test_params import TestInputParams, TestOutputParams
from src.actions.registry import register_action
from src.actions.user_messages.test_messages import form_test_message
from src.actions.utils import extract_id_from_message
from src.external_services.llm import LLM
import asyncio
from concurrent.futures import ThreadPoolExecutor


@register_action(
    TestInputParams,
    TestOutputParams,
    system_name="Test",
    action_name="test_action",
    result_message_func=form_test_message,
)
def test_action(auth_data: dict, input_params: TestInputParams) -> TestOutputParams:
    doc_id = extract_id_from_message(input_params.name)

    return TestOutputParams(name=doc_id)
