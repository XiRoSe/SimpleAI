import os
from dataclasses import dataclass
from typing import Optional

from utils import load_env_file


# Load .env file when module is imported
load_env_file()


@dataclass
class ChatConfig:
    """Configuration for ChatGPT client."""
    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.9
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    max_retries: int = 3
    memory_size: int = 10

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Auto-load API key from environment if not provided
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")

            # Debug information
            if not self.api_key:
                print("🔍 Debug info:")
                print(f"   Current working directory: {os.getcwd()}")
                print(f"   OPENAI_API_KEY in environment: {'Yes' if 'OPENAI_API_KEY' in os.environ else 'No'}")

                # Check if .env file exists
                env_files = ['.env', '.env.local', '.env.production']
                for env_file in env_files:
                    if os.path.exists(env_file):
                        print(f"   Found {env_file}: Yes")
                        with open(env_file, 'r') as f:
                            content = f.read()
                            has_key = 'OPENAI_API_KEY' in content
                            print(f"   {env_file} contains OPENAI_API_KEY: {'Yes' if has_key else 'No'}")
                    else:
                        print(f"   Found {env_file}: No")

        if not self.api_key:
            raise ValueError(
                "API key is required. Please:\n"
                "1. Create a .env file in your project root with: OPENAI_API_KEY=sk-your-key-here\n"
                "2. Or set environment variable: export OPENAI_API_KEY=sk-your-key-here\n"
                "3. Or pass api_key parameter: ChatConfig(api_key='sk-your-key-here')"
            )

        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")

        if not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")

        if self.max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        if self.memory_size < 0:
            raise ValueError("memory_size must be non-negative")


@dataclass
class VisionConfig(ChatConfig):
    """Configuration specifically for vision tasks."""
    model: str = "gpt-4o"
    detail: str = "auto"  # low, high, auto

    def __post_init__(self):
        super().__post_init__()

        if self.detail not in ["low", "high", "auto"]:
            raise ValueError("detail must be 'low', 'high', or 'auto'")