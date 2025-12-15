"""Anthropic Claude client implementation."""

from typing import List, Optional, AsyncIterator
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
        **kwargs
    ):
        """
        Initialize Anthropic client.

        Args:
            model: Model name (default: claude-3-5-sonnet-20241022)
            api_key: Anthropic API key (default: from config)
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
        except anthropic.RateLimitError as e:
            self.logger.error(f"Anthropic rate limit exceeded: {e}")
            raise RuntimeError(f"Rate limit exceeded: {e}") from e
        except anthropic.AuthenticationError as e:
            self.logger.error(f"Anthropic authentication failed: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise RuntimeError(f"API error: {e}") from e

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
        except anthropic.RateLimitError as e:
            self.logger.error(f"Anthropic rate limit exceeded: {e}")
            raise RuntimeError(f"Rate limit exceeded: {e}") from e
        except anthropic.AuthenticationError as e:
            self.logger.error(f"Anthropic authentication failed: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise RuntimeError(f"API error: {e}") from e

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
