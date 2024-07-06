def form_test_message(action_result_data: dict) -> tuple:
    print(action_result_data)
    message_dict = {
        "Test name": action_result_data["name"],
    }

    message_str = (
        f"The following Test was created:\n"
        f"Test name: {action_result_data['name']}"
    )
    return message_str, message_dict