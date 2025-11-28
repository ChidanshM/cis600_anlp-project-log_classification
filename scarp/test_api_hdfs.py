import pandas as pd
import requests
import io
from sklearn.metrics import classification_report, accuracy_score

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/classify/"
DATASET_PATH = "dataset/HDFS_2k.log_structured.csv"
# ---------------------

def prepare_hdfs_data():
    """
    Loads HDFS dataset and adapts it to the format required by the API.
    """
    try:
        df = pd.read_csv(DATASET_PATH)
    except FileNotFoundError:
        print(f"❌ Dataset not found at {DATASET_PATH}. Please check the path.")
        exit(1)

    # Rename columns to match what the API expects
    # HDFS 'Content' -> 'log_message'
    # HDFS 'EventTemplate' -> 'ground_truth' (for validation later)
    if 'Content' in df.columns:
        df = df.rename(columns={'Content': 'log_message'})
    
    # Add 'source' column if missing (API requires it)
    if 'source' not in df.columns:
        df['source'] = 'HDFS'

    # Keep track of ground truth labels for validation
    if 'EventTemplate' in df.columns:
        df['ground_truth'] = df['EventTemplate']
    else:
        print("⚠️ Warning: 'EventTemplate' not found. Cannot calculate accuracy, only prediction.")
        df['ground_truth'] = None

    # Select only columns needed for the API upload
    upload_df = df[['source', 'log_message']]
    
    return df, upload_df

def test_api():
    print(f"🚀 Connecting to API at {API_URL}...")

    # 1. Prepare Data
    full_df, upload_df = prepare_hdfs_data()
    print(f"📂 Prepared {len(upload_df)} logs for testing.")

    # 2. Convert to CSV for upload
    stream = io.StringIO()
    upload_df.to_csv(stream, index=False)
    stream.seek(0)
    
    # 3. Send Request
    try:
        files = {'file': ('test_hdfs.csv', stream, 'text/csv')}
        response = requests.post(API_URL, files=files)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return
            
        print("✅ API Response Received.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is 'uvicorn app.main:app' running?")
        return

    # 4. Process Response
    result_content = response.content.decode('utf-8')
    result_df = pd.read_csv(io.StringIO(result_content))
    
    # 5. Validate (Compare Predictions vs Ground Truth)
    if 'target_label' in result_df.columns and 'ground_truth' in full_df.columns:
        # Align the dataframes
        y_true = full_df['ground_truth'].astype(str)
        y_pred = result_df['target_label'].astype(str)
        
        # Calculate Metrics
        acc = accuracy_score(y_true, y_pred)
        print(f"\n📊 Validation Results:")
        print(f"   Accuracy: {acc * 100:.2f}%")
        
        # Detailed Report
        print("\n🔍 Classification Report:")
        print(classification_report(y_true, y_pred, zero_division=0))
        
        # Save detailed results for review
        result_df['actual_label'] = y_true
        result_df['match'] = result_df['target_label'] == result_df['actual_label']
        result_df.to_csv("hdfs_validation_results.csv", index=False)
        print("💾 Detailed results saved to 'hdfs_validation_results.csv'")
        
    else:
        print("⚠️ Could not validate. Missing 'target_label' in response or 'ground_truth' in dataset.")
        print("Response columns:", result_df.columns)

if __name__ == "__main__":
    test_api()