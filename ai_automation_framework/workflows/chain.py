"""Chain for sequential processing."""

from typing import List, Callable, Any, Dict, Optional
from ai_automation_framework.core.base import BaseComponent


class Chain(BaseComponent):
    """
    Chain for sequential processing of tasks.

    Each step in the chain receives the output of the previous step.
    """

    def __init__(self, steps: Optional[List[Callable]] = None, **kwargs):
        """
        Initialize the chain.

        Args:
            steps: List of processing steps (functions)
            **kwargs: Additional configuration
        """
        super().__init__(name="Chain", **kwargs)
        self.steps = steps or []

    def _initialize(self) -> None:
        """Initialize the chain."""
        self.logger.info(f"Initialized Chain with {len(self.steps)} steps")

    def add_step(self, step: Callable) -> "Chain":
        """
        Add a step to the chain.

        Args:
            step: Processing function

        Returns:
            Self for chaining
        """
        self.steps.append(step)
        return self

    def run(self, initial_input: Any) -> Any:
        """
        Run the chain with initial input.

        Args:
            initial_input: Initial input to the chain

        Returns:
            Final output after all steps
        """
        self.initialize()

        current_output = initial_input
        self.logger.info(f"Starting chain execution with {len(self.steps)} steps")

        for i, step in enumerate(self.steps, 1):
            self.logger.debug(f"Executing step {i}/{len(self.steps)}: {step.__name__}")
            current_output = step(current_output)

        self.logger.info("Chain execution completed")
        return current_output

    def __call__(self, initial_input: Any) -> Any:
        """Make chain callable."""
        return self.run(initial_input)
