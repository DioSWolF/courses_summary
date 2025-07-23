from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead, UserWithToken
from app.services.user_service import UserService
from app.db.session import get_uow_session
from app.core.auth import get_current_user


router = APIRouter()


@router.post("/", response_model=UserWithToken, dependencies=[])
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_uow_session)):
    """
    Create a new user and return the user data along with an authentication token.

    :param user: UserCreate
        The user data required for creating a new user.
    :param db: AsyncSession, optional
        Database session dependency for saving the new user.
    :return: UserWithToken
        The created user information along with a JWT or authentication token.
    """
    return await UserService.create_user(db, user)


@router.get(
    "/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user)]
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_uow_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Retrieve user details by user ID.

    Requires authentication via the current user dependency.

    :param current_user: UserRead
        User dependency of the current user.
    :param user_id: int
        The unique identifier of the user to retrieve.
    :param db: AsyncSession, optional
        Database session dependency for querying the user.
    :return: UserRead
        The user data for the specified user ID.
    """
    return await UserService.get_user(db, user_id, current_user.id)
