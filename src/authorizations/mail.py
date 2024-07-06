from pydantic import BaseModel

class MailCredentials(BaseModel):
    username: str
    password: str