from pydantic import BaseModel
from typing import Dict


class ExtractInputParams(BaseModel):
    user_request: str


class ExtractOutputParams(BaseModel):
    answer: str
