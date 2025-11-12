from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml


class Config(BaseSettings):
    # Paths
    data_dir: Path = Field(default=Path.home() / ".temporal-kb" / "data")
    config_dir: Path = Field(default=Path.home() / ".temporal-kb" / "config")

    # Database
    db_path: Optional[Path] = None
    postgres_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection string (if using PostgreSQL instead of SQLite)",
    )

    # File storage
    entries_dir: Optional[Path] = None

    # Vector store
    vector_db_path: Optional[Path] = None
    embedding_model: str = "all-MiniLM-L6-v2"

    # Git
    git_enabled: bool = True
    git_auto_commit: bool = True
    git_remote: Optional[str] = None

    # Encryption
    encryption_enabled: bool = False
    master_key_path: Optional[Path] = None

    # Search
    fts_enabled: bool = True
    semantic_search_enabled: bool = True

    # API
    api_host: str = "localhost"
    api_port: int = 8000
    api_cors_origins: List[str] = ["http://localhost:3000"]

    # Security
    api_keys: List[str] = Field(default_factory=list)
    jwt_secret: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    # Note: postgres_url and api_keys already defined above

    class Config:
        env_prefix = "KB_"
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set derived paths
        if self.db_path is None:
            self.db_path = self.data_dir / "db" / "kb.db"
        if self.entries_dir is None:
            self.entries_dir = self.data_dir / "entries"
        if self.vector_db_path is None:
            self.vector_db_path = self.data_dir / "vectors"

        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.entries_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        """Load configuration from YAML file"""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path):
        """Save configuration to YAML file"""
        data = self.model_dump(exclude_none=True)
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


# Global config instance
_config: Optional[Config] = None


def init_config(config_path: Optional[Path] = None) -> Config:
    """Initialize configuration"""
    global _config

    if config_path and config_path.exists():
        _config = Config.from_yaml(config_path)
    else:
        _config = Config()
        # Save default config
        default_config_path = _config.config_dir / "config.yaml"
        _config.to_yaml(default_config_path)

    return _config


def get_config() -> Config:
    """Get the global configuration instance"""
    if _config is None:
        return init_config()
    return _config
