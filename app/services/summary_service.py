import asyncio
import json

from celery.result import AsyncResult

from app.repositories.course_repo import CourseRepository
from app.db.models.course import CourseStatus
from app.schemas.course import CourseRead
from app.schemas.summary import SummaryUpdate
from app.core.config import settings
from app.tasks.summary_tasks import generate_summary_task
from app.core.exceptions import InternalServerError


class SummaryService:
    """
    Service for managing course summaries using Celery asynchronous tasks.

    Provides methods to start a summary generation task and update course summaries.
    """

    @staticmethod
    async def start_celery_summary(course_id: int, current_user_id: int):
        """
        Start a Celery task to generate a course summary and poll for its result.

        The method polls the task status at intervals defined by settings.poll_interval
        until the task is ready or a timeout defined by settings.timeout_seconds is reached.

        :param current_user_id: int
            The unique identifier of the current user.
        :param course_id: int
            The ID of the course to generate a summary for.
        :return: CourseRead | None
            The course data with generated summary if the task completed successfully,
            otherwise None if the task timed out.
        """
        task = generate_summary_task.delay(course_id, current_user_id)
        max_attempts = int(settings.timeout_seconds / settings.poll_interval)

        for _ in range(max_attempts):
            result = AsyncResult(task.id)

            if result.ready():
                break

            await asyncio.sleep(settings.poll_interval)

        result = AsyncResult(task.id)

        if result.failed():
            raise InternalServerError(log_message=result.failed())

        if result.ready():
            return CourseRead(**json.loads(result.result))

        return None

    @staticmethod
    async def put_summary_course(
        session, course_id: int, summary_update: SummaryUpdate, current_user_id: int
    ) -> CourseRead:
        """
        Update the AI-generated summary and status of a course in the database.

        :param current_user_id: int
            The unique identifier of the current user.
        :param session: AsyncSession
            The database session for updating the course.
        :param course_id: int
            The ID of the course to update.
        :param summary_update: SummaryUpdate
            The updated summary data.
        :return: CourseRead
            The updated course data serialized for response.
        """
        course_repo = CourseRepository(session)
        course_obj = await course_repo.get_by_id(course_id, current_user_id)

        course_obj.ai_summary = summary_update.summary
        course_obj.status = CourseStatus.finalized.value
        course = await course_repo.save(course_obj)

        return CourseRead.from_orm(course)
