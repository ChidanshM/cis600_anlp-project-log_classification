import pandas as pd
import requests
import io
from sklearn.metrics import classification_report, accuracy_score

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/classify/"
DATASET_PATH = "dataset/HDFS_2k.log_structured.csv"
# ---------------------

def run_test():
    print(f"📂 Loading {HDFS_FILE}...")
    try:
        # Load the HDFS dataset
        # We use 'Content' as the input message and 'EventTemplate' as the expected label
        df = pd.read_csv(HDFS_FILE)
    except FileNotFoundError:
        print(f"❌ File not found: {HDFS_FILE}")
        return

    print(f"✅ Loaded {len(df)} logs.")

    # --- 1. PREPARE DATA FOR API ---
    # The API expects 'source' and 'log_message'
    api_payload = pd.DataFrame({
        'source': ['HDFS'] * len(df),     # Dummy source
        'log_message': df['Content']      # Map 'Content' -> 'log_message'
    })

    # Convert to CSV in memory to upload
    csv_buffer = io.StringIO()
    api_payload.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # --- 2. SEND TO SERVER ---
    print(f"🚀 Sending data to API: {API_URL} ...")
    try:
        files = {'file': ('hdfs_test.csv', csv_buffer, 'text/csv')}
        response = requests.post(API_URL, files=files)
        
        if response.status_code != 200:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Failed! Make sure your server is running:")
        print("   Run: uvicorn server:app --reload")
        return

    # --- 3. PROCESS RESULTS ---
    print("✅ Response received! analyzing...")
    
    # Parse the CSV response from the API
    result_csv = io.StringIO(response.content.decode('utf-8'))
    results = pd.read_csv(result_csv)

    # --- 4. VALIDATE ACCURACY ---
    # We compare the API's 'target_label' vs the original 'EventTemplate'
    # Note: This assumes your model was trained to predict EventTemplate
    
    # Align columns (just in case row order was preserved, which pandas usually does)
    y_true = df['EventTemplate'].astype(str)
    y_pred = results['target_label'].astype(str)

    # Calculate Metrics
    acc = accuracy_score(y_true, y_pred)
    print(f"\n📊 Validation Results")
    print(f"======================")
    print(f"Accuracy: {acc * 100:.2f}%")
    print(f"Total Samples: {len(y_true)}")
    
    # Show a detailed report if classes match
    unique_true = y_true.unique()
    unique_pred = y_pred.unique()
    
    # Only print full report if there's overlap in labels (sanity check)
    if set(unique_pred).issubset(set(unique_true)) or len(unique_pred) > 0:
        print("\nDetailed Classification Report:")
        print(classification_report(y_true, y_pred, zero_division=0))
    else:
        print("\n⚠️ Warning: Predicted labels do not match Ground Truth classes.")
        print(f"Expected Examples: {unique_true[:3]}")
        print(f"Predicted Examples: {unique_pred[:3]}")

    # Save detailed comparison
    output_filename = "hdfs_validation_report.csv"
    results['ground_truth'] = y_true
    results['is_correct'] = results['target_label'] == results['ground_truth']
    results.to_csv(output_filename, index=False)
    print(f"\n💾 Detailed report saved to: {output_filename}")

if __name__ == "__main__":
    run_test()