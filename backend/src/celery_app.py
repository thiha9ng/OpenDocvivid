"""
Celery application module for Multi Translate Service
"""

import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from src.configs.config import settings

celery_app = Celery("celery_app")

class CeleryConfig:
    # Broker configuration (Redis)
    broker_url = settings.celery_broker_url
    result_backend = settings.celery_result_backend
    
    # Task routes configuration
    task_routes = {
        'src.tasks.generate_tasks.video_task': {
            'queue': 'generate_task_queue'
        },
        'grant_monthly_credits': {
            'queue': 'default'
        },
        'check_expired_subscriptions': {
            'queue': 'default'
        },
        'check_subscription_renewal': {
            'queue': 'default'
        }
    }
    
    # Queue configuration
    task_default_queue = 'default'
    task_queues = (
        Queue('default', routing_key='default'),
        Queue('generate_task_queue', routing_key='video_task'),
    )
    
    # Celery Beat scheduled task configuration
    beat_schedule = {
        # Grant monthly credits every day at midnight
        'grant-monthly-credits': {
            'task': 'grant_monthly_credits',
            'schedule': crontab(hour=0, minute=0),
            'options': {'queue': 'default'}
        },
        # Check expired subscriptions every day at 1 AM
        'check-expired-subscriptions': {
            'task': 'check_expired_subscriptions',
            'schedule': crontab(hour=1, minute=0),
            'options': {'queue': 'default'}
        },
        # Check subscription renewal every day at 9 AM
        'check-subscription-renewal': {
            'task': 'check_subscription_renewal',
            'schedule': crontab(hour=9, minute=0),
            'options': {'queue': 'default'}
        },
        # Clean up expired pending subscriptions every hour
        'cleanup-expired-pending-subscriptions': {
            'task': 'cleanup_expired_pending_subscriptions',
            'schedule': crontab(minute=0),
            'options': {'queue': 'default'}
        },
    }
    
    # Timezone
    timezone = 'UTC'
    enable_utc = True

celery_app.config_from_object(CeleryConfig)

celery_app.autodiscover_tasks([
    'src.tasks.generate_tasks',
    'src.tasks.credit_tasks',
])