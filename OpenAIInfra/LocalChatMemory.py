from collections import deque
from typing import List, Dict, Deque, Union


class ChatMemory:
    """Manages conversation history with configurable memory size."""

    def __init__(self, max_length: int = 10):
        if max_length < 0:
            raise ValueError("max_length must be non-negative")

        self.messages: Deque[Dict[str, str]] = deque(maxlen=max_length)
        self.token_count = 0

    def add_message(self, role: str, content: str) -> None:
        """Add a single message to memory."""
        if not role or not content:
            raise ValueError("Both 'role' and 'content' are required")

        if role not in ["user", "assistant", "system"]:
            raise ValueError("Role must be 'user', 'assistant', or 'system'")

        self.messages.append({"role": role, "content": content})
        # Rough token estimation (4 chars ≈ 1 token)
        self.token_count += len(content) // 4

    def add_messages(self, messages: List[Dict[str, str]]) -> None:
        """Add multiple messages to memory."""
        if not messages:
            raise ValueError("Messages list cannot be empty")

        for message in messages:
            if not message.get("role") or not message.get("content"):
                raise ValueError("Each message must have 'role' and 'content'")
            self.add_message(message["role"], message["content"])

    def get_messages(self) -> List[Dict[str, str]]:
        """Return all stored messages as a list."""
        return list(self.messages)

    def get_last_message(self) -> Dict[str, str]:
        """Get the most recent message."""
        if not self.messages:
            raise ValueError("No messages in memory")
        return self.messages[-1]

    def get_messages_by_role(self, role: str) -> List[Dict[str, str]]:
        """Get all messages from a specific role."""
        return [msg for msg in self.messages if msg["role"] == role]

    def clear(self) -> None:
        """Clear all stored messages."""
        self.messages.clear()
        self.token_count = 0

    def get_token_estimate(self) -> int:
        """Get rough token count estimate."""
        return self.token_count

    def get_memory_stats(self) -> Dict[str, Union[int, List]]:
        """Get comprehensive memory statistics."""
        return {
            "message_count": len(self.messages),
            "token_estimate": self.get_token_estimate(),
            "memory_limit": self.messages.maxlen,
            "user_messages": len(self.get_messages_by_role("user")),
            "assistant_messages": len(self.get_messages_by_role("assistant")),
            "system_messages": len(self.get_messages_by_role("system"))
        }

    def is_full(self) -> bool:
        """Check if memory is at capacity."""
        return len(self.messages) == self.messages.maxlen

    def is_empty(self) -> bool:
        """Check if memory is empty."""
        return len(self.messages) == 0