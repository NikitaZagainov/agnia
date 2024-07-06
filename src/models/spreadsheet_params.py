from pydantic import BaseModel
from typing import Optional


class SheetIdExtractorInputParams(BaseModel):
    message: str


class SheetIdExtractorOutputParams(BaseModel):
    doc_id: Optional[str]


class DownloadAndQuerySheetInputParams(BaseModel):
    doc_id: Optional[str]
    user_query: str


class DownloadAndQuerySheetOutputParams(BaseModel):
    query_result: str


class SheetPostprocessingInputParams(BaseModel):
    user_query: str
    query_result: str


class SheetPostprocessingOutputParams(BaseModel):
    report: str
