"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    llm_provider: str = Field(default="gemini", env="LLM_PROVIDER")
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")

    # Neo4j Configuration
    neo4j_uri: str = Field(default="bolt://neo4j:7687", env="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", env="NEO4J_USERNAME")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")

    # ChromaDB Configuration
    chroma_persist_dir: str = Field(default="./chroma_data", env="CHROMA_PERSIST_DIR")

    # API Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        env="CORS_ORIGINS",
    )
    app_name: str = Field(default="AgentGraph Intel", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Module-level singleton
settings = Settings()
