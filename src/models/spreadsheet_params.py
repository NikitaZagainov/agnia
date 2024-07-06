from pydantic import BaseModel
from typing import Optional


class SheetIdExtractorInputParams(BaseModel):
    message: str


class SheetIdExtractorOutputParams(BaseModel):
    doc_id: Optional[str]


class SheetQueryInputParams(BaseModel):
    doc_id: Optional[str]
    message: str


class SheetQueryOutputParams(BaseModel):
    report: str


class SheetPostprocessingInputParams(BaseModel):
    message: str
    report: str


class SheetPostprocessingOutputParams(BaseModel):
    report: str
