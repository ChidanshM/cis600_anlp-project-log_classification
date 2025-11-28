import pandas as pd
import re

def parse_hdfs_log(log_file_path, output_csv_path):
    print(f"📂 Parsing {log_file_path}...")
    
    # Define the HDFS log pattern
    # Format: Date Time PID Level Component: Content
    log_pattern = re.compile(r'(\d{6})\s+(\d{6})\s+(\d+)\s+(\w+)\s+([^:]+):\s+(.*)')
    
    parsed_data = []
    
    with open(log_file_path, 'r') as f:
        for line in f:
            match = log_pattern.match(line.strip())
            if match:
                date, time, pid, level, component, content = match.groups()
                parsed_data.append({
                    'timestamp': f"{date} {time}",
                    'pid': pid,
                    'level': level,
                    'component': component,
                    'log_message': content,  # Mapping 'Content' -> 'log_message'
                    # For HDFS, the 'Level' is often used as a proxy for label in simple tasks,
                    # BUT real anomaly labels usually come from a separate file (anomaly_label.csv).
                    # If you don't have that, we can use 'Level' or 'Component' as a temporary target.
                    'target_label': level 
                })

    # Convert to DataFrame
    df = pd.DataFrame(parsed_data)
    
    # Save to CSV
    df.to_csv(output_csv_path, index=False)
    print(f"✅ Parsed {len(df)} lines. Saved to {output_csv_path}")
    return df

if __name__ == "__main__":
    # Replace with your actual file path
    parse_hdfs_log("../HDFS.log", "../HDFS_structured.csv")