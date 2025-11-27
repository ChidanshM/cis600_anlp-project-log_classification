import requests
import os

# Configuration
url = "http://127.0.0.1:8000/classify/"
input_file = "tests/test.csv"
output_file = "classified_output.csv"  # The file where results will be saved

# Check if input file exists first
if not os.path.exists(input_file):
    print(f"Error: File not found at {os.path.abspath(input_file)}")
else:
    try:
        # Open and send the file
        with open(input_file, "rb") as f:
            print(f"Sending {input_file} to {url}...")
            files = {"file": ("test.csv", f, "text/csv")}
            response = requests.post(url, files=files)

        # Check status
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Save the content to a file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            print(f"Success! Classified logs saved to: {os.path.abspath(output_file)}")
            
            # Print a preview to the console
            print("\n--- Preview of Response ---")
            print(response.text)
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Connection Failed: {e}")