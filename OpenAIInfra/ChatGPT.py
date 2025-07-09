import json
from configs import ChatConfig
from open_ai_infra import OpenAIInfra


class ChatGPT(OpenAIInfra):
    """User-friendly ChatGPT client with enhanced features."""

    def __init__(self, config: ChatConfig):
        super().__init__(config)
        self.conversation_started = False

    def chat(self, message: str) -> str:
        """Simple chat interface - most common use case."""
        if not self.conversation_started:
            self.logger.info("Starting new conversation")
            self.conversation_started = True

        return self.send_message(message, use_memory=True)

    def ask(self, question: str, context: str = None) -> str:
        """Ask a question with optional context (no memory)."""
        if context:
            messages = [
                {"role": "system", "content": f"Context: {context}"},
                {"role": "user", "content": question}
            ]
            return self._make_request(messages)
        return self.send_message(question, use_memory=False)

    def complete(self, prompt: str, **kwargs) -> str:
        """Simple completion without conversation context."""
        messages = [{"role": "user", "content": prompt}]
        return self._make_request(messages, **kwargs)

    def role_play(self, character: str, user_message: str) -> str:
        """Role-playing with a specific character."""
        system_prompt = f"You are {character}. Stay in character and respond accordingly."
        return self.send_system_message(system_prompt, user_message)

    def summarize(self, text: str, style: str = "concise") -> str:
        """Summarize text with different styles."""
        styles = {
            "concise": "Provide a brief, concise summary",
            "detailed": "Provide a detailed summary with key points",
            "bullet": "Provide a bullet-point summary",
            "executive": "Provide an executive summary for business use"
        }

        if style not in styles:
            raise ValueError(f"Style must be one of: {list(styles.keys())}")

        prompt = f"{styles[style]} of the following text:\n\n{text}"
        return self.complete(prompt)

    def translate(self, text: str, target_language: str, source_language: str = "auto") -> str:
        """Translate text between languages."""
        if source_language == "auto":
            prompt = f"Translate the following text to {target_language}:\n\n{text}"
        else:
            prompt = f"Translate the following text from {source_language} to {target_language}:\n\n{text}"

        return self.complete(prompt)

    def explain(self, topic: str, level: str = "intermediate") -> str:
        """Explain a topic at different complexity levels."""
        levels = {
            "simple": "Explain this in simple terms that anyone can understand",
            "intermediate": "Provide a clear, moderately detailed explanation",
            "advanced": "Provide a comprehensive, technical explanation",
            "eli5": "Explain this like I'm 5 years old"
        }

        if level not in levels:
            raise ValueError(f"Level must be one of: {list(levels.keys())}")

        prompt = f"{levels[level]}: {topic}"
        return self.complete(prompt)

    def brainstorm(self, topic: str, num_ideas: int = 10) -> str:
        """Generate ideas for brainstorming."""
        prompt = f"Generate {num_ideas} creative ideas for: {topic}"
        return self.complete(prompt)

    def review_code(self, code: str, language: str = "python") -> str:
        """Review code and provide suggestions."""
        prompt = f"""Review the following {language} code and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Improvement suggestions
4. Best practices recommendations

Code:
```{language}
{code}
```"""
        return self.complete(prompt)

    def write_email(self, purpose: str, tone: str = "professional", length: str = "medium") -> str:
        """Generate email templates."""
        tones = ["professional", "casual", "friendly", "formal"]
        lengths = ["short", "medium", "long"]

        if tone not in tones:
            raise ValueError(f"Tone must be one of: {tones}")
        if length not in lengths:
            raise ValueError(f"Length must be one of: {lengths}")

        prompt = f"Write a {length}, {tone} email for: {purpose}"
        return self.complete(prompt)

    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if self.memory.is_empty():
            return "No conversation to summarize."

        messages = self.memory.get_messages()
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        return self.summarize(conversation_text, "concise")

    def restart_conversation(self) -> None:
        """Restart the conversation by clearing memory."""
        self.clear_memory()
        self.conversation_started = False
        self.logger.info("Conversation restarted")

    def save_conversation(self, filepath: str) -> None:
        """Save conversation to a file."""
        import json

        conversation = {
            "config": {
                "model": self.config.model,
                "temperature": self.config.temperature
            },
            "messages": self.export_conversation(),
            "stats": self.get_memory_stats()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Conversation saved to {filepath}")

    def load_conversation(self, filepath: str) -> None:
        """Load conversation from a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            conversation = json.load(f)

        self.import_conversation(conversation["messages"])
        self.conversation_started = True
        self.logger.info(f"Conversation loaded from {filepath}")
