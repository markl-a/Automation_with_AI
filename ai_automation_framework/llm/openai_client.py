"""OpenAI client implementation."""

from typing import List, Optional, AsyncIterator
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
        **kwargs
    ):
        """
        Initialize OpenAI client.

        Args:
            model: Model name (default: from config)
            api_key: OpenAI API key (default: from config)
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

    def _messages_to_openai_format(self, messages: List[Message]) -> List[dict]:
        """Convert Message objects to OpenAI format."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

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

        except openai.RateLimitError as e:
            self.logger.error(f"OpenAI rate limit exceeded: {e}")
            raise RuntimeError(f"Rate limit exceeded: {e}") from e
        except openai.AuthenticationError as e:
            self.logger.error(f"OpenAI authentication failed: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"API error: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error calling OpenAI: {e}")
            raise RuntimeError(f"Failed to get OpenAI response: {e}") from e

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

        except openai.RateLimitError as e:
            self.logger.error(f"OpenAI rate limit exceeded: {e}")
            raise RuntimeError(f"Rate limit exceeded: {e}") from e
        except openai.AuthenticationError as e:
            self.logger.error(f"OpenAI authentication failed: {e}")
            raise RuntimeError(f"Authentication failed: {e}") from e
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"API error: {e}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error calling OpenAI: {e}")
            raise RuntimeError(f"Failed to get OpenAI response: {e}") from e

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
