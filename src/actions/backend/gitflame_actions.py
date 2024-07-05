import json

import requests

from src.utils.base import strip_url, ActionException
from src.models.gitflame_params import *
from src.actions.registry import register_action
from src.actions.user_messages.gitflame_messages import *

system_name = "GitFlame"
api_url = "https://api.gitflame.ru/api/v1"
api_version = "1"


def _get_headers(authorization_data: dict[str, str]) -> dict:
    return {"Authorization": f'Bearer {authorization_data["GitFlame"]}'}


@register_action(GetRepoInfoInputParams, GetRepoInfoOutputParams, system_name="GitFlame", action_name="Get repo information")
def get_repo_info(authorization_data: dict, input_data: GetRepoInfoInputParams) -> GetRepoInfoOutputParams:
    
    headers = _get_headers(authorization_data)
    url = f"{strip_url(api_url)}/repos/{input_data.owner}/{input_data.repo}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise ActionException(
            f"Failed to get repo information. Status Code: {response.status_code}. Details: {response.text}")
    
    response = json.loads(response.text)

    owner_fields = {
        "id": response["owner"]["id"],
        "username": response["owner"]["username"],
        "login": response["owner"]["login"],
    }
    output_fields = {
        "id": response["id"],
        "name": response["name"],
        "description": response["description"],
        "owner": GitFlameOwner(**owner_fields),
        "stars_count": response["stars_count"]
    }
    return GetRepoInfoOutputParams(**output_fields)


@register_action(CreateIssueInputParams, CreateIssueOutputParams,
                 system_name="GitFlame", action_name="Create issue", result_message_func=form_create_issue_result_message)
def create_issue(authorization_data: dict, input_data: CreateIssueInputParams):
    headers = _get_headers(authorization_data)

    # add params where "disposition" == "body"
    body_params = {
        "title": input_data.title,
        "body": input_data.body
    }

    url = f"{strip_url(api_url)}/repos/{input_data.owner}/{input_data.repo}/issues"

    response = requests.post(url, headers=headers, json=body_params)

    if response.status_code != 201:
        raise ActionException(f"Failed to create issue. Status Code: {response.status_code}. Details: {response.text}")
    
    response = json.loads(response.text)
    
    output_fields = {
        "title": response["title"],
        "url": response["url"],
        "number": response["number"],
        "created_at": response["created_at"],
        "repository": response["repository"],
        "body": response["body"],
    }

    return CreateIssueOutputParams(**output_fields)


@register_action(GetIssueInputParams, GetIssueOutputParams,
                 system_name="GitFlame", action_name="Get issue")
def get_issue(authorization_data: dict, input_data: GetIssueInputParams):
    headers = _get_headers(authorization_data)
    url = f"{strip_url(api_url)}/repos/{input_data.owner}/{input_data.repo}/issues/{input_data.index}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ActionException(f"Failed to get issue. Status Code: {response.status_code}. Details: {response.text}")

    response = json.loads(response.text)

    user_output = {
        "id": response["user"]["id"],
        "username": response["user"]["username"],
        "login": response["user"]["login"]
    }

    output = {
        "title": response["title"],
        "created_at": response["created_at"],
        "user": GitFlameOwner(**user_output)
    }

    return GetIssueOutputParams(**output)


@register_action(
    DeleteIssueInputParams, DeleteIssueOutputParams,
    system_name="GitFlame", action_name="Delete issue"
)
def delete_issue(authorization_data: dict, input_data: DeleteIssueInputParams):
    headers = _get_headers(authorization_data)
    url = f"{strip_url(api_url)}/repos/{input_data.owner}/{input_data.repo}/issues/{input_data.index}"

    response = requests.delete(url, headers=headers)

    if response.status_code != 204:
        raise ActionException(f"Failed to delete issue. Status Code: {response.status_code}. Details: {response.text}")

    return DeleteIssueOutputParams()


@register_action(EditIssueInputParams, EditIssueOutputParams,
                 system_name="GitFlame", action_name="Edit issue")
def edit_issue(authorization_data: dict, input_data: EditIssueInputParams):
    headers = _get_headers(authorization_data)

    # add params where "disposition" == "body"
    body_params = {
        "title": input_data.title,
        "body": input_data.body
    }

    url = f"{strip_url(api_url)}/repos/{input_data.owner}/{input_data.repo}/issues/{input_data.index}"

    response = requests.patch(url, headers=headers, json=body_params)

    if response.status_code != 201:
        raise ActionException(f"Failed to edit issue. Status Code: {response.status_code}. Details: {response.text}")
    
    response = json.loads(response.text)

    output = {
        "updated_at": response["updated_at"]
    }

    return EditIssueOutputParams(**output)


@register_action(GetRepoIssuesInputParams, GetRepoIssuesOutputParams,
                 system_name="GitFlame", action_name="Get repo issues")
def get_repo_issues(authorization_data: dict, input_data: GetRepoIssuesInputParams):
    headers = _get_headers(authorization_data)

    # add params where "disposition" == "query"
    query_params = {
    }

    url = f"{strip_url(api_url)}/repos/{input_data.owner}/{input_data.repo}/issues"

    response = requests.get(url, headers=headers, params=query_params)

    if response.status_code != 200:
        raise ActionException(f"Failed to get issues. Status Code: {response.status_code}. Details: {response.text}")
    
    response = json.loads(response.text)
    
    output = list()
    for issue in response:
        user_output = {
            "id": issue["user"]["id"],
            "username": issue["user"]["username"],
            "login": issue["user"]["login"],
        }

        issue_output = {
            "title": issue["title"],
            "created_at": issue["created_at"],
            "user": GitFlameOwner(**user_output)
        }

        output.append(
            GetIssueOutputParams(**issue_output)
        )

    return GetRepoIssuesOutputParams(issues=output)
