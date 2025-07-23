from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.celery_task import CeleryTask
from app.core.exceptions import CeleryTaskNotFoundError
from app.schemas.celery_task import CeleryTaskCreate


class CeleryTaskRepository:
    """
    Repository class for managing CeleryTask entities in the database.

    Provides methods to create, retrieve, and save CeleryTask records asynchronously.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an asynchronous database session.

        :param db: AsyncSession
            The asynchronous SQLAlchemy session for database operations.
        """
        self.db = db

    async def create(self, celery_task: CeleryTaskCreate) -> CeleryTask:
        """
        Create a new CeleryTask record in the database.

        :param celery_task: CeleryTaskCreate
            The data for creating a new CeleryTask.
        :return: CeleryTask
            The created CeleryTask instance after saving and refreshing.
        """
        filtered_data = celery_task.dict()
        task_obj = CeleryTask(**filtered_data)
        task = await self.save_commit(task_obj)
        return task

    async def get_by_id(self, task_id: str, current_user_id: int) -> CeleryTask:
        """
        Retrieve a CeleryTask by its unique task ID.

        :param current_user_id: int
            The unique identifier of the current user.
        :param task_id: str
            The unique identifier of the Celery task.
        :raises CeleryTaskNotFoundError:
            Raised if no task with the specified ID exists.
        :return: CeleryTask
            The found CeleryTask instance.
        """
        result = await self.db.execute(
            select(CeleryTask).where(
                (CeleryTask.task_id == task_id)
                & (CeleryTask.user_id == current_user_id)
            )
        )
        celery_task = result.scalar_one_or_none()

        if celery_task is None:
            raise CeleryTaskNotFoundError(task_id)

        return celery_task

    async def save(self, task: CeleryTask):
        """
        Add and flush a CeleryTask instance to the current database session.

        :param task: CeleryTask
            The CeleryTask instance to save.
        :return: CeleryTask
            The saved CeleryTask instance refreshed from the database.
        """
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def save_commit(self, task: CeleryTask) -> CeleryTask:
        """
        Add, commit, and refresh a CeleryTask instance in the database.

        :param task: CeleryTask
            The CeleryTask instance to save and commit.
        :return: CeleryTask
            The committed and refreshed CeleryTask instance.
        """
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
