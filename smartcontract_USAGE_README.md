# API Usage Guide

## Example Usage

### Using cURL

```bash
# Get a specific patient's payout
curl http://localhost:5000/api/patient/1

# Get all patients
curl http://localhost:5000/api/patients

# Filter patients by age
curl "http://localhost:5000/api/patients/filter?age=35"

# Filter patients by payout range
curl "http://localhost:5000/api/patients/filter?min_payout=50&max_payout=150"

# Get statistics
curl http://localhost:5000/api/statistics

# Health check
curl http://localhost:5000/api/health