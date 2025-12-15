"""Multi-agent system implementation."""

from typing import List, Dict, Any, Optional
from ai_automation_framework.core.base import BaseComponent
from ai_automation_framework.agents.base_agent import BaseAgent


class MultiAgentSystem(BaseComponent):
    """
    Multi-agent system for collaborative problem solving.

    Coordinates multiple specialized agents to work together on complex tasks.
    """

    def __init__(
        self,
        name: str = "MultiAgentSystem",
        agents: Optional[Dict[str, BaseAgent]] = None,
        **kwargs
    ):
        """
        Initialize the multi-agent system.

        Args:
            name: System name
            agents: Dictionary of agent name -> agent instance
            **kwargs: Additional configuration
        """
        super().__init__(name=name, **kwargs)
        self.agents = {}
        self.conversation_history: List[Dict[str, Any]] = []

        # Validate and add agents
        if agents:
            for agent_name, agent in agents.items():
                if not isinstance(agent, BaseAgent):
                    raise TypeError(f"Agent '{agent_name}' must be an instance of BaseAgent, got {type(agent).__name__}")
                self.agents[agent_name] = agent

    def _initialize(self) -> None:
        """Initialize the system."""
        for agent in self.agents.values():
            agent.initialize()
        self.logger.info(f"Initialized MultiAgentSystem with {len(self.agents)} agents")

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """
        Register an agent in the system.

        Args:
            name: Agent name
            agent: Agent instance
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(f"Agent must be an instance of BaseAgent, got {type(agent).__name__}")
        self.agents[name] = agent
        self.logger.info(f"Registered agent: {name}")

    def get_agent(self, name: str) -> BaseAgent:
        """
        Get an agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance
        """
        if name not in self.agents:
            raise ValueError(f"Agent not found: {name}")
        return self.agents[name]

    def sequential_execution(
        self,
        task: str,
        agent_sequence: List[str]
    ) -> Dict[str, Any]:
        """
        Execute task sequentially through multiple agents.

        Args:
            task: Initial task
            agent_sequence: List of agent names in order

        Returns:
            Results from each agent
        """
        if not agent_sequence:
            raise ValueError("agent_sequence cannot be empty")

        self.initialize()

        results = {}
        current_input = task

        self.logger.info(f"Sequential execution: {' -> '.join(agent_sequence)}")

        for agent_name in agent_sequence:
            agent = self.get_agent(agent_name)
            self.logger.info(f"Executing with agent: {agent_name}")

            try:
                result = agent.run(current_input)
            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed: {e}")
                result = {"error": str(e), "agent": agent_name}

            results[agent_name] = result
            self.conversation_history.append({
                "agent": agent_name,
                "input": current_input,
                "output": result
            })

            # Use output as input for next agent
            if isinstance(result, dict) and "answer" in result:
                current_input = result["answer"]
            else:
                current_input = str(result)

        return results

    def collaborative_execution(
        self,
        task: str,
        coordinator_agent: str,
        worker_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Execute task with coordinator-worker pattern.

        Args:
            task: Task description
            coordinator_agent: Name of coordinator agent
            worker_agents: List of worker agent names

        Returns:
            Execution results
        """
        if not worker_agents:
            raise ValueError("worker_agents cannot be empty")

        self.initialize()

        coordinator = self.get_agent(coordinator_agent)
        self.logger.info(f"Collaborative execution coordinated by: {coordinator_agent}")

        # Coordinator plans the work
        planning_prompt = f"""
        Task: {task}

        Available workers: {', '.join(worker_agents)}

        Plan how to distribute this task among the available workers.
        For each worker, describe what they should do.
        """

        try:
            plan = coordinator.chat(planning_prompt)
            self.logger.info(f"Coordinator created plan")
        except Exception as e:
            self.logger.error(f"Coordinator planning failed: {e}")
            raise

        # Execute with workers
        worker_results = {}
        for worker_name in worker_agents:
            worker = self.get_agent(worker_name)

            worker_task = f"""
            Original task: {task}

            Coordinator's plan: {plan}

            Your role as {worker_name}: Execute your part of the plan.
            """

            try:
                result = worker.run(worker_task)
            except Exception as e:
                self.logger.error(f"Worker {worker_name} failed: {e}")
                result = {"error": str(e), "agent": worker_name}
            worker_results[worker_name] = result

            self.conversation_history.append({
                "agent": worker_name,
                "input": worker_task,
                "output": result
            })

        # Coordinator synthesizes results
        synthesis_prompt = f"""
        Task: {task}

        Worker results:
        {self._format_results(worker_results)}

        Synthesize these results into a final answer.
        """

        final_answer = coordinator.chat(synthesis_prompt)

        return {
            "plan": plan,
            "worker_results": worker_results,
            "final_answer": final_answer
        }

    def _format_results(self, results: Dict[str, Any]) -> str:
        """Format results for display."""
        formatted = []
        for agent_name, result in results.items():
            if isinstance(result, dict) and "answer" in result:
                formatted.append(f"{agent_name}: {result['answer']}")
            else:
                formatted.append(f"{agent_name}: {result}")
        return "\n\n".join(formatted)

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history.copy()

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        for agent in self.agents.values():
            agent.clear_memory()
