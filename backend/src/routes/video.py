"""
Video generation routes module for AI DocVivid Service
"""

from fastapi import APIRouter, Depends, File, UploadFile, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from enum import Enum
from src.utils.logger import get_logger
from src.services.video_service import VideoService, VideoGenerationRequest
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import get_db
from src.models.task_modes import SUPPORTED_LANGUAGES, LANGUAGE_NAMES
from src.utils.dependencies import get_current_user_id
from src.utils.webpage import WebPageUtil

# Get logger for this module
logger = get_logger(__name__)

router = APIRouter()
video_service = VideoService()

class VoiceType(str, Enum):
    """Supported voice type enumeration"""
    ZEPHYR = "Zephyr"
    PUCK = "Puck"
    CHARON = "Charon"
    KORE = "Kore"
    FENRIR = "Fenrir"
    LEDA = "Leda"
    ORUS = "Orus"
    AOEDE = "Aoede"
    CALLIRRHOE = "Callirrhoe"
    AUTONOE = "Autonoe"
    ENCELADUS = "Enceladus"
    IAPETUS = "Iapetus"
    UMBRIEL = "Umbriel"
    ALGIEBA = "Algieba"
    DESPINA = "Despina"
    ERINOME = "Erinome"
    ALGENIB = "Algenib"
    RASALGETHI = "Rasalgethi"
    LAOMEDEIA = "Laomedeia"
    ACHERNAR = "Achernar"
    ALNILAM = "Alnilam"
    SCHEDAR = "Schedar"
    GACRUX = "Gacrux"
    PULCHERRIMA = "Pulcherrima"
    ACHIRD = "Achird"
    ZUBENELGENUBI = "Zubenelgenubi"
    VINDEMIATRIX = "Vindemiatrix"
    SADACHBIA = "Sadachbia"
    SADALTAGER = "Sadaltager"
    SULAFAT = "Sulafat"

@router.post("/generate")
async def generate_video(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    language: str = Form("en"),
    voice_type: VoiceType = Form(VoiceType.ACHERNAR),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate video (from text, file, or URL)
    
    Parameters:
        text: Text content
        file: Uploaded file
        url: URL link
        language: Target language (default: en)
        voice_type: Voice type (default: Achernar)
        
    Returns:
        task_id: Unique task identifier
    """
    logger.info(f"Received video generation request with language={language}, voice_type={voice_type.value}")
    
    # 验证语言是否支持
    if language not in SUPPORTED_LANGUAGES:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error", 
                "message": f"Unsupported language: {language}. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            }
        )
    
    if not any([text, file, url]):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "At least one of text, file, or url must be provided"}
        )
    
    # Create request object
    request = VideoGenerationRequest(
        text=text,
        file=file,
        url=url,
        language=language,
        voice_type=voice_type.value
    )
    
    # Submit task for async processing
    task_id = await video_service.submit_generation_task(request, db, user_id)
    
    return {
        "status": "success", 
        "data": {
            "task_id": task_id
        },
        "message": "Video generation task submitted successfully"
    }


@router.get("/tasks")
async def get_user_video_tasks(
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量（1-100）"),
    status: Optional[str] = Query(None, description="任务状态筛选（pending, processing, completed, failed）"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get video task list for current user
    
    Parameters:
        page: Page number (starting from 1, default: 1)
        page_size: Items per page (1-100, default: 10)
        status: Task status filter (optional: pending, processing, completed, failed)
        
    Returns:
        tasks: Task list
        pagination: Pagination information
    """
    logger.info(f"User {user_id} requesting tasks list: page={page}, page_size={page_size}, status={status}")
    
    # 获取任务列表
    result = await video_service.get_user_tasks(
        user_id=user_id,
        db=db,
        page=page,
        page_size=page_size,
        status=status
    )
    
    return {
        "status": "success",
        "data": result,
        "message": "Tasks retrieved successfully"
    }


@router.get("/url-preview")
async def url_preview(
    url: str
):
    """
    Get page metadata from URL (such as title, description, og:xxx, etc.)
    """

    if not url or not url.startswith(("http://", "https://")):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid or missing URL"}
        )
    metadata = await WebPageUtil.get_metadata(url)
    return {
        "status": "success",
        "data": {
            **metadata
        },
        "message": "Metadata extracted successfully"
    }