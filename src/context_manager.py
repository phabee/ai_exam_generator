from typing import List, Dict

class ContextManager:
    def __init__(self):
        self.current_module = "General Python"
        self.context_data = ""

    def load_module_context(self, module_name: str, context_text: str):
        """Loads the context material for a specific module."""
        self.current_module = module_name
        self.context_data = context_text

    def get_context(self) -> str:
        return self.context_data

    def get_system_prompt_addition(self) -> str:
        if not self.context_data:
            return ""
        return f"\n\nContext/Lecture Material for {self.current_module}:\n{self.context_data}\n"
