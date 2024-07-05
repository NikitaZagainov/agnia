from pydantic_settings import BaseSettings


class TodoistAuthSettings(BaseSettings):
    todoist_oauth_api_url: str = "https://todoist.com/oauth/authorize/"
    todoist_token_exchange_api_url: str = "https://todoist.com/oauth/access_token/"
    todoist_redirect_url: str = "http://localhost:8845/get/token/todoist"
    todoist_scope: str = "task:add,data:read,data:read_write,data:delete,project:delete"
    todoist_state: str = "can_be_left_unchanged"
    # can be received by getting client_id and client_secret here
    todoist_client_id: str = ""
    todoist_client_secret: str = ""


class TeamSettings(BaseSettings):
    # no defaults are provided, so startup fails if settings are not specified
    team_id: str
    access_token: str


class EnpointsSettings(BaseSettings):
    llm_endpoint: str = "http://10.100.30.244:1322/llm/get_response"
    embedder_endpoint: str = "http://10.100.30.244:1322/embedder/get_response"
    save_auth_endpoint: str = "http://10.100.30.244:9200/save-authorization-data"
    socket_endpoint: str = "ws://10.100.30.244:8200/actions-ws"


team_auth_settings = TeamSettings()
todoist_auth_settings = TodoistAuthSettings()
endpoints_settings = EnpointsSettings()
