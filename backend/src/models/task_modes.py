import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base, utc_now

class TaskStatus(PyEnum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SegmentStatus(PyEnum):
    """Segment status enumeration"""
    PENDING = "pending"
    TEXT_EXTRACTED = "text_extracted"
    IMAGE_GENERATED = "image_generated"
    AUDIO_GENERATED = "audio_generated"
    VIDEO_GENERATED = "video_generated"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoGenerateTask(Base):
    """
    Video generate task model
    """
    __tablename__ = "video_generate_tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    # Task identification
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Input data
    input_type = Column(String(50), nullable=False)  # text, file, url
    original_text = Column(Text, nullable=True)  # Text input or extracted from file/url
    source_url = Column(String(255), nullable=True)  # URL input if provided
    
    # Storage information
    input_file_url = Column(String(255), nullable=True)  # URL for uploaded input file
    output_video_url = Column(String(255), nullable=True)  # URL for generated video
    audio_url = Column(String(255), nullable=True)  # URL for generated/extracted audio
    video_duration = Column(Integer, nullable=True)  # Video duration in seconds
    
    # Credit information
    credit_cost = Column(Integer, nullable=True)  # 任务消耗的积分数
    
    # Processing parameters
    target_language = Column(String(20), nullable=False, default="en")
    voice_type = Column(String(50), nullable=False, default="Achernar")
    
    # Task status and tracking
    status = Column(String(50), nullable=False, default=TaskStatus.PENDING.value, index=True)
    progress = Column(Integer, nullable=False, default=0)  # Progress: 0-100
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Relationship to segments
    segments = relationship("VideoSegment", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VideoGenerateTask(id={self.id}, task_id={self.task_id}, status={self.status})>"
    
    def to_dict(self, include_segments=False, exclude_fields=None):
        """Convert model instance to dictionary
        
        Args:
            include_segments: Whether to include segments data
            exclude_fields: List of field names to exclude from the result
        """
        try:
            # Safely access all attributes to handle potential lazy loading
            id_value = str(self.id) if hasattr(self, 'id') and self.id is not None else None
            user_id_value = str(self.user_id) if hasattr(self, 'user_id') and self.user_id is not None else None
            result = {
                "id": id_value,
                "user_id": user_id_value,
                "task_id": self.task_id,
                "input_type": self.input_type,
                "original_text": self.original_text,
                "source_url": self.source_url,
                "input_file_url": self.input_file_url,
                "output_video_url": self.output_video_url,
                "audio_url": self.audio_url,
                "video_duration": self.video_duration,
                "credit_cost": self.credit_cost,
                "target_language": self.target_language,
                "voice_type": self.voice_type,
                "status": self.status,
                "progress": self.progress,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "error_message": self.error_message
            }
            
            # Exclude specified fields
            if exclude_fields:
                for field in exclude_fields:
                    result.pop(field, None)
            
            # Optionally include segments
            if include_segments and hasattr(self, 'segments'):
                result["segments"] = [segment.to_dict() for segment in self.segments]
            
            return result
        except Exception as e:
            # Log the error and return a minimal dict
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in to_dict(): {e}")
            return {
                "task_id": getattr(self, 'task_id', None),
                "status": getattr(self, 'status', None),
                "error": "Failed to serialize task data"
            } 


class VideoSegment(Base):
    """
    Video segment model for storing intermediate results of each text segment
    """
    __tablename__ = "video_segments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to parent task
    task_id = Column(UUID(as_uuid=True), ForeignKey('video_generate_tasks.id'), nullable=False, index=True)
    
    # Segment information
    segment_index = Column(Integer, nullable=False)  # Order of segment in the task
    segment_text = Column(Text, nullable=False)  # Text content of this segment
    
    # Generated assets URLs
    image_url = Column(String(255), nullable=True)  # Generated image for this segment
    audio_url = Column(String(255), nullable=True)  # Generated audio for this segment
    video_url = Column(String(255), nullable=True)  # Generated video clip for this segment
    
    # Segment metadata
    duration = Column(Integer, nullable=True)  # Duration in seconds
    segment_metadata = Column(JSON, nullable=True)  # Additional metadata (e.g., image generation params, audio params)
    
    # Segment status and tracking
    status = Column(String(50), nullable=False, default=SegmentStatus.PENDING.value, index=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Relationship to parent task
    task = relationship("VideoGenerateTask", back_populates="segments")
    
    def __repr__(self):
        return f"<VideoSegment(id={self.id}, task_id={self.task_id}, segment_index={self.segment_index}, status={self.status})>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        try:
            id_value = str(self.id) if hasattr(self, 'id') and self.id is not None else None
            task_id_value = str(self.task_id) if hasattr(self, 'task_id') and self.task_id is not None else None
            return {
                "id": id_value,
                "task_id": task_id_value,
                "segment_index": self.segment_index,
                "segment_text": self.segment_text,
                "image_url": self.image_url,
                "audio_url": self.audio_url,
                "video_url": self.video_url,
                "duration": self.duration,
                "segment_metadata": self.segment_metadata,
                "status": self.status,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "error_message": self.error_message
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in VideoSegment.to_dict(): {e}")
            return {
                "id": getattr(self, 'id', None),
                "segment_index": getattr(self, 'segment_index', None),
                "status": getattr(self, 'status', None),
                "error": "Failed to serialize segment data"
            }


# Supported languages
SUPPORTED_LANGUAGES = [
    'en',      # English
    'zh',      # Simplified Chinese
    'ja',      # Japanese
    'ko',      # Korean
    'fr',      # French
    'de',      # German
    'es',      # Spanish
    'pt',      # Portuguese
    'ru',      # Russian
    'ar',      # Arabic
    'hi',      # Hindi
    'it',      # Italian
    'nl',      # Dutch
    'sv',      # Swedish
    'id',      # Indonesian
    'pl',      # Polish
    'th',      # Thai
    'tr',      # Turkish
    'vi',      # Vietnamese
    'ro',      # Romanian
    'uk',      # Ukrainian
    'bn',      # Bengali
    'mr',      # Marathi
    'ta',      # Tamil
    'te',      # Telugu
]

# Language code to language name mapping
LANGUAGE_NAMES = {
    'en': 'English',
    'zh': 'Simplified Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'it': 'Italian',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'id': 'Indonesian',
    'pl': 'Polish',
    'th': 'Thai',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'ro': 'Romanian',
    'uk': 'Ukrainian',
    'bn': 'Bengali',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'te': 'Telugu',
}

def validate_languages(languages):
    """Validate target languages"""
    if not languages:
        return False, "Target languages cannot be empty"
    
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            return False, f"Unsupported language: {lang}"
    
    return True, None