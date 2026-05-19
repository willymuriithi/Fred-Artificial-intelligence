"""Configuration management for Fred AI."""

import json
import os
from pathlib import Path
from typing import Any, Optional


class Config:
    """Manages Fred AI configuration settings."""

    DEFAULT_CONFIG = {
        "api_key": "",
        "api_base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2048,
        "memory_enabled": True,
        "max_history": 50,
        "verbose": False,
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. Defaults to ~/.fred_ai/config.json
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".fred_ai" / "config.json"
        
        self._config: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config: {e}")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value

    @property
    def api_key(self) -> str:
        return self._config.get("api_key", "")

    @api_key.setter
    def api_key(self, value: str) -> None:
        self._config["api_key"] = value

    @property
    def model(self) -> str:
        return self._config.get("model", "gpt-4o-mini")

    @model.setter
    def model(self, value: str) -> None:
        self._config["model"] = value

    @property
    def verbose(self) -> bool:
        return self._config.get("verbose", False)

    @verbose.setter
    def verbose(self, value: bool) -> None:
        self._config["verbose"] = value
