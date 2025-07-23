import logging
from typing import Any
from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


class BaseAPIException(HTTPException):
    """
    Base exception class for API errors, extending FastAPI's HTTPException.

    Logs an error message upon initialization.

    :param status_code: int, optional
        HTTP status code to return (default is 500 Internal Server Error).
    :param detail: str, optional
        Error detail message to include in the HTTP response.
    :param headers: dict[str, Any] | None, optional
         HTTP headers to include in the response.
    :param log_message: str | Exception | None, optional
        Message or exception to be logged. If an Exception is passed, logs with traceback.
    """

    def __init__(
        self,
        *,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Internal server error",
        headers: dict[str, Any] | None = None,
        log_message: str | Exception | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        if isinstance(log_message, Exception):
            logger.error(f"{self.__class__.__name__}: {detail}", exc_info=log_message)
        else:
            logger.error(f"{self.__class__.__name__}: {log_message or detail}")


def create_exception_class(name: str, status_code: int, detail_template: str):
    """
    Dynamically create a new exception class inheriting from BaseAPIException.

    The generated exception class formats the detail message using the provided template.

    :param name: str
        Name of the new exception class.
    :param status_code: int
        HTTP status code that the exception will use.
    :param detail_template: str
        A format string used to create the exception detail message.
    :return: type
        A new exception class ready to be raised with formatted detail.
    """
    return type(
        name,
        (BaseAPIException,),
        {
            "__init__": lambda self, *args, log_message=None: BaseAPIException.__init__(
                self,
                status_code=status_code,
                detail=detail_template.format(*args),
                log_message=log_message,
            )
        },
    )


UserNotFoundError = create_exception_class(
    "UserNotFoundError",
    status.HTTP_404_NOT_FOUND,
    "User with id {} not found.",
)

UserExistedError = create_exception_class(
    "UserExistedError",
    status.HTTP_409_CONFLICT,
    "User with this mail already exists.",
)

CourseNotFoundError = create_exception_class(
    "CourseNotFoundError",
    status.HTTP_404_NOT_FOUND,
    "Course with id {} not found.",
)

SummaryEmptyError = create_exception_class(
    "SummaryEmptyError",
    status.HTTP_422_UNPROCESSABLE_ENTITY,
    "Summary for course with id {} is empty.",
)

OpenAIServerError = create_exception_class(
    "OpenAIServerError",
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "OpenAI server error.",
)

InternalServerError = create_exception_class(
    "InternalServerError",
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "Internal server error.",
)

OpenAIRateLimitError = create_exception_class(
    "OpenAIRateLimitError",
    status.HTTP_429_TOO_MANY_REQUESTS,
    "Rate limit exceeded: max {} requests per {} hours.",
)

SQLSessionError = create_exception_class(
    "SQLSessionError",
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "Internal server error",
)

GeneralSQLSessionError = create_exception_class(
    "GeneralSQLSessionError",
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    "Internal server error",
)

CeleryTaskNotFoundError = create_exception_class(
    "CeleryTaskNotFoundError",
    status.HTTP_404_NOT_FOUND,
    "Celery task ID {} not found in system.",
)
UnauthorizedError = create_exception_class(
    "UnauthorizedError",
    status.HTTP_401_UNAUTHORIZED,
    "Wrong authentication token.",
)

UserForbiddenError = create_exception_class(
    "UserForbiddenError",
    status.HTTP_403_FORBIDDEN,
    "Forbidden for user {}.",
)
