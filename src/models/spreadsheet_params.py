from pydantic import BaseModel


class SheetIdExtractorInputParams(BaseModel):
    message: str


class SheetIdExtractorOutputParams(BaseModel):
    doc_id: str