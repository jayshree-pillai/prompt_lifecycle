from typing import Any, Dict


class LLMClient:
    """
    LLM client stub.

    Today:
      - call(prompt_text) returns the prompt_text unchanged (echo)

    Tomorrow:
      - replace the body of call() with Azure/OpenAI plumbing,
        but keep the same interface so Runtime doesn't change.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def call(self, prompt_text: str) -> str:
        # Echo stub: makes it easy to see exactly what would be sent to the model.
        return prompt_text
