from google import genai
from dotenv import load_dotenv
from typing import Any
import os

load_dotenv()


def extract_text_from_response(response: Any) -> str:
    """Extract text content from API response.

    Args:
        response: API response object.

    Returns:
        Extracted text content.
    """
    text_parts = []

    if response and response.candidates:
        for candidate in response.candidates:
            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        text_parts.append(part.text)


client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """Translate the following Japanese text to English:
```
ステップ 1: 目を開ける
指示: 目を開ける
```

Please include only the English translation result, and do not include anything unnecessary.
"""
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
print(response.text)
