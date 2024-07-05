def form_create_issue_result_message(action_result_data: dict) -> tuple:
    repo = action_result_data["repository"]["name"]
    issue_title = action_result_data["title"]
    issue_body = action_result_data["body"]

    message_dict = {
        "Issue repository": repo,
        "Issue title": issue_title,
        "Issue body": issue_body,
    }

    message_str = (
        f"The following GitFlame Issue was created:\n"
        f"Repository: {repo}\n"
        f"Issue title: {issue_title}\n"
        f"Issue body:\n{issue_body}"
    )

    return message_str, message_dict



