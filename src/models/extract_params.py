from pydantic import BaseModel


class ExtractInputParams(BaseModel):
    user_request: str


class ExtractOutputParams(BaseModel):
    answer: str
