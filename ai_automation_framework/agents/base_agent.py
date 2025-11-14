"""Base agent implementation."""

from typing import List, Dict, Any, Optional
from abc import abstractmethod
from ai_automation_framework.core.base import BaseComponent, Message, Response
from ai_automation_framework.llm import BaseLLMClient, OpenAIClient


class BaseAgent(BaseComponent):
    """
    Base class for AI agents.

    An agent combines an LLM with memory, tools, and decision-making capabilities.
    """

    def __init__(
        self,
        name: str = "Agent",
        llm: Optional[BaseLLMClient] = None,
        system_message: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the agent.

        Args:
            name: Agent name
            llm: LLM client
            system_message: System message defining agent's role
            **kwargs: Additional configuration
        """
        super().__init__(name=name, **kwargs)
        self.llm = llm or OpenAIClient()
        self.system_message = system_message
        self.memory: List[Message] = []

        if system_message:
            self.memory.append(Message(role="system", content=system_message))

    def _initialize(self) -> None:
        """Initialize the agent."""
        self.llm.initialize()
        self.logger.info(f"Initialized agent: {self.name}")

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to memory.

        Args:
            role: Message role
            content: Message content
        """
        self.memory.append(Message(role=role, content=content))

    def get_memory(self) -> List[Message]:
        """
        Get conversation memory.

        Returns:
            List of messages
        """
        return self.memory.copy()

    def clear_memory(self, keep_system: bool = True) -> None:
        """
        Clear conversation memory.

        Args:
            keep_system: Whether to keep system message
        """
        if keep_system and self.system_message:
            self.memory = [Message(role="system", content=self.system_message)]
        else:
            self.memory = []

    def chat(self, user_message: str, **kwargs) -> str:
        """
        Chat with the agent.

        Args:
            user_message: User's message
            **kwargs: Additional parameters for LLM

        Returns:
            Agent's response
        """
        self.initialize()

        # Add user message to memory
        self.add_message("user", user_message)

        # Get response from LLM
        response = self.llm.chat(self.memory, **kwargs)

        # Add assistant response to memory
        self.add_message("assistant", response.content)

        return response.content

    @abstractmethod
    def run(self, task: str, **kwargs) -> Any:
        """
        Run the agent on a task.

        Args:
            task: Task description
            **kwargs: Additional parameters

        Returns:
            Task result
        """
        pass

    def __call__(self, task: str, **kwargs) -> Any:
        """Make agent callable."""
        return self.run(task, **kwargs)
