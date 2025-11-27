# Core API & Server (Safe to upgrade)
fastapi==0.122.0
uvicorn==0.38.0
python-dotenv==1.2.0
python-multipart==0.0.20
httpx==0.28.1

# AI & ML (Pinned for stability)
# Do NOT upgrade scikit-learn without retraining your model!
scikit-learn==1.6.0
# 3.3.1 is stable for your current embedding code
sentence-transformers==3.3.1
joblib==1.3.2
pandas==2.0.2

# GenAI (Must be new for Gemini 2.5 support)
google-genai==1.52.0

# Testing
pytest==9.0.1