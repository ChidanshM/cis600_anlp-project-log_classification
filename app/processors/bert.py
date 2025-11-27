from .base import LogProcessor
from sentence_transformers import SentenceTransformer

class BertProcessor(LogProcessor):
    def __init__(self, classifier_model):
        self.classifier = classifier_model
        # Initialize the sentence transformer
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def classify(self, log_message: str) -> str | None:
        embeddings = self.embedding_model.encode([log_message])
        probabilities = self.classifier.predict_proba(embeddings)[0]
        
        # Confidence threshold check
        if max(probabilities) < 0.5:
            return "Unclassified"
        
        return self.classifier.predict(embeddings)[0]