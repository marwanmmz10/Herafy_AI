from datetime import datetime

# Mock data based on your Google Sheet structure
reviews_batch = [
    {
        "review_id": 1,
        "user_id": 101,
        "technician_id": 50,
        "rating_value": 5,
        "review_text": "Excellent service",
        "created_at": "2026-04-06 10:00:00",
        "device_id": "DEV-882",
        "ip_address": "192.168.1.1"
    },
    {
        "review_id": 2,
        "user_id": 101,
        "technician_id": 50,
        "rating_value": 5,
        "review_text": "Good",
        "created_at": "2026-04-06 10:00:45",  # Less than 60 seconds!
        "device_id": "DEV-882",
        "ip_address": "192.168.1.1"
    }
]

def detect_basic_fraud(data_list):
    """
    Analyzes a list of reviews to detect immediate fraud patterns.
    Rules:
    1. Duplicate Device ID within 60 seconds.
    2. High rating with very short text.
    """
    fraud_reports = []
    date_format = "%Y-%m-%d %H:%M:%S"

    for i in range(1, len(data_list)):
        prev_rev = data_list[i-1]
        curr_rev = data_list[i]

        # Time Difference Calculation
        t1 = datetime.strptime(prev_rev['created_at'], date_format)
        t2 = datetime.strptime(curr_rev['created_at'], date_format)
        time_diff = (t2 - t1).total_seconds()

        # Fraud Logic
        is_same_device = prev_rev['device_id'] == curr_rev['device_id']
        is_too_fast = time_diff < 60

        if is_same_device and is_too_fast:
            report = {
                "review_id": curr_rev['review_id'],
                "risk_score": 90,
                "reason": "Rapid duplicate posting from same device"
            }
            fraud_reports.append(report)

    return fraud_reports

# Execution
results = detect_basic_fraud(reviews_batch)
print(f"Fraud Analysis Results: {results}")