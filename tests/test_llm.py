"""Tests for LLM clients."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ai_automation_framework.llm import OpenAIClient, AnthropicClient
from ai_automation_framework.core.base import Message, Response


class TestOpenAIClient:
    """Test OpenAI client."""

    def test_client_initialization(self):
        """Test client initialization."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            client = OpenAIClient(api_key="test_key")
            assert client.api_key == "test_key"
            assert client.model is not None

    def test_messages_conversion(self):
        """Test message format conversion."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            client = OpenAIClient(api_key="test_key")
            messages = [
                Message(role="user", content="Hello"),
                Message(role="assistant", content="Hi")
            ]
            openai_messages = client._messages_to_openai_format(messages)
            assert len(openai_messages) == 2
            assert openai_messages[0]["role"] == "user"
            assert openai_messages[0]["content"] == "Hello"


class TestAnthropicClient:
    """Test Anthropic client."""

    def test_client_initialization(self):
        """Test client initialization."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            client = AnthropicClient(api_key="test_key")
            assert client.api_key == "test_key"
            assert client.model is not None

    def test_messages_conversion(self):
        """Test message format conversion."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            client = AnthropicClient(api_key="test_key")
            messages = [
                Message(role="system", content="You are helpful"),
                Message(role="user", content="Hello")
            ]
            system, anthropic_messages = client._messages_to_anthropic_format(messages)
            assert system == "You are helpful"
            assert len(anthropic_messages) == 1
            assert anthropic_messages[0]["role"] == "user"
