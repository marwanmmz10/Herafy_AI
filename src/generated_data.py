import csv
import os
import random
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
data_dir = os.path.join(base_dir, 'data')
file_path = os.path.join(data_dir, 'herafy_reviews.csv')

os.makedirs(data_dir, exist_ok=True)

header = ['review_id', 'user_id', 'technician_id', 'rating_value', 'review_text', 'created_at', 'device_id',
          'ip_address', 'service_status']


def generate_bulk_data(n=100):
    rows = []
    start_time = datetime(2026, 4, 1)

    for i in range(1, n + 1):
        # Randomly decide if this row will be a "Fraud" pattern
        is_fraud = random.random() < 0.2  # 20% chance of fraud pattern

        review_id = i
        user_id = random.randint(100, 200)
        tech_id = random.randint(10, 20)

        if is_fraud:
            rating = 5
            text = "Good"  # Short text
            status = random.choice(['pending', 'completed'])
            device = "DEV-FRAUD"  # Repeatable device
            # Night hours (1 AM to 5 AM)
            time_offset = timedelta(days=random.randint(0, 10), hours=random.randint(1, 5))
        else:
            rating = random.randint(1, 5)
            text = "This was a very professional service, thank you!"
            status = "completed"
            device = f"DEV-{random.randint(1000, 9000)}"
            # Normal hours
            time_offset = timedelta(days=random.randint(0, 10), hours=random.randint(8, 20))

        created_at = (start_time + time_offset).strftime("%Y-%m-%d %H:%M:%S")

        rows.append(
            [review_id, user_id, tech_id, rating, text, created_at, device, f"192.168.1.{random.randint(1, 254)}",
             status])
    return rows


# Create the file
data = generate_bulk_data(100)
with open(file_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)

print(f"Success! Generated {len(data)} rows in {file_path}")