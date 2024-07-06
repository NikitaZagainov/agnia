def form_mail_message(action_result_data: dict) -> tuple:
    subject = action_result_data["subject"]
    time = action_result_data["time"]
    sender = action_result_data["sender"]
    body = action_result_data["body"]
    error_code = action_result_data["error_code"]

    if error_code == 1:
        return body, {"error_code": 1}
    message_dict = {
        "error_code": error_code,
    }

    message_str = (
        f"Sender: {sender}\n" f"Subject: {subject}\n" f"Time: {time}\n" f"Body:\n{body}"
    )
    return message_str, message_dict
