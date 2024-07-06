def form_test_message(action_result_data: dict) -> tuple:
    doc_id = action_result_data["doc_id"]
    message_dict = {"doc_id": doc_id}
    if doc_id is None:
        message_str = "Failed to fetch document id"
    else:
        message_str = f"Document id: {doc_id}"
    return message_str, message_dict