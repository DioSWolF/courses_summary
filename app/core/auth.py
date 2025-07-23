from datetime import datetime

from asyncpg.pgproto.pgproto import timedelta
from fastapi import Depends
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_uow_session
from app.core.config import settings, api_key_header
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserRead
from app.services.auth_service import TokenService, AuthService


async def get_auth_service(db: AsyncSession = Depends(get_uow_session)) -> AuthService:
    """
    Provide an instance of AuthService configured with token service and user repository.

    :param db: AsyncSession, optional
        Database session dependency for user repository operations.
    :return: AuthService
        An authentication service instance ready for use.
    """
    token_service = TokenService(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )
    user_repo = UserRepository(db)

    return AuthService(token_service, user_repo)


async def get_current_user(
    authorization: str = Depends(api_key_header),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    """
    Retrieve the currently authenticated user based on the authorization header.

    :param authorization: str
        The API key or token passed in the request header.
    :param auth_service: AuthService, optional
        The authentication service dependency used to validate and retrieve the user.
    :return: UserRead
        The currently authenticated user's data.
    """
    return await auth_service.get_current_user(authorization)


def create_access_token(user_id: int) -> str:
    """
    Generate a JWT access token for a given user ID.

    The token contains the user ID as the subject and an expiration timestamp.

    :param user_id: int
        The unique identifier of the user to encode in the token.
    :return: str
        The encoded JWT token as a string.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
