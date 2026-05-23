# Payout REST API Project

This project provides a REST API for retrieving patient payout information based on CPT codes and medical bundles.

## Architecture

### Components

1. **payout_api_server.py** - Flask REST API server that serves patient payout data
2. **payout_api_client.py** - Python client that makes requests to the API
3. **emr_payout_mapper.py** - Maps CPT codes to payout values
4. **bundle_payout_calculator.py** - Calculates payouts based on code bundles

### Data Files

- **emr_codes.csv** - CPT codes and their associated payout values
- **bundle_records_matching.json** - Patient records with matching bundle payouts
- **bundle_payout_results_matching.json** - Calculated payout results

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Project
### Step 1: Start the API Server
```bash
python payout_api_server.py
```
The server will start on http://localhost:5000

You should see output like:

```Code
Starting Payout API Server...
Available endpoints:
  GET /api/health - Health check
  GET /api/patient/<id> - Get payout for a specific patient
  GET /api/patients - Get all patients
  GET /api/patients/filter - Filter patients by criteria
  GET /api/statistics - Get payout statistics
```
### Step 2: Run the Client (in a new terminal)
```bash
python payout_api_client.py
```
The client will make various requests to the API and display results.

## API Endpoints
### Health Check
```Code
GET /api/health
```
Returns status and total number of patients in the system.

#### Response:

```JSON
{
  "status": "healthy",
  "message": "Payout API is running",
  "total_patients": 5
}
```
### Get Patient Payout
```Code
GET /api/patient/<patient_id>
```
Get payout information for a specific patient (1-based index).

#### Example:

```Code
GET /api/patient/1
```
#### Response:

```JSON
{
  "patient_id": 1,
  "age": 35,
  "gender": "Male",
  "codes_completed": "CPT12847, CPT58923, CPT50062",
  "bundle": "CPT12847, CPT58923, CPT50062",
  "payout": 79,
  "currency": "USD"
}
```

### Get All Patients
```Code
GET /api/patients
```
Get all patient records.

#### Response:

```JSON
{
  "total_records": 5,
  "patients": [
    {
      "patient_id": 1,
      "age": 35,
      "gender": "Male",
      "codes_completed": "CPT12847, CPT58923, CPT50062",
      "bundle": "CPT12847, CPT58923, CPT50062",
      "payout": 79
    },
    ...
  ]
}
```
### Filter Patients
```Code
GET /api/patients/filter?age=35&gender=Male&min_payout=50&max_payout=150
```
Filter patients by age, gender, or payout range.

#### Query Parameters:

- `age` (optional, int) - Exact age to filter by
- `gender` (optional, string) - Gender to filter by (Male/Female)
- `min_payout` (optional, float) - Minimum payout amount
- `max_payout` (optional, float) - Maximum payout amount
Response:

```JSON
{
  "total_records": 1,
  "filters": {
    "age": 35,
    "gender": "Male",
    "min_payout": 50,
    "max_payout": 150
  },
  "patients": [
    {
      "patient_id": 1,
      "age": 35,
      "gender": "Male",
      "codes_completed": "CPT12847, CPT58923, CPT50062",
      "bundle": "CPT12847, CPT58923, CPT50062",
      "payout": 79
    }
  ]
}
```

### Get Statistics
```Code
GET /api/statistics
```
Get aggregated statistics about all patient payouts.

#### Response:

```JSON
{
  "total_records": 5,
  "total_payout": 401,
  "average_payout": 80.2,
  "min_payout": 59,
  "max_payout": 100
}
```