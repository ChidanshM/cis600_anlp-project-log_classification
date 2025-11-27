from .base import LogProcessor
import re

class RegexProcessor(LogProcessor):
    def __init__(self, patterns: dict):
        self.patterns = patterns

    def classify(self, log_message: str) -> str | None:
        for pattern, label in self.patterns.items():
            if re.search(pattern, log_message):
                return label
        return None