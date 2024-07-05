from typing import List

from pydantic import BaseModel


class GitFlameOwner(BaseModel):
    id: int
    username: str
    login: str


class GetRepoInfoInputParams(BaseModel):
    owner: str
    repo: str


class GetRepoInfoOutputParams(BaseModel):
    id: int
    name: str
    description: str
    owner: GitFlameOwner
    stars_count: int


class CreateIssueInputParams(BaseModel):
    owner: str
    repo: str
    title: str
    body: str


class CreateIssueOutputParams(BaseModel):
    title: str
    url: str
    number: int
    created_at: str
    repository: dict
    body: list


class GetIssueInputParams(BaseModel):
    owner: str
    repo: str
    index: int


class GetIssueOutputParams(BaseModel):
    title: str
    created_at: str
    user: GitFlameOwner


class DeleteIssueInputParams(BaseModel):
    owner: str
    repo: str
    index: int


class DeleteIssueOutputParams(BaseModel):
    # no output params here
    pass


class EditIssueInputParams(BaseModel):
    owner: str
    repo: str
    index: int
    title: str
    body: str


class EditIssueOutputParams(BaseModel):
    updated_at: str


class GetRepoIssuesInputParams(BaseModel):
    owner: str
    repo: str


class GetRepoIssuesOutputParams(BaseModel):
    issues: List[GetIssueOutputParams]
