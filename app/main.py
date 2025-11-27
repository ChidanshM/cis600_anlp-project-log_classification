import pandas as pd
import io
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from app.services.classifier import ClassificationService

# --- FIX 1: Initialize app first ---
app = FastAPI()

# --- FIX 2: Initialize service ONLY ONCE ---
# We do this globally so it persists across requests
try:
    service = ClassificationService()
except Exception as e:
    print(f"Failed to initialize service: {e}")
    service = None

@app.post("/classify/")
async def classify_logs(file: UploadFile):
    # Check if service loaded correctly
    if service is None:
        raise HTTPException(status_code=500, detail="Classification service failed to start.")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Standardization check: stripping spaces from column names can prevent key errors
        df.columns = df.columns.str.strip()
        
        if "source" not in df.columns or "log_message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'log_message' columns.")

        # Prepare data for service
        logs = list(zip(df["source"], df["log_message"]))
        
        # Perform classification
        df["target_label"] = service.classify_batch(logs)

        # Return as a downloadable file
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=classified_output.csv"
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()