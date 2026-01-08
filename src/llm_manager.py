from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import os

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, model: str = None) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        import openai
        # Check for Azure config first
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY") or api_key
        azure_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        if azure_endpoint and azure_key:
            self.client = openai.AzureOpenAI(
                api_key=azure_key,
                api_version=azure_version,
                azure_endpoint=azure_endpoint
            )
            self.is_azure = True
            self.default_model = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4")
        else:
             self.client = openai.OpenAI(api_key=api_key)
             self.is_azure = False
             self.default_model = "gpt-4-turbo-preview"

    def generate_response(self, system_prompt: str, user_prompt: str, model: str = None) -> str:
        try:
            used_model = model or self.default_model
            response = self.client.chat.completions.create(
                model=used_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_response(self, system_prompt: str, user_prompt: str, model: str = "claude-3-opus-20240229") -> str:
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

class GoogleProvider(LLMProvider):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)

    def generate_response(self, system_prompt: str, user_prompt: str, model: str = "gemini-1.5-pro-latest") -> str:
         try:
            model = genai.GenerativeModel(model)
            # Gemini doesn't have a strict system prompt separation in the same way, but we can prepend it.
            response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text
         except Exception as e:
            return f"Error: {str(e)}"

class EnsembleEvaluator:
    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers

    def evaluate(self, prompt: str, system_prompt: str = "You are an expert examiner.") -> Dict[str, str]:
        results = {}
        # In a real app, we'd run these in parallel (async)
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__
            results[f"{provider_name}_{i}"] = provider.generate_response(system_prompt, prompt)
        return results

    def aggregate_feedback(self, individual_results: Dict[str, str]) -> str:
        # Simple concatenation for now, or use one LLM to summarize
        summary = "## Ensemble Evaluation Results\n\n"
        for provider, result in individual_results.items():
            summary += f"### {provider}\n{result}\n\n"
        return summary
