import json
import asyncio
from enum import Enum

from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedOK

from src.settings import team_auth_settings, endpoints_settings
from src.router import execute_action, form_result_message

import importlib

importlib.import_module(".extract", package="src.actions.ai")
importlib.import_module(".gitflame_actions", package="src.actions.backend")
importlib.import_module(".test_actions", package="src.actions.backend")

class ResultStatusEnum(Enum):
    SUCCESS = "Success"
    FAIL = "Fail"


with connect(
    f"{endpoints_settings.socket_endpoint}/{team_auth_settings.team_id}"
) as socket:
    print("Socket opened, waiting for messages...")
    try:
        while True:
            data_json = socket.recv()
            data = json.loads(data_json)
            if "error" in data:
                # Possible Error Cases
                # -   Returning not all fields of the required fields to socket
                # -   Returning invalid json
                print(data)
            else:
                print(f"Message from socket: {data}")
                request_id = data["request_id"]
                system_name = data["system_name"]
                action_name = data["action_name"]
                error_message = None
                execution_result = None
                messages = dict()

                try:
                    execution_result = asyncio.run(
                        execute_action(
                            system_name,
                            action_name,
                            data["input_data"],
                            data["system_authorization_data"],
                        )
                    )
                    status = ResultStatusEnum.SUCCESS.value
                    messages = form_result_message(
                        data["system_name"], data["action_name"], execution_result
                    )
                except Exception as e:
                    print("Error occurred: ", e)
                    status = ResultStatusEnum.FAIL.value
                    error_message = (
                        f"Action (system '{system_name}', action '{action_name}') failed "
                        f"due to the error: {e}"
                    )

                action_results = {
                    "request_id": request_id,
                    "status": status,
                }

                action_results.update(messages)
                # adding action results, so they can be used in other actions
                if execution_result is not None:
                    action_results["result"] = execution_result

                # adding error message that will be shown in telegram
                if error_message is not None:
                    action_results["error_message"] = error_message

                action_results_json = json.dumps(action_results)
                print(f"Results sent to action requestor: {action_results}")
                socket.send(action_results_json)

    except ConnectionClosedOK:
        print("Socket was closed")
