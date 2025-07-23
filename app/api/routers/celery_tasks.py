from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.celery_task import CeleryTaskRead
from app.services.celery_task_service import CeleryTaskService
from app.schemas.course import CourseRead
from app.schemas.summary import SummaryUpdate
from app.services.summary_service import SummaryService
from app.db.session import get_uow_session
from app.core.config import rate_limiter
from app.core.auth import get_current_user
from app.schemas.user import UserRead

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/{task_id}/", response_model=CeleryTaskRead)
async def check_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_uow_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Retrieve the status and result of a Celery task by its ID.

    :param current_user: UserRead, optional
        The current authenticated user initiating the request.
    :param task_id: str
        The unique identifier of the Celery task.
    :param db: AsyncSession, optional
        Database session dependency for accessing task information.
    :return: CeleryTaskRead
        The current status and result of the specified Celery task.
    """
    return await CeleryTaskService.get_celery_task(db, task_id, current_user.id)


@router.post("/{course_id}")
async def generate_course_summary_async(
    course_id: int, current_user: UserRead = Depends(get_current_user)
):
    """
    Trigger asynchronous generation of a course summary.

    Enforces a rate limit of 3 summaries per user per hour.

    :param course_id: int
        The ID of the course for which the summary will be generated.
    :param current_user: UserRead, optional
        The current authenticated user initiating the request.
    :return: dict
        A task identifier or confirmation that the summary generation has started.
    """
    rate_limiter.enforce_limit(current_user.id)
    return await CeleryTaskService.start_celery_summary(course_id, current_user.id)


@router.put("/{course_id}", response_model=CourseRead)
async def update_course_summary(
    course_id: int,
    summary_update: SummaryUpdate,
    db: AsyncSession = Depends(get_uow_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Update the summary of an existing course.

    :param current_user: UserRead, optional
        The current authenticated user initiating the request.
    :param course_id: int
        The ID of the course to update.
    :param summary_update: SummaryUpdate
        The data used to update the course summary.
    :param db: AsyncSession, optional
        Database session dependency for committing updates.
    :return: CourseRead
        The updated course data including the new summary.
    """
    return await SummaryService.put_summary_course(
        db, course_id, summary_update, current_user.id
    )
