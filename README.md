# 🤖 AI Automation Framework

A comprehensive, production-ready framework for LLM and AI automation - from basics to advanced. Built with modern best practices and designed for both learning and real-world applications.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.5.0-green.svg)](https://github.com/markl-a/Automation_with_AI/releases)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

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

**Level 4 - Advanced Automation**
- 17+ production-ready automation tools
- Email, Database, Web Scraping
- Task Scheduling, API Testing
- Cloud Integration, DevOps
- External workflow integration (Zapier, n8n, Airflow)

**Level 5 - AI-Assisted Development**
- AI Code Reviewer (quality, security, performance)
- AI Debug Assistant
- AI Documentation Generator
- AI Test Generator
- AI Refactoring Assistant

### 🛠️ Core Components

- **LLM Clients**: Unified interface for OpenAI, Anthropic Claude, Ollama (local), and more
- **RAG System**: Complete implementation with embeddings and vector stores
- **Agent Framework**: Base classes for building intelligent agents
- **Workflow Engine**: Chain and pipeline processing
- **Tools Collection**: Pre-built tools for file ops, calculations, web search, etc.
- **Document Loaders**: Support for PDF, Word, Markdown, and text files
- **Usage Tracking**: Monitor token usage and costs across all LLM calls
- **Response Caching**: Intelligent caching to reduce costs and improve speed
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
- [Changelog](#changelog)
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

# Workflow automation
python examples/level2_intermediate/03_workflow_automation.py

# Document processing
python examples/level2_intermediate/04_document_processing.py
```

### Level 3 - Advanced

```bash
# Multi-agent systems
python examples/level3_advanced/01_multi_agent.py
```

### Level 4 - Advanced Automation

```bash
# Email automation
python examples/level4_advanced_automation/01_email_automation_example.py

# Database automation
python examples/level4_advanced_automation/02_database_automation_example.py

# Web scraping
python examples/level4_advanced_automation/03_web_scraping_example.py

# All features demo
python examples/level4_advanced_automation/07_all_features_demo.py
```

### Level 5 - AI-Assisted Development

```bash
# AI development tools demo
python examples/level5_ai_assisted_dev/ai_dev_tools_demo.py
```

### Competition & Projects

```bash
# Kaggle competition assistant
python examples/competitions/kaggle_assistant.py

# Hackathon quick starter
python examples/competitions/hackathon_starter.py

# Social media manager
python examples/real_world_projects/social_media_manager.py
```

### Interactive Demos

```bash
# Chatbot with memory
python examples/demos/chatbot_demo.py

# Document Q&A system
python examples/demos/document_qa_demo.py

# AI code assistant
python examples/demos/code_assistant_demo.py
```

## 📖 Documentation

Comprehensive documentation and learning resources:

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete setup and first steps
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[Learning Path](docs/LEARNING_PATH.md)** - 📚 從零基礎到精通的完整學習路徑（Level 0-5）
- **[Competition Projects](docs/COMPETITION_PROJECTS.md)** - 🏆 Kaggle 和 Hackathon 項目模板
- **[Practice Exercises](docs/PRACTICE_EXERCISES.md)** - 🎯 實戰練習題庫（50+ 練習題）
- **[Advanced Features](docs/ADVANCED_FEATURES.md)** - 17+ 高級自動化功能
- **[API Reference](docs/API_REFERENCE.md)** - Detailed API documentation
- **Examples** - See `examples/` directory for 30+ code samples

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

Contributions are welcome! We appreciate your help in making this project better.

Please read our [Contributing Guide](CONTRIBUTING.md) to learn about:
- Development environment setup
- Code style guidelines
- Commit message conventions
- Pull request process
- Testing requirements

For major changes, please open an issue first to discuss what you would like to change.

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
- [x] Interactive demo applications
- [x] Comprehensive test suite
- [x] Document loaders (PDF, Word, Markdown, Text)
- [x] Common tools collection
- [x] Local LLM support (Ollama)
- [x] Usage tracking and cost monitoring
- [x] Response caching system
- [x] Complete API documentation
- [x] Enterprise-grade infrastructure (DI, Circuit Breaker, Events, Plugins)
- [x] Workflow automation integrations (Temporal, Prefect, Celery)
- [ ] Web UI with Streamlit
- [ ] Integration with more LLM providers (Google Gemini, Cohere)
- [ ] Advanced RAG techniques (HyDE, MultiQuery, etc.)
- [ ] Agent memory persistence
- [ ] Production deployment guides

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

**Current Version**: 0.5.0

---

**Built with ❤️ for the AI community**