import logging
from typing import List, Dict, Union
from openai import OpenAI

from configs import ChatConfig
from local_chat_memory import ChatMemory


class OpenAIInfra:
    """Core OpenAI infrastructure with memory and retry capabilities."""

    def __init__(self, config: ChatConfig) -> None:
        if not config.api_key:
            raise ValueError("API key is required in config")

        self.client = OpenAI(api_key=config.api_key)
        self.config = config
        self.memory = ChatMemory(max_length=self.config.memory_size)
        self.logger = logging.getLogger(__name__)

    def send_message(
            self,
            content: str,
            use_memory: bool = True,
            **kwargs
    ) -> str:
        """Send a text message and get response."""
        if not content.strip():
            raise ValueError("Message content cannot be empty")

        messages = self.memory.get_messages() if use_memory else []
        messages.append({"role": "user", "content": content})

        response = self._make_request(messages, **kwargs)

        if use_memory:
            self.memory.add_message("user", content)
            self.memory.add_message("assistant", response)

        return response

    def send_messages(
            self,
            messages: List[Dict[str, str]],
            use_memory: bool = True,
            **kwargs
    ) -> str:
        """Send multiple messages and get response."""
        if not messages:
            raise ValueError("Messages list cannot be empty")

        chat_messages = self.memory.get_messages() if use_memory else []
        chat_messages.extend(messages)

        response = self._make_request(chat_messages, **kwargs)

        if use_memory:
            self.memory.add_messages(messages)
            self.memory.add_message("assistant", response)

        return response

    def send_system_message(self, system_prompt: str, user_message: str, **kwargs) -> str:
        """Send a message with system prompt."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return self._make_request(messages, **kwargs)

    def _make_request(self, messages: List[Dict], **kwargs) -> str:
        """Make API request with retry logic."""
        request_params = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }

        if self.config.max_tokens:
            request_params["max_tokens"] = kwargs.get("max_tokens", self.config.max_tokens)

        last_exception = None

        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(f"API request attempt {attempt + 1}: {request_params['model']}")

                response = self.client.chat.completions.create(**request_params)

                if not response.choices:
                    raise Exception("No response choices returned from API")

                content = response.choices[0].message.content
                if not content:
                    raise Exception("Empty response content from API")

                self.logger.info(f"API request successful. Tokens used: {response.usage.total_tokens}")
                return content

            except Exception as e:
                last_exception = e
                self.logger.warning(f"API request attempt {attempt + 1} failed: {e}")

                if attempt == self.config.max_retries - 1:
                    self.logger.error(f"All {self.config.max_retries} attempts failed")
                    break

        raise Exception(f"OpenAI API failed after {self.config.max_retries} attempts: {last_exception}")

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
        self.logger.info("Memory cleared")

    def get_memory_stats(self) -> Dict[str, Union[int, List]]:
        """Get memory statistics."""
        return self.memory.get_memory_stats()

    def set_system_prompt(self, prompt: str) -> None:
        """Set a persistent system prompt."""
        if self.memory.is_empty() or self.memory.get_messages()[0]["role"] != "system":
            # Add system message at the beginning
            temp_messages = list(self.memory.get_messages())
            self.memory.clear()
            self.memory.add_message("system", prompt)
            if temp_messages:
                self.memory.add_messages(temp_messages)
        else:
            # Update existing system message
            messages = list(self.memory.get_messages())
            messages[0]["content"] = prompt
            self.memory.clear()
            self.memory.add_messages(messages)

        self.logger.info("System prompt set")

    def export_conversation(self) -> List[Dict[str, str]]:
        """Export the current conversation."""
        return self.memory.get_messages()

    def import_conversation(self, messages: List[Dict[str, str]]) -> None:
        """Import a conversation into memory."""
        self.memory.clear()
        self.memory.add_messages(messages)
        self.logger.info(f"Imported {len(messages)} messages")