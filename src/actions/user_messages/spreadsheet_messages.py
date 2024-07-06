def form_extract_id_message(action_result_data: dict) -> tuple:
    doc_id = action_result_data["doc_id"]
    message_dict = {"doc_id": doc_id}
    if doc_id is None:
        message_str = "Failed to fetch document id"
    else:
        message_str = f"Document id: {doc_id}"
    return message_str, message_dict

def form_query_sheet_message(action_result_data: dict) -> tuple:
    report = action_result_data["report"]
    message_dict = {"report": report}
    message_str = f"Report: \n{report}"
    return message_str, message_dict

def form_postprocess_sheet_message(action_result_data: dict) -> tuple:
    report = action_result_data["report"]
    message_dict = {"report": report}
    message_str = f"Report: \n{report}"
    return message_str, message_dict