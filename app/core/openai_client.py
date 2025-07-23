from openai import (
    AsyncOpenAI,
    APIStatusError,
    RateLimitError,
)
from app.core.config import settings
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)


from app.core.exceptions import (
    OpenAIServerError,
    InternalServerError,
    OpenAIRateLimitError,
)


class OpenAISummarizer:
    """
    Wrapper class for asynchronous interaction with OpenAI API to generate course summaries.

    Uses retry logic with exponential backoff for handling rate limits and internal server errors.

    Attributes:
        client (AsyncOpenAI): An asynchronous OpenAI API client initialized with the API key.
    """

    def __init__(self):
        """
        Initialize the OpenAISummarizer with an AsyncOpenAI client using the configured API key.
        """
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @retry(
        wait=wait_exponential(min=5, max=15),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, InternalServerError)),
    )
    async def generate_summary(self, prompt: str, model: str = "gpt-4") -> str:
        """
        Generate a summary of the given prompt using OpenAI's chat completion endpoint.

        Retries automatically on rate limiting or internal server errors up to 3 attempts with exponential backoff.

        :param prompt: str
            The text content (e.g. course description) to summarize.
        :param model: str, optional
            The OpenAI model to use for generation (default is "gpt-4").
        :return: str
            The summarized text returned from the OpenAI completion.
        :raises OpenAIRateLimitError:
            Raised when OpenAI API rate limits are exceeded.
        :raises OpenAIServerError:
            Raised when the OpenAI API returns an internal server error.
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this online course: {prompt}",
                    }
                ],
                timeout=30,
            )

            return response.choices[0].message.content.strip()

        except RateLimitError as e:
            raise OpenAIRateLimitError(log_message=e)
        except APIStatusError as e:
            raise OpenAIServerError(log_message=e)
        # except Exception as e:
        #     raise InternalServerError(log_message=e)


openai_summarizer = OpenAISummarizer()
