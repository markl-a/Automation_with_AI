"""OpenAI client implementation."""

from typing import List, Optional, AsyncIterator
import time
import random
import asyncio
from openai import OpenAI, AsyncOpenAI
import openai
from ai_automation_framework.llm.base_client import BaseLLMClient
from ai_automation_framework.core.base import Message, Response
from ai_automation_framework.core.config import get_config


class OpenAIClient(BaseLLMClient):
    """
    OpenAI client implementation.

    Supports GPT-4, GPT-4o, GPT-3.5-turbo and other OpenAI models.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        **kwargs
    ):
        """
        Initialize OpenAI client.

        Args:
            model: Model name (default: from config)
            api_key: OpenAI API key (default: from config)
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for exponential backoff (default: 1.0)
            **kwargs: Additional configuration
        """
        config = get_config()
        model = model or config.default_model
        api_key = api_key or config.openai_api_key

        super().__init__(
            model=model,
            api_key=api_key,
            name="OpenAIClient",
            **kwargs
        )

        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.max_retries = max_retries
        self.base_delay = base_delay

    def _messages_to_openai_format(self, messages: List[Message]) -> List[dict]:
        """Convert Message objects to OpenAI format."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable."""
        if isinstance(error, openai.RateLimitError):
            return True
        if isinstance(error, openai.APIError):
            # Retry on server errors and connection issues
            if hasattr(error, 'status_code'):
                return error.status_code >= 500
            return True
        # Don't retry authentication errors
        if isinstance(error, openai.AuthenticationError):
            return False
        return False

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = self.base_delay * (2 ** attempt)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter

    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Response:
        """
        Send a chat completion request to OpenAI.

        Args:
            messages: List of messages
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters

        Returns:
            Response object

        Raises:
            RuntimeError: If API call fails
        """
        self.initialize()

        openai_messages = self._messages_to_openai_format(messages)
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                    **kwargs
                )

                # Validate response
                if not response.choices or not response.choices[0].message.content:
                    self.logger.warning("Empty response from OpenAI API")
                    content = ""
                else:
                    content = response.choices[0].message.content

                # Handle usage safely
                usage = None
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }

                return Response(
                    content=content,
                    role="assistant",
                    model=response.model,
                    usage=usage,
                    finish_reason=response.choices[0].finish_reason if response.choices else None,
                    tool_calls=getattr(response.choices[0].message, 'tool_calls', None) if response.choices else None,
                )

            except openai.AuthenticationError as e:
                # Don't retry authentication errors
                self.logger.error(f"OpenAI authentication failed: {e}")
                raise RuntimeError(f"Authentication failed: {e}") from e
            except (openai.RateLimitError, openai.APIError) as e:
                last_error = e
                if attempt < self.max_retries and self._is_retryable_error(e):
                    delay = self._calculate_backoff_delay(attempt)
                    self.logger.warning(
                        f"OpenAI API error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    error_type = type(e).__name__
                    self.logger.error(f"OpenAI {error_type}: {e}")
                    raise RuntimeError(f"{error_type}: {e}") from e
            except Exception as e:
                self.logger.error(f"Unexpected error calling OpenAI: {e}")
                raise RuntimeError(f"Failed to get OpenAI response: {e}") from e

        # If we exhausted all retries
        if last_error:
            error_type = type(last_error).__name__
            self.logger.error(f"OpenAI {error_type} after {self.max_retries + 1} attempts: {last_error}")
            raise RuntimeError(f"{error_type} after {self.max_retries + 1} attempts: {last_error}") from last_error

    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Response:
        """
        Async version of chat.

        Args:
            messages: List of messages
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters

        Returns:
            Response object

        Raises:
            RuntimeError: If API call fails
        """
        self.initialize()

        openai_messages = self._messages_to_openai_format(messages)
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                    **kwargs
                )

                # Validate response
                if not response.choices or not response.choices[0].message.content:
                    self.logger.warning("Empty response from OpenAI API")
                    content = ""
                else:
                    content = response.choices[0].message.content

                # Handle usage safely
                usage = None
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }

                return Response(
                    content=content,
                    role="assistant",
                    model=response.model,
                    usage=usage,
                    finish_reason=response.choices[0].finish_reason if response.choices else None,
                    tool_calls=getattr(response.choices[0].message, 'tool_calls', None) if response.choices else None,
                )

            except openai.AuthenticationError as e:
                # Don't retry authentication errors
                self.logger.error(f"OpenAI authentication failed: {e}")
                raise RuntimeError(f"Authentication failed: {e}") from e
            except (openai.RateLimitError, openai.APIError) as e:
                last_error = e
                if attempt < self.max_retries and self._is_retryable_error(e):
                    delay = self._calculate_backoff_delay(attempt)
                    self.logger.warning(
                        f"OpenAI API error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    error_type = type(e).__name__
                    self.logger.error(f"OpenAI {error_type}: {e}")
                    raise RuntimeError(f"{error_type}: {e}") from e
            except Exception as e:
                self.logger.error(f"Unexpected error calling OpenAI: {e}")
                raise RuntimeError(f"Failed to get OpenAI response: {e}") from e

        # If we exhausted all retries
        if last_error:
            error_type = type(last_error).__name__
            self.logger.error(f"OpenAI {error_type} after {self.max_retries + 1} attempts: {last_error}")
            raise RuntimeError(f"{error_type} after {self.max_retries + 1} attempts: {last_error}") from last_error

    async def stream_chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion from OpenAI.

        Args:
            messages: List of messages
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        self.initialize()

        openai_messages = self._messages_to_openai_format(messages)

        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except openai.RateLimitError as e:
            self.logger.error(f"OpenAI rate limit exceeded during stream: {e}")
            raise RuntimeError(f"Rate limit exceeded: {e}") from e
        except openai.AuthenticationError as e:
            self.logger.error(f"OpenAI authentication failed during stream: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error during stream: {e}")
            raise RuntimeError(f"API error: {e}") from e
