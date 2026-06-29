from fastapi import APIRouter, UploadFile, File

from app.api.schemas import AnalyzeTextRequest, AnalyzeResponse, ModeInfo
from app.services.chat_service import ChatService

router = APIRouter()
service = ChatService()


@router.get("/modes", response_model=list[ModeInfo])
def get_modes():
    return service.get_modes()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_image(file: UploadFile = File(...)):
    image_bytes = file.file.read()
    modes, conversation = service.analyze_image(image_bytes)
    return AnalyzeResponse(modes=modes, conversation=conversation)


@router.post("/analyze/text", response_model=AnalyzeResponse)
def analyze_text(req: AnalyzeTextRequest):
    modes = service.analyze_text(req.context)
    return AnalyzeResponse(modes=modes, context=req.context)
