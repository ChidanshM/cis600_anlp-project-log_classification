import pandas as pd
import io
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from app.services.classifier import ClassificationService

app = FastAPI()

# Initialize service globally so we don't reload models on every request
service = ClassificationService()

@app.post("/classify/")
async def classify_logs(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
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