from app.db.models.course import Course
from app.repositories.course_repo import CourseRepository
from app.schemas.course import CourseCreate, CourseRead
from app.services.user_service import UserService


class CourseService:
    """
    Service layer for managing courses.

    Provides methods to create new courses and retrieve existing courses by ID.
    """

    @staticmethod
    async def create_course(
        session, course: CourseCreate, current_user_id: int
    ) -> CourseRead:
        """
        Create a new course associated with an existing user.

        :param current_user_id: int
            The unique identifier of the current user.
        :param session: AsyncSession
            The database session used for operations.
        :param course: CourseCreate
            The data required to create a new course, including user_id.
        :raises UserNotFoundError:
            If the user associated with course.user_id does not exist.
        :return: CourseRead
            The created course data serialized for response.
        """
        await UserService.get_user(session, course.user_id, current_user_id)
        course_obj = Course(**course.dict())
        repo = CourseRepository(session)
        course = await repo.save(course_obj)

        return CourseRead.from_orm(course)

    @staticmethod
    async def get_course(session, course_id: int, current_user_id: int) -> CourseRead:
        """
        Retrieve a course by its ID.

        :param current_user_id: int
            The unique identifier of the current user.
        :param session: AsyncSession
            The database session used for querying.
        :param course_id: int
            The unique identifier of the course to retrieve.
        :return: CourseRead
            The course data serialized for response.
        """
        course_repo = CourseRepository(session)
        course_obj = await course_repo.get_by_id(course_id, current_user_id)
        return CourseRead.from_orm(course_obj)
