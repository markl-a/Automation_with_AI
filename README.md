# 🤖 AI Automation Framework

A comprehensive, production-ready framework for LLM and AI automation - from basics to advanced. Built with modern best practices and designed for both learning and real-world applications.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🎯 Progressive Learning Path

**Level 1 - Basics** (Start Here!)
- Simple LLM API integration
- Prompt engineering fundamentals
- Text processing automation
- Streaming responses

**Level 2 - Intermediate**
- RAG (Retrieval-Augmented Generation)
- Function calling and tool use
- Workflow automation
- Chain processing
- Vector databases

**Level 3 - Advanced**
- Multi-agent systems
- Autonomous agents
- Complex task planning
- Agent collaboration patterns

### 🛠️ Core Components

- **LLM Clients**: Unified interface for OpenAI, Anthropic Claude, and more
- **RAG System**: Complete implementation with embeddings and vector stores
- **Agent Framework**: Base classes for building intelligent agents
- **Workflow Engine**: Chain and pipeline processing
- **Plugin System**: Extensible architecture
- **Production Ready**: Logging, configuration management, error handling

### 🌟 Highlights

- **2025 Best Practices**: Built using latest AI frameworks and patterns
- **Well Documented**: Extensive examples and documentation
- **Type Safe**: Full type hints with Pydantic models
- **Async Support**: Non-blocking operations for performance
- **Flexible**: Easy to extend and customize
- **Practical**: Real-world examples and demo applications

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Documentation](#documentation)
- [Framework Architecture](#framework-architecture)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (for OpenAI models)
- Anthropic API key (optional, for Claude models)

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Automation_with_AI.git
cd Automation_with_AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
```

## 🎓 Quick Start

### Simple Chat Example

```python
from ai_automation_framework.llm import OpenAIClient

# Create a client
client = OpenAIClient()

# Simple chat
response = client.simple_chat("Explain AI in simple terms")
print(response)
```

### RAG Example

```python
from ai_automation_framework.rag import Retriever
from ai_automation_framework.llm import OpenAIClient

# Create retriever
retriever = Retriever()

# Add documents
documents = [
    "Paris is the capital of France.",
    "London is the capital of England.",
    "Berlin is the capital of Germany."
]
retriever.add_documents(documents)

# Query with RAG
query = "What is the capital of France?"
context = retriever.get_context_string(query)

# Generate answer
client = OpenAIClient()
prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
answer = client.simple_chat(prompt)
print(answer)
```

### Agent Example

```python
from ai_automation_framework.agents import BaseAgent

# Create an agent
agent = BaseAgent(
    name="Assistant",
    system_message="You are a helpful AI assistant."
)

# Chat with the agent
response = agent.chat("Hello! Can you help me with Python?")
print(response)
```

## 📚 Examples

### Level 1 - Basics

Run the examples:

```bash
# Simple chat
python examples/level1_basics/01_simple_chat.py

# Prompt engineering
python examples/level1_basics/02_prompt_engineering.py

# Text processing
python examples/level1_basics/03_text_processing.py

# Streaming responses
python examples/level1_basics/04_streaming_responses.py
```

### Level 2 - Intermediate

```bash
# RAG basics
python examples/level2_intermediate/01_rag_basic.py

# Function calling
python examples/level2_intermediate/02_function_calling.py
```

### Level 3 - Advanced

```bash
# Multi-agent systems
python examples/level3_advanced/01_multi_agent.py
```

## 📖 Documentation

Detailed documentation is available in the `docs/` directory.

## 🏗️ Framework Architecture

```
ai_automation_framework/
├── core/              # Core components (config, logging, base classes)
├── llm/               # LLM client implementations
├── rag/               # RAG components (embeddings, vector stores, retrieval)
├── agents/            # Agent implementations
├── tools/             # Tool implementations for agents
├── workflows/         # Workflow orchestration (chains, pipelines)
└── plugins/           # Plugin system
```

### Key Design Principles

1. **Modularity**: Each component is independent and composable
2. **Extensibility**: Easy to add new LLM providers, tools, and agents
3. **Type Safety**: Full type hints for better IDE support
4. **Production Ready**: Proper logging, error handling, and configuration
5. **Best Practices**: Following 2025 AI framework patterns

## 🎯 Use Cases

This framework is perfect for:

- **Learning**: Progress from basics to advanced AI concepts
- **Prototyping**: Quickly build AI-powered applications
- **Production**: Deploy scalable AI automation solutions
- **Research**: Experiment with agents and workflows
- **Integration**: Add AI capabilities to existing applications

## 🔧 Advanced Features

### Custom LLM Provider

```python
from ai_automation_framework.llm.base_client import BaseLLMClient

class MyCustomClient(BaseLLMClient):
    def chat(self, messages, **kwargs):
        # Your implementation
        pass
```

### Custom Agent

```python
from ai_automation_framework.agents import BaseAgent

class MyAgent(BaseAgent):
    def run(self, task, **kwargs):
        # Your agent logic
        pass
```

### Custom Tool

```python
def my_tool(param1: str, param2: int) -> dict:
    """Your tool implementation."""
    return {"result": "success"}

# Register with agent
agent.register_tool("my_tool", my_tool, schema={...})
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This framework is built using modern AI technologies and best practices from:

- OpenAI GPT models
- Anthropic Claude models
- LangChain framework
- ChromaDB vector database
- And many other open-source projects

## 🗺️ Roadmap

- [x] Core framework implementation
- [x] Level 1-3 examples
- [ ] More demo applications
- [ ] Web UI with Streamlit
- [ ] Integration with more LLM providers
- [ ] Advanced agent patterns
- [ ] Comprehensive test suite

---

**Built with ❤️ for the AI community**