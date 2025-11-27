from .base import LogProcessor
import re
from google import genai

class LLMProcessor(LogProcessor):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def classify(self, log_message: str) -> str:
        prompt = f'''Classify the log message into one of these categories: 
        (1) Workflow Error, (2) Deprecation Warning.
        If you can't figure out a category, use "Unclassified".
        Put the category inside <category> </category> tags. 
        Log message: {log_message}'''

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            content = response.text
            match = re.search(r'<category>(.*)<\/category>', content, flags=re.DOTALL)
            if match:
                return match.group(1)
            return "Unclassified"
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Unclassified"