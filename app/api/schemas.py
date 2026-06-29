from pydantic import BaseModel


class ModeInfo(BaseModel):
    key: str
    icon: str
    label: str
    description: str


class AnalyzeTextRequest(BaseModel):
    context: str


class AnalyzeResponse(BaseModel):
    modes: dict[str, str]
    conversation: dict | None = None
    context: str | None = None
