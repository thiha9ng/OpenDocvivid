"""
Video generation service module for AI DocVivid Service
"""

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List
from fastapi import UploadFile
from google import genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.configs.config import settings
from src.utils.logger import get_logger
from src.utils.storage import storage_service
from src.utils.file_loader import FileExtractor
from src.tasks.generate_tasks import video_task
from src.models.task_modes import VideoGenerateTask, TaskStatus as DBTaskStatus
from celery.result import AsyncResult

from src.utils.webpage import WebPageUtil
from src.utils.exceptions import (
    URLAccessException,
    FileProcessingException,
    StorageException,
    BadRequestException,
    TokenLimitExceededException,
    InsufficientCreditException
)
from src.services.credit_service import CreditService

# Get logger for this module
logger = get_logger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VideoGenerationRequest:
    """
    Data class for video generation request parameters
    """
    text: Optional[str] = None
    file: Optional[UploadFile] = None
    url: Optional[str] = None
    language: str = "english"
    voice_type: str = "mike"


class VideoService:
    """
    Service for handling video generation tasks using Celery
    """

    def __init__(self):
        logger.info("VideoService initialized")

    async def submit_generation_task(self, request: VideoGenerationRequest, db: AsyncSession, user_id: str) -> str:
        """
        Submit a new video generation task using Celery

        Args:
            request: The video generation request parameters
            db: Database session
            user_id: User ID from token

        Returns:
            task_id: Unique identifier for the task
        """
        # 检查用户积分是否充足（最低30积分）

        user_uuid = uuid.UUID(user_id)
        # 检查积分是否满足最低要求
        is_sufficient = await CreditService.check_credit_sufficient(
            db=db,
            user_id=user_uuid,
            required_credit=CreditService.MIN_CREDIT_FOR_TASK
        )

        # 如果积分不足，抛出异常
        if not is_sufficient:
            logger.warning(
                f"User {user_id} has insufficient credit (< {CreditService.MIN_CREDIT_FOR_TASK})")
            raise InsufficientCreditException(
                f"Insufficient credit balance. You need at least {CreditService.MIN_CREDIT_FOR_TASK} credits to create a task. Please purchase more credits to continue."
            )

        task_id = str(uuid.uuid4())

        # 判断优先级：文件 > url > text
        input_type = None
        original_text = None
        source_url = None
        input_file_url = None

        if request.file:
            # 优先级最高：文件
            input_type = "file"
            logger.info(f"Processing file input: {request.file.filename}")

            # 读取文件内容并提取文本
            try:
                file_content = await request.file.read()

                # 判断文件类型并提取内容
                filename = request.file.filename.lower()
                if filename.endswith('.docx'):
                    original_text = FileExtractor.parse_docx_bytes(
                        file_content)
                elif filename.endswith('.pdf'):
                    original_text = FileExtractor.parse_pdf_bytes(file_content)
                elif filename.endswith(('.txt', '.md', '.text')):
                    original_text = FileExtractor.parse_text_bytes(
                        file_content)
                else:
                    logger.error(
                        f"Unsupported file type: {request.file.filename}")
                    raise FileProcessingException(
                        f"Unsupported file type: {request.file.filename}. Supported types: .docx, .pdf, .txt, .md, .text")

                logger.info(
                    f"Extracted text length: {len(original_text) if original_text else 0}")

                # 重置文件指针以便上传
                await request.file.seek(0)

            except ValueError as e:
                # 文件类型错误
                logger.error(f"Unsupported file type: {e}")
                raise FileProcessingException(
                    f"Unsupported file type: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to extract content from file: {e}")
                raise FileProcessingException(
                    f"Failed to extract content from file: {str(e)}")

            # 上传文件到 Google Cloud Storage
            destination_path = f"inputs/{task_id}/{request.file.filename}"
            try:
                input_file_url = await storage_service.upload_file(request.file, destination_path)
                logger.info(f"File uploaded to GCS: {input_file_url}")
            except Exception as e:
                logger.error(f"Failed to upload file: {e}")
                raise StorageException(
                    f"Failed to upload file to storage: {str(e)}")

        elif request.url:
            # 优先级第二：URL
            input_type = "url"
            source_url = request.url
            logger.info(f"Processing URL input: {source_url}")
            try:
                original_text = await WebPageUtil.get_content(source_url)
            except Exception as e:
                logger.error(f"Failed to extract content from URL: {e}")
                raise URLAccessException(f"Failed to access the provided URL")

        elif request.text:
            # 优先级最低：文本
            input_type = "text"
            original_text = request.text
            logger.info(
                f"Processing text input (length: {len(original_text)})")
        else:
            raise BadRequestException(
                "At least one of file, url, or text must be provided")

        # 校验文本长度,计算token是否超过1,048,576
        if original_text:
            try:
                client = genai.Client(api_key=settings.gemini_api_key)
                token_count_response = client.models.count_tokens(
                    model="gemini-2.5-flash",
                    contents=original_text
                )
                total_tokens = token_count_response.total_tokens
                logger.info(f"Token count for task {task_id}: {total_tokens}")

                # 检查是否超过模型的token限制
                max_tokens = 1_048_576
                if total_tokens > max_tokens:
                    logger.warning(
                        f"Token limit exceeded: {total_tokens} > {max_tokens}")
                    raise TokenLimitExceededException(
                        f"Input text contains {total_tokens} tokens, which exceeds the maximum limit of {max_tokens} tokens"
                    )
            except TokenLimitExceededException:
                # 直接重新抛出token限制异常
                raise
            except Exception as e:
                logger.error(f"Failed to count tokens: {e}")
                raise BadRequestException(
                    f"Failed to validate input text: {str(e)}")

        # 创建 VideoGenerateTask 记录
        task = VideoGenerateTask(
            task_id=task_id,
            user_id=user_id,
            input_type=input_type,
            original_text=original_text,
            source_url=source_url,
            input_file_url=input_file_url,
            target_language=request.language,
            progress=0,
            voice_type=request.voice_type,
            status=DBTaskStatus.PENDING.value
        )

        # 保存到数据库
        db.add(task)
        await db.commit()
        await db.refresh(task)

        logger.info(f"Created task {task_id} with input_type={input_type}")

        # Submit task to Celery with the same task_id
        # The apply_async method will enqueue the task for processing
        celery_task = video_task.apply_async(args=[task_id], task_id=task_id)
        logger.info(f"Celery task submitted: {celery_task.id}")

        return task_id

    async def get_user_tasks(
        self,
        user_id: str,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取用户的视频任务列表（支持分页和状态筛选）

        Args:
            user_id: 用户ID
            db: 数据库会话
            page: 页码（从1开始）
            page_size: 每页数量
            status: 可选的状态筛选（pending, processing, completed, failed）

        Returns:
            包含任务列表、分页信息的字典
        """
        logger.info(
            f"Fetching tasks for user {user_id}, page={page}, page_size={page_size}, status={status}")

        # 验证分页参数
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 100:
            page_size = 100

        # 构建查询
        query = select(VideoGenerateTask).where(
            VideoGenerateTask.user_id == user_id)

        # 添加状态筛选
        if status:
            query = query.where(VideoGenerateTask.status == status)

        # 按创建时间降序排序
        query = query.order_by(desc(VideoGenerateTask.created_at))

        # 计算总数
        count_query = select(VideoGenerateTask).where(
            VideoGenerateTask.user_id == user_id)
        if status:
            count_query = count_query.where(VideoGenerateTask.status == status)

        result = await db.execute(count_query)
        total = len(result.scalars().all())

        # 计算分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # 执行查询
        result = await db.execute(query)
        tasks = result.scalars().all()

        # 转换为字典，排除 original_text 字段（内容太多）
        tasks_data = []
        for task in tasks:
            task_dict = task.to_dict(exclude_fields=['original_text'])
            # 添加 name 字段，从 original_text 截取前30个字符
            if task.original_text:
                name = task.original_text[:30] + '...' if len(
                    task.original_text) > 30 else task.original_text
            else:
                name = ''
            task_dict['name'] = name

            # 如果有 output_video_url，使用 get_signed_url 重新生成签名 URL
            if task_dict.get('output_video_url'):
                try:
                    signed_url = storage_service.get_signed_url(
                        task_dict['output_video_url'],
                        expiration=3600  # 1小时有效期
                    )
                    task_dict['output_video_url'] = signed_url
                    logger.debug(
                        f"Generated signed URL for task {task.task_id}")
                except Exception as e:
                    logger.error(
                        f"Failed to generate signed URL for task {task.task_id}: {e}")
                    # 保留原始 URL

            tasks_data.append(task_dict)

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        logger.info(f"Found {len(tasks_data)} tasks for user {user_id}")

        return {
            "tasks": tasks_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
