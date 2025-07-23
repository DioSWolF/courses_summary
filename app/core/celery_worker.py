from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_backend=settings.redis_url,
    task_track_started=True,
    task_ignore_result=False,
)
celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}
