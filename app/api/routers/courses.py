from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user

from app.schemas.course import CourseRead, CourseCreate
from app.services.course_service import CourseService
from app.db.session import get_uow_session
from app.schemas.user import UserRead

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=CourseRead)
async def create_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_uow_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Create a new course with the provided details.

    :param current_user: UserRead, optional
        The current authenticated user initiating the request.
    :param course: CourseCreate
        The data required to create a new course.
    :param db: AsyncSession, optional
        Database session dependency for saving the new course.
    :return: CourseRead
        The newly created course data.
    """
    return await CourseService.create_course(db, course, current_user.id)


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_uow_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Retrieve details of a course by its ID.

    :param current_user: UserRead, optional
        The current authenticated user initiating the request.
    :param course_id: int
        The unique identifier of the course to retrieve.
    :param db: AsyncSession, optional
        Database session dependency for querying the course.
    :return: CourseRead
        The course data corresponding to the given ID.
    """
    return await CourseService.get_course(db, course_id, current_user.id)
