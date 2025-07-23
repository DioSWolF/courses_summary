from datetime import datetime, timedelta

from jose import jwt, JWTError

from app.core.exceptions import UnauthorizedError, InternalServerError
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserRead


class TokenService:
    """
    Service for creating and decoding JWT access tokens.

    Attributes:
        secret_key (str): Secret key used for encoding and decoding JWT.
        algorithm (str): Algorithm used for JWT encoding/decoding.
        expire_minutes (int): Token expiration time in minutes.
    """

    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int):
        """
        Initialize the TokenService with JWT configuration.

        :param secret_key: str
            Secret key for signing the JWT tokens.
        :param algorithm: str
            Algorithm used to encode/decode the tokens (e.g., "HS256").
        :param expire_minutes: int
            Expiration time of the access token in minutes.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_access_token(self, user_id: int) -> str:
        """
        Generate a JWT access token for the specified user ID.

        :param user_id: int
            The user ID to embed in the token's subject.
        :return: str
            The encoded JWT token.
        """
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        to_encode = {"sub": str(user_id), "exp": expire}
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_access_token(self, token: str) -> dict:
        """
        Decode and verify a JWT access token.

        :param token: str
            The JWT token string to decode.
        :raises UnauthorizedError:
            If the token does not contain a subject ("sub").
        :raises InternalServerError:
            If decoding fails due to an invalid token or other JWT errors.
        :return: dict
            The decoded JWT payload.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if "sub" not in payload:
                raise UnauthorizedError("Token missing subject")
            return payload
        except JWTError as e:
            raise InternalServerError(log_message=e)


class AuthService:
    """
    Service responsible for user authentication and retrieval from JWT tokens.

    Attributes:
        token_service (TokenService): Service for token creation and decoding.
        user_repo (UserRepository): Repository for user data access.
    """

    def __init__(self, token_service: TokenService, user_repo: UserRepository):
        """
        Initialize AuthService with token handling and user repository.

        :param token_service: TokenService
            Instance to handle token encoding and decoding.
        :param user_repo: UserRepository
            Repository to fetch user data from database.
        """
        self.token_service = token_service
        self.user_repo = user_repo

    async def get_current_user(self, authorization: str) -> UserRead:
        """
        Extract and return the current authenticated user based on the Authorization header.

        :param authorization: str
            The 'Authorization' header value, expected to start with "Bearer ".
        :raises UnauthorizedError:
            If the token is invalid, missing, malformed, or user does not exist.
        :return: UserRead
            The authenticated user's data.
        """
        if not authorization.startswith("Bearer "):
            raise UnauthorizedError

        token = authorization[7:]
        payload = self.token_service.decode_access_token(token)
        user_id_str = payload.get("sub")

        try:
            user_id = int(user_id_str)
        except ValueError:
            raise UnauthorizedError

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise UnauthorizedError

        return UserRead.from_orm(user)
