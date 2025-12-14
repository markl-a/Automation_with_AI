"""Base classes for the AI Automation Framework."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from ai_automation_framework.core.logger import get_logger


class BaseComponent(ABC):
    """
    Base class for all framework components.

    Provides common functionality like logging, configuration, and lifecycle management.
    """

    def __init__(self, name: Optional[str] = None, **kwargs):
        """
        Initialize the component.

        Args:
            name: Component name
            **kwargs: Additional configuration
        """
        self.name = name or self.__class__.__name__
        self.logger = get_logger(self.name)
        self.config = kwargs
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the component."""
        if not self._initialized:
            self.logger.info(f"Initializing {self.name}")
            self._initialize()
            self._initialized = True

    @abstractmethod
    def _initialize(self) -> None:
        """Component-specific initialization logic."""
        pass

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self._initialized:
            self.logger.info(f"Cleaning up {self.name}")
            self._cleanup()
            self._initialized = False

    def _cleanup(self) -> None:
        """Component-specific cleanup logic."""
        pass

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class Message(BaseModel):
    """Represents a message in a conversation."""

    role: str  # "system", "user", "assistant", "function"
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class Response(BaseModel):
    """Represents a response from an LLM or agent."""

    content: str
    role: str = "assistant"
    model: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tool_calls: Optional[Any] = None  # For function/tool calling support

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
