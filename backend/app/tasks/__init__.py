"""
Tasks Package - Celery 백그라운드 작업
"""
from .scheduler import celery_app

__all__ = ["celery_app"]
