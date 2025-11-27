import requests
import os

# Define the URL and file path
url = "http://127.0.0.1:8000/classify/"
file_path = "tests/test.csv"

# Check if file exists first
if not os.path.exists(file_path):
    print(f"Error: File not found at {os.path.abspath(file_path)}")
else:
    try:
        # Open and send the file
        with open(file_path, "rb") as f:
            print(f"Sending {file_path} to {url}...")
            files = {"file": ("test.csv", f, "text/csv")}
            response = requests.post(url, files=files)

        # Print the result
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("\n--- Success! Response Content ---")
            print(response.text)
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Connection Failed: {e}")