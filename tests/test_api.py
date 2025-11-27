import pytest
from app.processors.regex import RegexProcessor
from app.config import REGEX_PATTERNS

def test_regex_processor_match():
    processor = RegexProcessor(REGEX_PATTERNS)
    log = "Backup completed successfully."
    assert processor.classify(log) == "System Notification"

def test_regex_processor_no_match():
    processor = RegexProcessor(REGEX_PATTERNS)
    log = "This is a random error message."
    assert processor.classify(log) is None

# You can add more tests here for other processors using mocks