"""Anthropic Claude client implementation."""

from typing import List, Optional, AsyncIterator
import time
import random
import asyncio
import anthropic
from anthropic import Anthropic, AsyncAnthropic
from ai_automation_framework.llm.base_client import BaseLLMClient
from ai_automation_framework.core.base import Message, Response
from ai_automation_framework.core.config import get_config


class AnthropicClient(BaseLLMClient):
    """
    Anthropic Claude client implementation.

    Supports Claude 3.5 Sonnet, Claude 3 Opus, and other Claude models.
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        **kwargs
    ):
        """
        Initialize Anthropic client.

        Args:
            model: Model name (default: claude-3-5-sonnet-20241022)
            api_key: Anthropic API key (default: from config)
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for exponential backoff (default: 1.0)
            **kwargs: Additional configuration
        """
        config = get_config()
        api_key = api_key or config.anthropic_api_key

        super().__init__(
            model=model,
            api_key=api_key,
            name="AnthropicClient",
            **kwargs
        )

        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)
        self.max_retries = max_retries
        self.base_delay = base_delay

    def _messages_to_anthropic_format(self, messages: List[Message]) -> tuple:
        """
        Convert Message objects to Anthropic format.

        Returns:
            Tuple of (system_message, messages)
        """
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return system_message, anthropic_messages

    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable."""
        if isinstance(error, anthropic.RateLimitError):
            return True
        if isinstance(error, anthropic.APIError):
            # Retry on server errors and connection issues
            if hasattr(error, 'status_code'):
                return error.status_code >= 500
            return True
        # Don't retry authentication errors
        if isinstance(error, anthropic.AuthenticationError):
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
        Send a chat completion request to Anthropic.

        Args:
            messages: List of messages
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters

        Returns:
            Response object
        """
        self.initialize()

        system_message, anthropic_messages = self._messages_to_anthropic_format(messages)

        params = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }

        if system_message:
            params["system"] = system_message

        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.messages.create(**params)

                # Safely access content
                content = ""
                if response.content and len(response.content) > 0:
                    content = response.content[0].text
                else:
                    self.logger.warning("Empty response from Anthropic API")

                return Response(
                    content=content,
                    role="assistant",
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                    },
                    finish_reason=response.stop_reason,
                )
            except anthropic.AuthenticationError as e:
                # Don't retry authentication errors
                self.logger.error(f"Anthropic authentication failed: {e}")
                raise RuntimeError(f"Authentication failed: {e}") from e
            except (anthropic.RateLimitError, anthropic.APIError) as e:
                last_error = e
                if attempt < self.max_retries and self._is_retryable_error(e):
                    delay = self._calculate_backoff_delay(attempt)
                    self.logger.warning(
                        f"Anthropic API error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    error_type = type(e).__name__
                    self.logger.error(f"Anthropic {error_type}: {e}")
                    raise RuntimeError(f"{error_type}: {e}") from e

        # If we exhausted all retries
        if last_error:
            error_type = type(last_error).__name__
            self.logger.error(f"Anthropic {error_type} after {self.max_retries + 1} attempts: {last_error}")
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
        """
        self.initialize()

        system_message, anthropic_messages = self._messages_to_anthropic_format(messages)

        params = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }

        if system_message:
            params["system"] = system_message

        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.async_client.messages.create(**params)

                # Safely access content
                content = ""
                if response.content and len(response.content) > 0:
                    content = response.content[0].text
                else:
                    self.logger.warning("Empty response from Anthropic API")

                return Response(
                    content=content,
                    role="assistant",
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                    },
                    finish_reason=response.stop_reason,
                )
            except anthropic.AuthenticationError as e:
                # Don't retry authentication errors
                self.logger.error(f"Anthropic authentication failed: {e}")
                raise RuntimeError(f"Authentication failed: {e}") from e
            except (anthropic.RateLimitError, anthropic.APIError) as e:
                last_error = e
                if attempt < self.max_retries and self._is_retryable_error(e):
                    delay = self._calculate_backoff_delay(attempt)
                    self.logger.warning(
                        f"Anthropic API error (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    error_type = type(e).__name__
                    self.logger.error(f"Anthropic {error_type}: {e}")
                    raise RuntimeError(f"{error_type}: {e}") from e

        # If we exhausted all retries
        if last_error:
            error_type = type(last_error).__name__
            self.logger.error(f"Anthropic {error_type} after {self.max_retries + 1} attempts: {last_error}")
            raise RuntimeError(f"{error_type} after {self.max_retries + 1} attempts: {last_error}") from last_error

    async def stream_chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion from Anthropic.

        Args:
            messages: List of messages
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        self.initialize()

        system_message, anthropic_messages = self._messages_to_anthropic_format(messages)

        params = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }

        if system_message:
            params["system"] = system_message

        try:
            async with self.async_client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.RateLimitError as e:
            self.logger.error(f"Anthropic rate limit exceeded during stream: {e}")
            raise RuntimeError(f"Rate limit exceeded: {e}") from e
        except anthropic.AuthenticationError as e:
            self.logger.error(f"Anthropic authentication failed during stream: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error during stream: {e}")
            raise RuntimeError(f"API error: {e}") from e
