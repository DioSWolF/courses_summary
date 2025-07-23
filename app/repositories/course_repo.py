from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.course import Course
from app.core.exceptions import CourseNotFoundError


class CourseRepository:
    """
    Repository class for managing Course entities in the database.

    Provides methods to retrieve and persist Course records asynchronously.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an asynchronous database session.

        :param db: AsyncSession
            The asynchronous SQLAlchemy session for database operations.
        """
        self.db = db

    async def get_by_id(self, course_id: int, current_user_id: int) -> Course:
        """
        Retrieve a Course by its unique ID.

        :param current_user_id: int
            The unique identifier of the current user.
        :param course_id: int
            The unique identifier of the course.
        :raises CourseNotFoundError:
            Raised if no course with the specified ID exists.
        :return: Course
            The found Course instance.
        """
        result = await self.db.execute(
            select(Course).where(
                (Course.id == course_id) & (Course.user_id == current_user_id)
            )
        )
        course = result.scalar_one_or_none()

        if not course:
            raise CourseNotFoundError(course_id)

        return course

    async def save(self, course: Course) -> Course:
        """
        Add and flush a Course instance to the current database session.

        :param course: Course
            The Course instance to save.
        :return: Course
            The saved Course instance refreshed from the database.
        """
        self.db.add(course)
        await self.db.flush()
        await self.db.refresh(course)
        return course

    async def save_commit(self, course: Course):
        """
        Add, commit, and refresh a Course instance in the database.

        :param course: Course
            The Course instance to save and commit.
        """
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
