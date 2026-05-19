"""Memory management for Fred AI."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class ConversationMemory:
    """Stores and manages conversation history."""

    def __init__(self, max_history: int = 50, storage_path: Optional[str] = None):
        """Initialize conversation memory.
        
        Args:
            max_history: Maximum number of messages to keep in memory
            storage_path: Path to persist conversations. Defaults to ~/.fred_ai/conversations/
        """
        self.max_history = max_history
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".fred_ai" / "conversations"
        
        self.messages: list[dict] = []
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.
        
        Args:
            role: The role of the message sender ('user' or 'assistant')
            content: The message content
        """
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim if exceeds max history
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def get_messages(self) -> list[dict]:
        """Get all messages in the conversation."""
        return self.messages

    def get_context_messages(self, n: Optional[int] = None) -> list[dict]:
        """Get messages formatted for LLM context.
        
        Args:
            n: Number of recent messages to return. None returns all.
        """
        messages = self.messages[-n:] if n else self.messages
        return [{"role": m["role"], "content": m["content"]} for m in messages]

    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages = []

    def save_conversation(self, name: Optional[str] = None) -> str:
        """Save the current conversation to a file.
        
        Args:
            name: Optional name for the conversation file
            
        Returns:
            Path to the saved file
        """
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"conversation_{timestamp}"
        
        filepath = self.storage_path / f"{name}.json"
        with open(filepath, "w") as f:
            json.dump(self.messages, f, indent=2)
        
        return str(filepath)

    def load_conversation(self, name: str) -> bool:
        """Load a conversation from a file.
        
        Args:
            name: Name of the conversation file (without .json extension)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        filepath = self.storage_path / f"{name}.json"
        if not filepath.exists():
            return False
        
        try:
            with open(filepath, "r") as f:
                self.messages = json.load(f)
            return True
        except (json.JSONDecodeError, IOError):
            return False
