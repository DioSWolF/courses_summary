from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User
from app.core.exceptions import UserNotFoundError
from app.schemas.user import UserCreate


class UserRepository:
    """
    Repository class for managing User entities in the database.

    Provides methods to create, retrieve, and save User records asynchronously.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with an asynchronous database session.

        :param db: AsyncSession
            The asynchronous SQLAlchemy session for database operations.
        """
        self.db = db

    async def create(self, user: UserCreate) -> User:
        """
        Create a new User record in the database.

        :param user: UserCreate
            The data required to create a new User.
        :return: User
            The created User instance after saving and refreshing.
        """
        user_obj = User(**user.dict())
        user = await self.save(user_obj)
        return user

    async def get_by_id(self, user_id: int) -> User:
        """
        Retrieve a User by its unique ID.

        :param user_id: int
            The unique identifier of the User.
        :raises UserNotFoundError:
            Raised if no User with the specified ID exists.
        :return: User
            The found User instance.
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundError(user_id)

        return user

    async def save(self, user: User) -> User:
        """
        Add and flush a User instance to the current database session.

        :param user: User
            The User instance to save.
        :return: User
            The saved User instance refreshed from the database.
        """
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
