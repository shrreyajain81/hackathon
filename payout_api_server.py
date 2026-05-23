from flask import Flask, jsonify, request
import json
from emr_payout_mapper import EMRPayoutMapper
from bundle_payout_calculator import BundlePayoutCalculator

app = Flask(__name__)

# Initialize the mapper and calculator
mapper = EMRPayoutMapper("emr_codes.csv")
mapper.load_from_csv(skip_header=True)
calculator = BundlePayoutCalculator(mapper)

# Load the payout results
with open("bundle_payout_results.json", "r") as f:
    payout_records = json.load(f)


@app.route('/api/patient/<int:patient_id>', methods=['GET'])
def get_patient_payout(patient_id):
    """
    Get payout information for a specific patient by ID.
    
    Args:
        patient_id: The ID of the patient (1-based index)
    
    Returns:
        JSON response with patient payout information
    """
    # Validate patient ID (1-based index)
    if patient_id < 1 or patient_id > len(payout_records):
        return jsonify({
            'error': f'Patient ID {patient_id} not found',
            'message': f'Valid patient IDs are 1 to {len(payout_records)}'
        }), 404
    
    # Get patient record (convert to 0-based index)
    patient = payout_records[patient_id - 1]
    
    return jsonify({
        'patient_id': patient_id,
        'age': patient['age'],
        'gender': patient['gender'],
        'codes_completed': patient['codes_completed'],
        'bundle': patient['bundle'],
        'payout': patient['payout'],
        'currency': 'USD'
    }), 200


@app.route('/api/patient/<int:patient_id>/payout', methods=['POST'])
def update_patient_payout(patient_id):
    """
    Update the payout value for a specific patient.
    
    Args:
        patient_id: The ID of the patient (1-based index)
    
    Request body:
    {
        "payout": 64.00
    }
    
    Returns:
        JSON response with updated payout information
    """
    # Validate patient ID (1-based index)
    if patient_id < 1 or patient_id > len(payout_records):
        return jsonify({
            'error': f'Patient ID {patient_id} not found',
            'message': f'Valid patient IDs are 1 to {len(payout_records)}'
        }), 404
    
    try:
        data = request.get_json()
        new_payout = data.get('payout')
        
        if new_payout is None:
            return jsonify({
                'error': 'Missing required field: payout',
                'message': 'Request body must include payout value'
            }), 400
        
        if not isinstance(new_payout, (int, float)):
            return jsonify({
                'error': 'Invalid payout value',
                'message': 'Payout must be a number'
            }), 400
        
        # Update the payout in memory
        old_payout = payout_records[patient_id - 1]['payout']
        payout_records[patient_id - 1]['payout'] = round(new_payout, 2)
        
        return jsonify({
            'patient_id': patient_id,
            'old_payout': old_payout,
            'new_payout': round(new_payout, 2),
            'currency': 'USD',
            'message': f'Payout updated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500


@app.route('/api/patients', methods=['GET'])
def get_all_patients():
    """
    Get all patient payout records.
    
    Returns:
        JSON response with all patient records
    """
    return jsonify({
        'total_records': len(payout_records),
        'patients': [
            {
                'patient_id': i + 1,
                'age': patient['age'],
                'gender': patient['gender'],
                'codes_completed': patient['codes_completed'],
                'bundle': patient['bundle'],
                'payout': patient['payout']
            }
            for i, patient in enumerate(payout_records)
        ]
    }), 200


@app.route('/api/patients/filter', methods=['GET'])
def filter_patients():
    """
    Filter patients by age, gender, or payout range.
    
    Query Parameters:
        - age: Exact age to filter by
        - gender: Gender to filter by (Male/Female)
        - min_payout: Minimum payout amount
        - max_payout: Maximum payout amount
    
    Returns:
        JSON response with filtered patient records
    """
    age = request.args.get('age', type=int)
    gender = request.args.get('gender')
    min_payout = request.args.get('min_payout', type=float, default=0)
    max_payout = request.args.get('max_payout', type=float, default=float('inf'))
    
    filtered_patients = []
    
    for i, patient in enumerate(payout_records):
        # Apply filters
        if age and patient['age'] != age:
            continue
        if gender and patient['gender'].lower() != gender.lower():
            continue
        if not (min_payout <= patient['payout'] <= max_payout):
            continue
        
        filtered_patients.append({
            'patient_id': i + 1,
            'age': patient['age'],
            'gender': patient['gender'],
            'codes_completed': patient['codes_completed'],
            'bundle': patient['bundle'],
            'payout': patient['payout']
        })
    
    return jsonify({
        'total_records': len(filtered_patients),
        'filters': {
            'age': age,
            'gender': gender,
            'min_payout': min_payout,
            'max_payout': max_payout
        },
        'patients': filtered_patients
    }), 200


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    Get statistics about all patient payouts.
    
    Returns:
        JSON response with payout statistics
    """
    payouts = [p['payout'] for p in payout_records]
    
    return jsonify({
        'total_records': len(payout_records),
        'total_payout': round(sum(payouts), 2),
        'average_payout': round(sum(payouts) / len(payouts), 2) if payouts else 0,
        'min_payout': round(min(payouts), 2) if payouts else 0,
        'max_payout': round(max(payouts), 2) if payouts else 0
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response indicating API is running
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Payout API is running',
        'total_patients': len(payout_records)
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    print("Starting Payout API Server...")
    print("Available endpoints:")
    print("  GET /api/health - Health check")
    print("  GET /api/patient/<id> - Get payout for a specific patient")
    print("  POST /api/patient/<id>/payout - Update payout for a patient")
    print("  GET /api/patients - Get all patients")
    print("  GET /api/patients/filter - Filter patients by criteria")
    print("  GET /api/statistics - Get payout statistics")
    app.run(debug=True, host='0.0.0.0', port=5000)
