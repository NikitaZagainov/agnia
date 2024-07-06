from pydantic import BaseModel
from typing import Optional


class SheetIdExtractorInputParams(BaseModel):
    message: str


class SheetIdExtractorOutputParams(BaseModel):
    doc_id: Optional[str]