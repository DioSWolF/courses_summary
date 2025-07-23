from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_uow_session
from app.services.summary_service import SummaryService
from app.schemas.course import CourseRead
from app.schemas.summary import SummaryUpdate
from app.core.config import rate_limiter
from app.core.auth import get_current_user
from app.schemas.user import UserRead

router = APIRouter(dependencies=[Depends(get_current_user)])


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
    :return: json str
        A response indicating the summary generation task has started.
    """
    rate_limiter.enforce_limit(current_user.id)
    return await SummaryService.start_celery_summary(course_id, current_user.id)


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
        The data containing the updated summary fields.
    :param db: AsyncSession, optional
        Database session dependency for saving the update.
    :return: CourseRead
        The updated course data after applying the summary changes.
    """
    return await SummaryService.put_summary_course(
        db, course_id, summary_update, current_user.id
    )
