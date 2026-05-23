from payout_api_client import PayoutAPIClient

client = PayoutAPIClient("http://localhost:5000")

# Get a patient's payout
patient = client.get_patient_payout(1)
print(f"Patient payout: ${patient['payout']}")

# Filter patients
filtered = client.filter_patients(age=35)
print(f"Found {filtered['total_records']} patients aged 35")

# Get statistics
stats = client.get_statistics()
print(f"Average payout: ${stats['average_payout']}")