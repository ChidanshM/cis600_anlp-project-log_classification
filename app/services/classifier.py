import joblib
from app.config import MODEL_PATH, REGEX_PATTERNS, GOOGLE_API_KEY
from app.processors.regex import RegexProcessor
from app.processors.bert import BertProcessor
from app.processors.llm import LLMProcessor

class ClassificationService:
    def __init__(self):
        # Initialize processors
        print("Initializing Classification Service...")
        self.regex_processor = RegexProcessor(REGEX_PATTERNS)
        
        # Load the BERT classifier model
        print(f"Loading model from {MODEL_PATH}...")
        try:
            self.bert_model = joblib.load(MODEL_PATH)
            self.bert_processor = BertProcessor(self.bert_model)
        except FileNotFoundError:
            raise RuntimeError(f"Model file not found at {MODEL_PATH}. Please ensure the model exists.")

        # Initialize LLM processor
        if GOOGLE_API_KEY:
            self.llm_processor = LLMProcessor(GOOGLE_API_KEY)
        else:
            print("Warning: GOOGLE_API_KEY not set. LLM features will fail.")
            self.llm_processor = None

    def classify_log(self, source: str, message: str) -> str:
        # Special handling for LegacyCRM
        if source == "LegacyCRM":
            if self.llm_processor:
                return self.llm_processor.classify(message)
            return "Unclassified (LLM Not Configured)"
        
        # Stage 1: Regex
        label = self.regex_processor.classify(message)
        if label:
            return label
            
        # Stage 2: BERT
        label = self.bert_processor.classify(message)
        if label != "Unclassified":
            return label

        # Stage 3: LLM Fallback (for complex/unknown patterns)
        if self.llm_processor:
            return self.llm_processor.classify(message)

        return "Unclassified"
    
    def classify_batch(self, logs: list[tuple[str, str]]) -> list[str]:
        return [self.classify_log(source, msg) for source, msg in logs]
    
