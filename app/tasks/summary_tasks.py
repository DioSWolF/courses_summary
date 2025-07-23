from app.db.session import unit_of_work
from app.repositories.course_repo import CourseRepository
from app.db.models.course import CourseStatus
import asyncio

from app.core.celery_worker import celery_app
from app.schemas.course import CourseRead
from app.repositories.celery_task_repo import CeleryTaskRepository
from app.schemas.celery_task import CeleryTaskCreate
from app.core.exceptions import SummaryEmptyError
from app.core.openai_client import openai_summarizer


@celery_app.task(name="celery_app.tasks.summary_tasks", bind=True, coroutine=True)
def generate_summary_task(self, course_id: int, current_user_id: int):
    """
    Celery task entry point to generate a course summary asynchronously.

    This task wraps the asynchronous _generate_summary coroutine
    to run it synchronously inside the Celery worker.

    :param current_user_id: int
        The unique identifier of the current user.
    :param self: Task instance provided by Celery when the task is bound.
    :param course_id: int
        The ID of the course to generate a summary for.
    :return: str
        JSON serialized CourseRead object representing the updated course.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _generate_summary(course_id, self.request.id, current_user_id)
    )


async def _generate_summary(course_id: int, task_id: str, current_user_id: int) -> str:
    """
    Asynchronous function that performs the summary generation.

    Creates a CeleryTask record with pending status,
    calls the OpenAI summarizer,
    updates the course with the summary and status,
    updates the CeleryTask with final status and result,
    and returns the serialized updated course.

    :param course_id: int
        The ID of the course to summarize.
    :param task_id: str
        The unique identifier of the Celery task.
    :raises SummaryEmptyError:
        If the summarization result is empty.
    :return: str
        JSON serialized CourseRead object with the updated course data.
    """
    async with unit_of_work() as session:
        task_repo = CeleryTaskRepository(session)
        course_repo = CourseRepository(session)

        course_obj = await course_repo.get_by_id(course_id, current_user_id)
        task_obj = CeleryTaskCreate(
            task_id=task_id,
            status=CourseStatus.pending.value,
            course_id=course_obj.id,
            user_id=course_obj.user_id,
            result=None,
        )
        await task_repo.create(task_obj)

        summary = await openai_summarizer.generate_summary(
            course_obj.course_description
        )

        if not summary:
            raise SummaryEmptyError()

        course_obj.ai_summary = summary
        course_obj.status = CourseStatus.completed.value
        await course_repo.save_commit(course_obj)

        task = await task_repo.get_by_id(task_id, current_user_id)
        course = await course_repo.get_by_id(course_id, current_user_id)
        task.status = course.status
        task.result = course.ai_summary
        await task_repo.save_commit(task)

        return CourseRead.from_orm(course_obj).json()
