"""Configuration management for the AI Automation Framework."""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict


class Config(BaseModel):
    """
    Configuration class for AI Automation Framework.

    Loads configuration from environment variables and provides
    a centralized way to access settings.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    cohere_api_key: Optional[str] = Field(default=None, description="Cohere API key")

    # Model Configuration
    default_model: str = Field(default="gpt-4o", description="Default LLM model")
    default_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Default embedding model"
    )
    max_tokens: int = Field(default=4096, description="Maximum tokens for generation")
    temperature: float = Field(default=0.7, description="Temperature for generation")

    # Vector Database
    chroma_persist_directory: str = Field(
        default="./data/chroma",
        description="ChromaDB persistence directory"
    )
    vector_db_type: str = Field(default="chroma", description="Vector database type")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="./logs/ai_automation.log", description="Log file path")

    # Paths
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    logs_dir: Path = Field(default=Path("./logs"), description="Logs directory")

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """
        Load configuration from environment variables.

        Args:
            env_file: Path to .env file. If None, uses default .env

        Returns:
            Config instance
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            cohere_api_key=os.getenv("COHERE_API_KEY"),
            default_model=os.getenv("DEFAULT_MODEL", "gpt-4o"),
            default_embedding_model=os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-3-small"),
            max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            chroma_persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma"),
            vector_db_type=os.getenv("VECTOR_DB_TYPE", "chroma"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "./logs/ai_automation.log"),
        )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        Path(self.chroma_persist_directory).parent.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.model_dump()


# Global config instance
_config: Optional[Config] = None


def get_config(env_file: Optional[str] = None) -> Config:
    """
    Get or create global config instance.

    Args:
        env_file: Path to .env file

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config.from_env(env_file)
        _config.ensure_directories()
    return _config
