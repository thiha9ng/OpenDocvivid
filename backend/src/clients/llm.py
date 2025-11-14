from google import genai
from src.configs.config import settings
llm_client = genai.Client(  # pyright: ignore[reportUndefinedVariable]
        api_key=settings.gemini_api_key  # pyright: ignore[reportUndefinedVariable]
    )

class LLMClient:
    @classmethod
    def generate_text(cls, PROMPT: str, model: str = "gemini-2.5-flash", temperature: float = 0.7, max_output_tokens: int = 16384) -> str:
        response =llm_client.models.generate_content(
            model=model,
            contents=PROMPT,
            config={
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
        )
        return response.text