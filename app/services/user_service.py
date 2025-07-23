from app.schemas.user import UserCreate, UserRead, UserWithToken
from app.repositories.user_repo import UserRepository
from app.core.auth import create_access_token
from app.core.validation import check_owner


class UserService:
    """
    Service layer for managing user-related operations.

    Provides methods for user creation and retrieval.
    """

    @staticmethod
    async def create_user(session, user: UserCreate):
        """
        Create a new user and generate an access token for authentication.

        :param session: AsyncSession
            The database session used for operations.
        :param user: UserCreate
            The user data required to create a new user.
        :return: UserWithToken
            The created user data along with an access token and token type.
        """
        user_repo = UserRepository(session)
        user_obj = await user_repo.create(user)
        access_token = create_access_token(user_obj.id)

        return UserWithToken(
            user=user_obj, access_token=access_token, token_type="bearer"
        )

    @staticmethod
    async def get_user(session, user_id: int, current_user_id: int):
        """
        Retrieve a user by their unique ID.

        :param current_user_id: int
        The unique identifier of the current user.
        :param session: AsyncSession
            The database session used for querying.
        :param user_id: int
            The unique identifier of the user.
        :return: UserRead
            The user data serialized for response.
        """
        check_owner(current_user_id, user_id)
        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(user_id)

        return UserRead.from_orm(user)
