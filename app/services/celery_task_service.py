from app.repositories.course_repo import CourseRepository
from app.schemas.celery_task import CeleryTaskRead, CeleryTaskCreate
from app.tasks.summary_tasks import generate_summary_task
from app.repositories.celery_task_repo import CeleryTaskRepository
from app.db.models.course import CourseStatus
from app.schemas.course import CourseRead
from app.schemas.summary import SummaryUpdate


class CeleryTaskService:
    """
    Service layer for managing Celery task operations related to course summaries.

    Provides methods to get task status, start summary generation tasks, and update course summaries.
    """

    @staticmethod
    async def get_celery_task(
        session, task_id: str, current_user_id: int
    ) -> CeleryTaskRead:
        """
        Retrieve a Celery task by its ID.

        :param current_user_id: int
            The unique identifier of the current user.
        :param session: AsyncSession
            The database session for querying tasks.
        :param task_id: str
            The unique identifier of the Celery task.
        :return: CeleryTaskRead
            The serialized Celery task data.
        """
        task_repo = CeleryTaskRepository(session)
        celery_task = await task_repo.get_by_id(task_id, current_user_id)

        return CeleryTaskRead.from_orm(celery_task)

    @staticmethod
    async def start_celery_summary(course_id: int, current_user_id: int):
        """
        Start an asynchronous Celery task to generate a course summary.

        :param current_user_id: int
            The unique identifier of the current user.
        :param course_id: int
            The ID of the course to summarize.
        :return: CeleryTaskCreate
            A data object representing the initiated Celery task.
        """
        task = generate_summary_task.delay(course_id, current_user_id)

        return CeleryTaskCreate(
            task_id=task.id,
            status=task.status,
            course_id=course_id,
            user_id=current_user_id,
            result=str(task.result) if task.ready() else None,
        )

    @staticmethod
    async def put_summary_course(
        session, course_id: int, summary_update: SummaryUpdate, current_user_id: int
    ) -> CourseRead:
        """
        Update the AI-generated summary and status of a course.

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
