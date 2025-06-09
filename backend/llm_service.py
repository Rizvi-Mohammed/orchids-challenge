import os
import base64
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

# Required imports for Azure OpenAI
from openai import AsyncAzureOpenAI, APIConnectionError, APIStatusError

# Required imports for Anthropic (Claude)
from anthropic import AsyncAnthropic, APIStatusError as AnthropicAPIStatusError

# Required imports for Gemini
import google.generativeai as genai


# --- CENTRALIZED SYSTEM PROMPT ---
# Define the system prompt once for all LLM providers
LLM_SYSTEM_PROMPT = """
You are an expert web developer AI. Your task is to accurately clone the aesthetic and layout of the given website into a single, self-contained HTML file.

**Instructions for HTML Generation:**
1.  **Structure:** Generate a complete HTML5 document (`<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`).
2.  **Styling:** All CSS should be embedded directly within a single `<style>` tag in the `<head>` section. Do NOT use external stylesheets or `!important`.
3.  **Visual Fidelity:** Replicate the visual appearance, layout, colors, fonts, spacing, and element sizing as accurately as possible based on the screenshot.
4.  **Responsiveness:** Ensure the generated HTML is responsive and adapts well to different screen sizes (especially mobile-first), using CSS media queries if necessary.
5.  **Semantic HTML:** Use appropriate HTML5 semantic tags (e.g., `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<button>`, `<a>`, `<img>`) for meaningful structure.
6.  **Assets:** For images, use placeholder images (e.g., `https://placehold.co/WIDTHxHEIGHT/BGCOLOR/TEXTCOLOR?text=DESCRIPTION`) as `src` values. Do NOT try to fetch or embed original image URLs directly.
7.  **Content:** Include placeholder text that clearly indicates the original content's nature (e.g., "Main Headline", "Product Description").
8.  **JavaScript:** Do NOT include any JavaScript unless it's absolutely necessary for a core UI interaction (like a simple modal toggle or tab switch, if clearly evident). Keep it minimal and inline within `<script>` tags in `<body>`.
9.  **Self-Contained:** The output MUST be a single HTML file with all CSS inline, and all content (including placeholder images) directly embedded or linked via generic placeholders. No external files or complex relative paths.
10. **Output Format:** Provide ONLY the HTML code. Do NOT include any conversational text, markdown formatting (like ```html), or explanations outside the HTML document itself.
"""


class LLMProvider(ABC):
    """
    Abstract Base Class (Interface) for LLM Providers.
    All concrete LLM providers must implement the generate_content method.
    """
    @abstractmethod
    async def generate_content(self, system_prompt: str, parts: List[Dict[str, Any]]) -> str:
        """
        Generates content using the specific LLM provider.

        Args:
            system_prompt: The system-level instructions for the LLM.
            parts: A list of content parts (text and/or image data) to send to the LLM.

        Returns:
            The generated text content from the LLM.
        """
        pass


class AzureOpenAILLMProvider(LLMProvider):
    """
    Concrete implementation of LLMProvider for Azure OpenAI API.
    """
    def __init__(self):
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.azure_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        if not all([self.azure_endpoint, self.azure_api_key, self.azure_deployment_name]):
            raise ValueError("AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT_NAME environment variables must be set for AzureOpenAILLMProvider.")

        self.client = AsyncAzureOpenAI(
            api_key=self.azure_api_key,
            api_version=self.azure_api_version,
            azure_endpoint=self.azure_endpoint
        )
        print("AzureOpenAILLMProvider initialized.")

    async def generate_content(self, system_prompt: str, parts: List[Dict[str, Any]]) -> str:
        """
        Generates content using the configured Azure OpenAI model.
        Converts generic 'parts' format to Azure OpenAI's 'messages' format.
        """
        try:
            # Construct messages for Azure OpenAI (vision models expect a specific format)
            messages_content: List[Dict[str, Any]] = []
            
            # User message content (from 'parts' argument)
            for part in parts:
                if 'text' in part:
                    messages_content.append({"type": "text", "text": part['text']})
                elif 'mime_type' in part and 'data' in part:
                    base64_image = base64.b64encode(part['data']).decode('utf-8')
                    messages_content.append({"type": "image_url", "image_url": {"url": f"data:{part['mime_type']};base64,{base64_image}"}})

            messages = [
                {"role": "system", "content": system_prompt}, # System prompt is now passed
                {"role": "user", "content": messages_content}
            ]

            response = await self.client.chat.completions.create(
                model=self.azure_deployment_name,
                messages=messages,
                max_tokens=8000 # Increased max_tokens
            )
            cloned_html = response.choices[0].message.content

            if cloned_html.startswith("```html") and cloned_html.endswith("```"):
                cloned_html = cloned_html[7:-3].strip()
            return cloned_html

        except (APIConnectionError, APIStatusError) as e:
            print(f"Azure OpenAI API Error: {e}")
            raise
        except Exception as e:
            print(f"Error calling Azure OpenAI API: {e}")
            raise


class AnthropicLLMProvider(LLMProvider):
    """
    Concrete implementation of LLMProvider for Anthropic API (Claude).
    """
    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model_name = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")

        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set for AnthropicLLMProvider.")

        self.client = AsyncAnthropic(api_key=self.anthropic_api_key)
        print("AnthropicLLMProvider initialized.")

    async def generate_content(self, system_prompt: str, parts: List[Dict[str, Any]]) -> str:
        """
        Generates content using the configured Anthropic model.
        Converts generic 'parts' format to Anthropic's 'content' block format.
        """
        try:
            anthropic_content_blocks: List[Dict[str, Any]] = []
            for part in parts:
                if 'text' in part:
                    anthropic_content_blocks.append({"type": "text", "text": part['text']})
                elif 'mime_type' in part and 'data' in part:
                    base64_image = base64.b64encode(part['data']).decode('utf-8')
                    anthropic_content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": part['mime_type'],
                            "data": base64_image
                        }
                    })

            response = await self.client.messages.create(
                model=self.anthropic_model_name,
                max_tokens=4000, # Claude max_tokens for vision models
                system=system_prompt, # System prompt is now passed
                messages=[
                    {
                        "role": "user",
                        "content": anthropic_content_blocks
                    }
                ]
            )
            cloned_html = response.content[0].text

            if cloned_html.startswith("```html") and cloned_html.endswith("```"):
                cloned_html = cloned_html[7:-3].strip()
            return cloned_html

        except AnthropicAPIStatusError as e:
            print(f"Anthropic API Error: {e}")
            raise
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            raise


class GeminiLLMProvider(LLMProvider):
    """
    Concrete implementation of LLMProvider for Google Gemini API.
    """
    def __init__(self):
        # Local import to only load genai if Gemini is chosen
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set for GeminiLLMProvider.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro') # Or 'gemini-pro-vision' for vision-only tasks
        print("GeminiLLMProvider initialized.")

    async def generate_content(self, system_prompt: str, parts: List[Dict[str, Any]]) -> str:
        """
        Generates content using the configured Gemini model.
        """
        try:
            # For Gemini, the system prompt is usually handled by prepending a "user" role message
            # or by specific model configuration. Here, we'll prepend it as a text part.
            gemini_parts = [{"text": system_prompt}]
            gemini_parts.extend(parts)

            response = await self.model.generate_content_async(gemini_parts)
            cloned_html = response.text
            if cloned_html.startswith("```html") and cloned_html.endswith("```"):
                cloned_html = cloned_html[7:-3].strip()
            return cloned_html
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise


def get_llm_provider(provider_name: str) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider instance.
    """
    if provider_name.lower() == "azure_openai":
        return AzureOpenAILLMProvider()
    elif provider_name.lower() == "anthropic":
        return AnthropicLLMProvider()
    elif provider_name.lower() == "gemini":
        return GeminiLLMProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}. Supported: 'azure_openai', 'anthropic', 'gemini'.")