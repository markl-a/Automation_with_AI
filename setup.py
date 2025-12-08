from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-automation-framework",
    version="0.1.0",
    author="AI Automation Framework Contributors",
    description="A comprehensive framework for LLM and AI automation from basics to advanced",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markl-a/Automation_with_AI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.50.0",
        "anthropic>=0.39.0",
        "langchain>=0.3.0",
        "chromadb>=0.5.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.9.0",
        "rich>=13.9.0",
        "loguru>=0.7.2",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "black>=24.8.0",
            "flake8>=7.1.0",
            "mypy>=1.11.0",
        ],
        "all": [
            "autogen-agentchat>=0.4.0",
            "crewai>=0.80.0",
            "streamlit>=1.39.0",
            "ollama>=0.3.0",
        ],
    },
)
