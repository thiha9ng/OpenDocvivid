from typing import Dict, Any, List
import time
import os
import json
import tempfile
import wave
from tenacity import retry, stop_after_attempt, retry_unless_exception_type, wait_exponential
from celery import shared_task
from google import genai
from google.genai.types import GenerateContentConfig, ImageConfig, Part, SpeechConfig, VoiceConfig, PrebuiltVoiceConfig
from PIL import Image
from io import BytesIO
from sqlalchemy import select
from pydantic import BaseModel
from moviepy import (
    ImageClip, AudioFileClip, VideoFileClip,
    concatenate_videoclips, ColorClip
)
from moviepy.audio.AudioClip import AudioClip
import numpy as np
import tiktoken

from src.models.task_modes import LANGUAGE_NAMES
from src.configs.config import settings
from src.utils.logger import get_logger
from src.models.base import sync_session
from src.models.task_modes import VideoGenerateTask, TaskStatus
from src.models import User, CreditTransaction, TransactionType, calculate_segment_credit
from src.utils.storage import storage_service

logger = get_logger(__name__)


class TokenLimitExceededError(Exception):
    """Token数量超过限制的异常，不应该重试"""
    pass


class SegmentResponse(BaseModel):
    """分段响应模型"""
    segments: List[str]


class NarrationResponse(BaseModel):
    """旁白响应模型"""
    narration: str


@retry(stop=stop_after_attempt(3))
def split_content_into_segments(text: str, video_type: str = "tutorial") -> List[str]:
    """
    使用Gemini将文本内容分段

    Args:
        text: 原始文本内容
        video_type: 视频类型 (tutorial/promotional)

    Returns:
        分段后的内容列表
    """
    logger.info(f"Splitting content into segments for {video_type} video")

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    prompt = f"""
you are a professional video script editor.
Please decompose the following content into multiple segments suitable for making {'introduction video' if video_type == 'introduction' else 'tutorial video'}.

Requirements:
1. Each segment should be an independent scene or theme
2. Each segment should be medium length (suggested 30-100 words)
3. The segments should be logically coherent
4. The number of segments should be between 3-8

Content:
{text}
Result format:
{{
    "segments": ["segment1", "segment2", ...]
}}
Only return the JSON object, nothing else.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 16384,
                "response_mime_type": "application/json",
                "response_schema": SegmentResponse,
                "http_options": {'timeout': 180000},
            }
        )

        # 使用解析后的对象
        result: SegmentResponse = response.parsed
        segments = result.segments
        logger.info(f"Content split into {len(segments)} segments")
        return segments
    except Exception as e:
        logger.error(f"Failed to split content into segments: {e}")
        # 如果解析失败，将整个文本作为单一段落
        raise e


@retry(stop=stop_after_attempt(3))
def generate_image_for_segment(segment_text: str, index: int, temp_dir: str) -> str:
    """
    使用Gemini为每个段落生成图片

    Args:
        segment_text: 段落文本
        index: 段落索引
        temp_dir: 临时目录路径

    Returns:
        生成的图片路径
    """
    logger.info(f"Generating image for segment {index}")

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    # 首先生成图片描述prompt
    prompt_generation = f"""
content:
```
{segment_text}
```
1. generate infographic for above blog content
2. extract key information
3. Keep the infographic concise
4. image word only use english
5. Plus rich and cute cartoon elements

"""

    # 使用gemini-2.5-flash-image生成图片
    try:
        image_response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt_generation],
             config=GenerateContentConfig(
                image_config=ImageConfig(
                    aspect_ratio="16:9",
                ),
                http_options={'timeout': 180000},
            )
        )

        # 保存图片
        image_path = os.path.join(temp_dir, f"image_{index:03d}")

        # 从response.candidates[0].content.parts中提取图片数据
        image_saved = False
        for part in image_response.candidates[0].content.parts:
            if part.text is not None:
                # 跳过文本部分
                continue
            elif part.inline_data is not None:
                # 找到图片数据
                mime_type = part.inline_data.mime_type
                extension = mime_type.split("/")[-1]
                image = Image.open(BytesIO(part.inline_data.data))
                image_path = image_path + "." + extension
                image.save(image_path)
                logger.info(f"Image saved to {image_path}")
                image_saved = True
                break

        if image_saved:
            return image_path
        else:
            logger.error(
                f"No image data found in response for segment {index}")
            raise Exception(
                f"No image data found in response for segment {index}")

    except Exception as e:
        logger.error(f"Failed to generate image for segment {index}: {e}")
        raise e


def create_placeholder_image(image_path: str) -> str:
    """创建一个简单的占位图片"""
    # 使用PIL创建一个纯色占位图片
    img = Image.new('RGB', (1920, 1080), color='gray')
    img.save(image_path)
    logger.info(f"Created placeholder image: {image_path}")
    return image_path


@retry(stop=stop_after_attempt(3))
def generate_narration_script(segment_text: str, index: int, language: str = "en") -> str:
    """
    为每个段落生成旁白台词和视频脚本

    Args:
        segment_text: 段落文本
        index: 段落索引
        language: 目标语言

    Returns:
        包含narration和script的字典
    """
    logger.info(f"Generating narration script for segment {index}")

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    target_language = LANGUAGE_NAMES.get(language, "English")

    prompt = f"""
you are a professional video script writer.
Please generate narration script for the following content.

Content: {segment_text}

Requirements:
1. The narration script should be natural and fluent, suitable for speech synthesis
2. The narration should use {target_language} language
3. The narration should be done in one go
only return the narration script, nothing else.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "http_options": {'timeout': 180000},
            }
        )

        # 使用解析后的对象
        logger.info(f"Generated narration for segment {index}")
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate narration script: {e}")
        raise e

@retry(stop=stop_after_attempt(3))
def generate_audio_from_text(text: str, index: int, temp_dir: str, language: str = "en", voice: str = "Achernar") -> str:
    """
    使用Gemini TTS将台词转换为语音

    Args:
        text: 台词文本
        index: 段落索引
        temp_dir: 临时目录路径
        language: 语言代码
        voice: 语音类型

    Returns:
        生成的音频文件路径
    """
    logger.info(f"Generating audio for segment {index} with voice {voice}")

    # 计算并限制text的token数量，不超过3.2万
    max_tokens = 32000
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    token_count = len(tokens)

    logger.info(f"Original text token count: {token_count}")

    if token_count > max_tokens:
        logger.error(
            f"Text token count ({token_count}) exceeds maximum limit ({max_tokens})")
        # 抛出自定义异常，停止重试
        raise TokenLimitExceededError(
            f"Text token count ({token_count}) exceeds maximum limit ({max_tokens}). "
            f"Please reduce the text length."
        )

    # 创建客户端时设置更长的超时时间（300秒 = 5分钟）
    client = genai.Client(
        api_key=settings.gemini_api_key
    )
    wav_path = os.path.join(temp_dir, f"audio_{index:03d}.wav")

    try:
        # 使用最新的Gemini TTS API
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=GenerateContentConfig(
                response_modalities=["AUDIO"],
                http_options={'timeout': 360000},
                speech_config=SpeechConfig(
                    voice_config=VoiceConfig(
                        prebuilt_voice_config=PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                )
            )
        )

        # 从响应中提取音频数据
        if response.candidates and response.candidates[0].content.parts:
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            # save file
            wave_file(wav_path, audio_data)
            logger.info(f"Audio saved to {wav_path}")
            return wav_path
        else:
            logger.error(f"No audio data received for segment {index}")
            raise Exception(f"No audio data received for segment {index}")
    except Exception as e:
        logger.error(f"Failed to generate audio for segment {index}: {e}")
        raise e

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

def convert_audio_to_wav(input_path: str, output_path: str) -> str:
    """将音频文件转换为WAV格式"""
    try:
        # 使用moviepy读取音频并导出为WAV
        audio = AudioFileClip(input_path)
        audio.write_audiofile(
            output_path,
            codec='pcm_s16le',
            fps=44100,
            nbytes=2,
            logger=None  # 禁用moviepy的日志输出
        )
        audio.close()

        logger.info(f"Audio converted to WAV: {output_path}")

        # 删除原始文件
        if os.path.exists(input_path) and input_path != output_path:
            os.remove(input_path)

        return output_path
    except Exception as e:
        logger.error(f"Failed to convert audio to WAV: {e}")
        # 如果转换失败，返回原始文件
        return input_path


def create_silence_audio(audio_path: str, duration: float = 3.0) -> str:
    """创建一个静音音频文件"""
    # 使用moviepy创建静音音频
    def make_frame(t):
        return np.zeros(2)  # 双声道静音

    audio = AudioClip(make_frame, duration=duration, fps=44100)
    audio.write_audiofile(audio_path, fps=44100, logger=None)
    audio.close()

    logger.info(f"Created silence audio: {audio_path}")
    return audio_path


def get_audio_duration(audio_path: str) -> float:
    """获取音频文件的时长"""
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()
    return duration


def get_video_duration(video_path: str) -> float:
    """获取视频文件的时长（秒）"""
    video = VideoFileClip(video_path)
    duration = video.duration
    video.close()
    return duration


def merge_image_and_audio(image_path: str, audio_path: str, output_path: str) -> str:
    """
    使用moviepy将图片和音频合成为视频片段

    Args:
        image_path: 图片路径
        audio_path: 音频路径
        output_path: 输出视频路径

    Returns:
        输出视频路径
    """
    logger.info(f"Merging image and audio to {output_path}")

    # 加载音频并获取时长
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # 创建图片视频片段，时长与音频相同
    video = ImageClip(image_path, duration=duration)

    # 将音频添加到视频
    video = video.with_audio(audio)

    # 导出视频
    video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        audio_bitrate='192k',
        preset='medium',
        logger=None  # 禁用moviepy的进度输出
    )

    # 关闭资源 - 使用 del 而不是 close() 来避免 moviepy 删除输出文件
    # 参考: https://github.com/Zulko/moviepy/issues/1084
    del video
    del audio

    # 验证文件是否存在
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Video segment file was not created: {output_path}")
    
    logger.info(f"Video segment created: {output_path}")
    return output_path


def concatenate_videos(video_paths: List[str], output_path: str) -> str:
    """
    使用moviepy将多个视频片段拼接成最终视频

    Args:
        video_paths: 视频片段路径列表
        output_path: 输出视频路径

    Returns:
        输出视频路径
    """
    logger.info(f"Concatenating {len(video_paths)} video segments")

    # 验证所有视频片段是否存在
    for i, path in enumerate(video_paths):
        if not os.path.exists(path):
            logger.error(f"Video segment {i} not found: {path}")
            raise FileNotFoundError(f"Video segment {i} not found: {path}")
        logger.info(f"Found video segment {i}: {path} ({os.path.getsize(path)} bytes)")

    # 加载所有视频片段
    clips = [VideoFileClip(path) for path in video_paths]

    # 拼接视频
    final_video = concatenate_videoclips(clips, method="compose")

    # 导出最终视频
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        logger=None  # 禁用moviepy的进度输出
    )

    # 关闭所有资源 - 使用 del 而不是 close() 来避免 moviepy 删除输出文件
    del final_video
    for clip in clips:
        del clip

    # 验证输出文件是否存在
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Final video file was not created: {output_path}")

    logger.info(f"Final video created: {output_path}")
    return output_path


def update_task_progress(session, task, progress_percent: float, status_message: str = None):
    """更新任务进度并提交到数据库"""
    try:
        if task:
            # 更新进度字段
            task.progress = int(progress_percent)
            # 提交到数据库，让前端可以实时查询进度
            session.commit()
            
        # 记录日志
        log_msg = f"Progress: {progress_percent:.1f}%"
        if status_message:
            log_msg += f" - {status_message}"
        logger.info(log_msg)
    except Exception as e:
        logger.error(f"Failed to update progress: {e}")
        # 即使更新进度失败，也不应该中断任务执行
        # 回滚以避免影响后续的数据库操作
        session.rollback()


@shared_task(bind=True, name='src.tasks.generate_tasks.video_task', queue='generate_task_queue',
             autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def video_task(self, task_id: str) -> Dict[str, Any]:
    """
    Celery task for video generation

    Args:
        task_id: Unique identifier for the task

    Returns:
        Dictionary containing the result of the video generation
    """
    logger.info(f"Processing video generation task for {task_id}")

    session = sync_session()
    temp_dir = None
    task = None

    try:
        # 1. 从数据库获取任务
        logger.info("Fetching task from database")
        stmt = select(VideoGenerateTask).where(
            VideoGenerateTask.task_id == task_id)
        result = session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            logger.error(f"Task {task_id} not found")
            return {"status": "failed", "error": "Task not found"}

        # 更新任务状态为处理中，并设置初始进度 (5%)
        task.status = TaskStatus.PROCESSING.value
        task.progress = 5
        session.commit()

        # 2. 获取文本内容 (10%)
        update_task_progress(session, task, 10, "Loading text content")
        text_content = task.original_text
        if not text_content:
            raise ValueError("No text content found in task")

        logger.info(f"Text content length: {len(text_content)}")

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {temp_dir}")

        # 3. 使用Gemini将内容分段 (20%)
        update_task_progress(
            session, task, 20, "Splitting content into segments")
        segments = split_content_into_segments(text_content, "introduction")
        logger.info(f"Content split into {len(segments)} segments")

        if not segments:
            raise ValueError("Failed to split content into segments")

        # 4-7. 为每个段落生成图片、台词、音频和视频片段 (20-80%)
        video_segments = []
        segment_durations = []  # 记录每个segment的时长
        segment_progress_range = 60  # 从20%到80%，共60%的进度

        for i, segment in enumerate(segments):
            base_progress = 20 + (i * segment_progress_range / len(segments))
            logger.info(f"Processing segment {i+1}/{len(segments)}")

            # 生成图片 (每个segment的25%)
            update_task_progress(session, task, base_progress,
                                 f"Generating image for segment {i+1}")
            image_path = generate_image_for_segment(segment, i, temp_dir)

            # 生成台词和脚本 (每个segment的25%)
            update_task_progress(session, task, base_progress + segment_progress_range/(len(segments)*4),
                                 f"Generating narration for segment {i+1}")
            narration_text = generate_narration_script(
                segment, i, task.target_language
            )

            # 生成音频 (每个segment的25%)
            update_task_progress(session, task, base_progress + segment_progress_range/(len(segments)*2),
                                 f"Generating audio for segment {i+1}")
            audio_path = generate_audio_from_text(
                narration_text, i, temp_dir,
                task.target_language, task.voice_type
            )

            # 合成视频片段 (每个segment的25%)
            update_task_progress(session, task, base_progress + segment_progress_range*3/(len(segments)*4),
                                 f"Merging video segment {i+1}")
            segment_video_path = os.path.join(temp_dir, f"segment_{i:03d}.mp4")
            merge_image_and_audio(image_path, audio_path, segment_video_path)
            video_segments.append(segment_video_path)
            
            # 获取并记录该segment的时长
            segment_duration = get_video_duration(segment_video_path)
            segment_durations.append(segment_duration)
            logger.info(f"Segment {i+1} duration: {segment_duration:.2f} seconds")

        # 8. 拼接所有视频片段 (85%)
        update_task_progress(session, task, 85, "Concatenating video segments")
        final_video_path = os.path.join(temp_dir, "final_video.mp4")
        concatenate_videos(video_segments, final_video_path)

        # 检查最终视频文件是否存在且有效
        if not os.path.exists(final_video_path):
            raise ValueError("Final video file was not created")

        file_size = os.path.getsize(final_video_path)
        logger.info(f"Final video size: {file_size / 1024 / 1024:.2f} MB")

        if file_size < 1000:  # 如果文件小于1KB，可能有问题
            raise ValueError(
                "Final video file is too small, possibly corrupted")

        # 9. 上传最终视频到GCS (95%)
        update_task_progress(
            session, task, 95, "Uploading video to cloud storage")
        logger.info("Uploading final video to GCS")
        output_gcs_path = f"outputs/{task_id}/video.mp4"

        # 同步上传到GCS
        blob = storage_service.bucket.blob(output_gcs_path)
        blob.upload_from_filename(final_video_path, content_type="video/mp4")

        # 计算视频总时长（所有segment时长相加）
        total_duration = sum(segment_durations)
        logger.info(f"Total video duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")

        # 10. 计算并扣除积分 (98%)
        update_task_progress(session, task, 98, "Calculating and consuming credits")
        try:
            # 计算每个segment的积分（时长单位：秒）
            segment_credits = [calculate_segment_credit(int(duration)) for duration in segment_durations]
            total_credits = sum(segment_credits)
            
            logger.info(f"Credit calculation - Segments: {len(segment_durations)}, "
                       f"Durations: {[int(d) for d in segment_durations]}, "
                       f"Credits: {segment_credits}, Total: {total_credits}")
            
            # 获取用户并扣除积分（允许为负数）
            user = session.query(User).filter(User.id == task.user_id).first()
            if not user:
                logger.error(f"User {task.user_id} not found for credit deduction")
                raise ValueError(f"User {task.user_id} not found")
            
            # 记录扣除前的余额
            balance_before = user.credit_balance
            
            # 扣除积分（允许为负数）
            user.credit_balance -= total_credits
            
            # 创建积分流水记录
            transaction = CreditTransaction(
                user_id=task.user_id,
                task_id=task.id,
                transaction_type=TransactionType.TASK_CONSUME.value,
                amount=-total_credits,  # 负数表示消耗
                balance_after=user.credit_balance,
                description=f"task {task.task_id} consume {total_credits} credits (segments: {len(segment_durations)})",
                extra_metadata=json.dumps({
                    "segment_durations": [int(d) for d in segment_durations],
                    "segment_credits": segment_credits,
                    "total_duration": int(total_duration)
                })
            )
            
            session.add(transaction)
            
            logger.info(f"Credit deduction - User: {task.user_id}, "
                       f"Before: {balance_before}, Consumed: {total_credits}, "
                       f"After: {user.credit_balance}")
            
            # 如果余额为负，记录警告
            if user.credit_balance < 0:
                logger.warning(f"User {task.user_id} credit balance is negative: {user.credit_balance}")
            
        except Exception as credit_error:
            logger.error(f"Failed to deduct credits: {credit_error}", exc_info=True)
            # 积分扣除失败不应该导致整个任务失败，只记录错误
            total_credits = 0  # 设置为0，避免后续使用未定义的变量

        # 11. 更新任务状态 (100%)
        task.output_video_url = output_gcs_path
        task.video_duration = int(total_duration)  # 存储为整数（秒）
        task.credit_cost = total_credits  # 记录积分消耗
        task.status = TaskStatus.COMPLETED.value
        task.progress = 100
        task.error_message = None  # 清除之前可能的错误信息
        session.commit()
        logger.info("Task completed: 100%")

        logger.info(f"Video generation completed for task {task_id}")

        return {
            "status": "completed",
            "task_id": task_id,
            "output_video_url": output_gcs_path,
            "segments_count": len(segments),
            "video_size_mb": file_size / 1024 / 1024,
            "video_duration": int(total_duration),
            "credit_cost": total_credits
        }

    except Exception as e:
        logger.error(
            f"Error processing video task {task_id}: {e}", exc_info=True)

        # 更新任务状态为失败
        if session and task:
            task.status = TaskStatus.FAILED.value
            task.error_message = str(e)
            session.commit()

        return {
            "status": "failed",
            "task_id": task_id,
            "error": str(e)
        }

    finally:
        # 清理临时文件
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary directory: {e}")

        if session:
            session.close()
