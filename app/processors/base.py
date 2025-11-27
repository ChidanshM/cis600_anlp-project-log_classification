from abc import ABC, abstractmethod

class LogProcessor(ABC):
    """
    Abstract base class for all log processors.
    """
    @abstractmethod
    def classify(self, log_message: str) -> str | None:
        """
        Classify a log message.
        Returns the label as a string, or None if classification fails.
        """
        pass