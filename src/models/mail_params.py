from pydantic import BaseModel

class MailInputParams(BaseModel):
    message: str

class MailOutputParams(BaseModel):
    response: str
    error_code: int