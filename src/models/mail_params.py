from pydantic import BaseModel
from typing import Optional

class MailInputParams(BaseModel):
    message: str

class MailOutputParams(BaseModel):
    subject: Optional[str]
    time: Optional[str]
    sender: Optional[str]
    body: Optional[str]
    error_code: int