from pydantic import BaseModel


class TestInputParams(BaseModel):
    name: str


class TestOutputParams(BaseModel):
    name: str