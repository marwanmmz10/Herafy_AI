import csv
import os
import random
from datetime import datetime, timedelta

# Set up directory paths relative to the current script location
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
data_dir = os.path.join(base_dir, 'data')
file_path = os.path.join(data_dir, 'herafy_reviews.csv')

# Create the data directory if it does not exist
os.makedirs(data_dir, exist_ok=True)

# Define the structure of the CSV file
header = [
    'review_id', 'user_id', 'technician_id', 'rating_value',
    'review_text', 'created_at', 'device_id', 'ip_address', 'service_status'
]

def generate_bulk_data(n=1000):
    """Generates synthetic review data with specific fraud patterns."""
    rows = []
    start_time = datetime(2026, 4, 1)

    for i in range(1, n + 1):
        # Define a 20% probability for a record to follow a suspicious pattern
        is_fraud = random.random() < 0.2

        review_id = i
        user_id = random.randint(100, 200)
        tech_id = random.randint(10, 20)

        if is_fraud:
            # Fraud Pattern: High rating, very short text, static device ID, and late-night hours
            rating = 5
            text = "Good"
            status = random.choice(['pending', 'completed'])
            device = "DEV-FRAUD"
            # Generate timestamps between 1 AM and 5 AM
            time_offset = timedelta(days=random.randint(0, 10), hours=random.randint(1, 5))
        else:
            # Normal Pattern: Varied ratings, descriptive text, unique devices, and daytime hours
            rating = random.randint(1, 5)
            text = "This was a very professional service, thank you!"
            status = "completed"
            device = f"DEV-{random.randint(1000, 9000)}"
            # Generate timestamps between 8 AM and 8 PM
            time_offset = timedelta(days=random.randint(0, 10), hours=random.randint(8, 20))

        # Format the timestamp into a standard string format
        created_at = (start_time + time_offset).strftime("%Y-%m-%d %H:%M:%S")

        # Append the generated record to the rows list
        rows.append([
            review_id, user_id, tech_id, rating, text,
            created_at, device, f"192.168.1.{random.randint(1, 254)}", status
        ])
    return rows

# Generate 1000 records
data = generate_bulk_data(1000)

# Write the generated data to the CSV file
with open(file_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header) # Write the column names
    writer.writerows(data)  # Write all data rows

print(f"Success! Generated {len(data)} rows in {file_path}")