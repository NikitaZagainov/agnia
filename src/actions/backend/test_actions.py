from src.models.test_params import TestInputParams, TestOutputParams
from src.actions.registry import register_action
from src.actions.user_messages.test_messages import form_test_message
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
def test_action(some_data: dict, input_params: TestInputParams) -> TestOutputParams:
    print("=" * 50)
    print(some_data)
    print("=" * 50)
    print(input_params)
    print("=" * 50)

    with ThreadPoolExecutor(max_workers=1) as executor:
        llm = LLM()
        future = executor.submit(lambda: asyncio.run(llm.get_response({"prompt": "test"})))
        response = future.result()
    print(response)

    return TestOutputParams(name=input_params.name)
