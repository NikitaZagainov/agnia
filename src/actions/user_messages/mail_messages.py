def form_mail_message(action_result_data: dict) -> tuple:
    message_str = action_result_data["response"]
    if action_result_data["error_code"] == 1:
        message_str = "Error: \n" + message_str
        message_dict = {"error": message_str}
    else:
        message_str = "Message: \n" + message_str
        message_dict = {"message": message_str}
    return message_str, message_dict