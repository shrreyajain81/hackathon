from flask import Flask, render_template, jsonify, request
import json

app = Flask(__name__, template_folder='templates', static_folder='static')

# API Server URL
API_BASE_URL = "http://localhost:5000"
MARKETPLACE_BASE_URL = "http://localhost:6000"

# Load payout data locally for quick access
try:
    with open("bundle_payout_results.json", "r") as f:
        payout_records = json.load(f)
except FileNotFoundError:
    payout_records = []


@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html', total_patients=len(payout_records))


@app.route('/api/ui/patient/<int:patient_id>')
def get_patient_ui(patient_id):
    """
    Get patient payout information for the UI.
    
    Args:
        patient_id: The ID of the patient (1-based index)
    
    Returns:
        JSON response with patient information
    """
    if patient_id < 1 or patient_id > len(payout_records):
        return jsonify({
            'error': True,
            'message': f'Patient ID {patient_id} not found',
            'valid_range': f'1-{len(payout_records)}'
        }), 404
    
    patient = payout_records[patient_id - 1]
    
    return jsonify({
        'error': False,
        'patient_id': patient_id,
        'age': patient['age'],
        'gender': patient['gender'],
        'codes_completed': patient['codes_completed'],
        'bundle': patient['bundle'],
        'payout': patient['payout'],
        'currency': 'USD'
    }), 200


@app.route('/api/ui/update-patient-payout/<int:patient_id>', methods=['POST'])
def update_patient_payout_ui(patient_id):
    """
    Update patient payout in memory and sync with REST API server.
    
    Args:
        patient_id: The ID of the patient (1-based index)
    
    Request body:
    {
        "payout": 64.00
    }
    
    Returns:
        JSON response with updated payout
    """
    if patient_id < 1 or patient_id > len(payout_records):
        return jsonify({
            'error': True,
            'message': f'Patient ID {patient_id} not found'
        }), 404
    
    try:
        data = request.get_json()
        new_payout = data.get('payout')
        
        if new_payout is None:
            return jsonify({
                'error': True,
                'message': 'Missing required field: payout'
            }), 400
        
        # Update payout in local memory
        old_payout = payout_records[patient_id - 1]['payout']
        payout_records[patient_id - 1]['payout'] = round(new_payout, 2)
        
        # Also update in REST API server
        try:
            import requests
            rest_response = requests.post(
                f'{API_BASE_URL}/api/patient/{patient_id}/payout',
                json={'payout': round(new_payout, 2)},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            print(f"REST API update response: {rest_response.status_code}")
        except Exception as e:
            print(f"Warning: Could not sync with REST API: {e}")
        
        return jsonify({
            'error': False,
            'patient_id': patient_id,
            'old_payout': old_payout,
            'new_payout': round(new_payout, 2),
            'message': 'Payout updated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': True,
            'message': str(e)
        }), 500


@app.route('/api/ui/all-patients')
def get_all_patients_ui():
    """Get all patients for the UI."""
    patients = []
    for i, patient in enumerate(payout_records, 1):
        patients.append({
            'patient_id': i,
            'age': patient['age'],
            'gender': patient['gender'],
            'payout': patient['payout']
        })
    
    return jsonify({
        'error': False,
        'total_records': len(patients),
        'patients': patients
    }), 200


@app.route('/api/ui/statistics')
def get_statistics_ui():
    """Get payout statistics for the UI."""
    if not payout_records:
        return jsonify({
            'error': False,
            'total_records': 0,
            'total_payout': 0,
            'average_payout': 0,
            'min_payout': 0,
            'max_payout': 0
        }), 200
    
    payouts = [p['payout'] for p in payout_records]
    
    return jsonify({
        'error': False,
        'total_records': len(payout_records),
        'total_payout': round(sum(payouts), 2),
        'average_payout': round(sum(payouts) / len(payouts), 2),
        'min_payout': round(min(payouts), 2),
        'max_payout': round(max(payouts), 2)
    }), 200


@app.route('/api/ui/marketplace/activities')
def get_marketplace_activities():
    """
    Proxy endpoint to fetch marketplace activities.
    This allows the UI to call the marketplace server through the UI server.
    """
    try:
        import requests
        response = requests.get(f'{MARKETPLACE_BASE_URL}/api/marketplace/activities')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            'error': True,
            'message': f'Failed to fetch marketplace activities: {str(e)}'
        }), 500


@app.route('/api/ui/marketplace/redeem', methods=['POST'])
def redeem_marketplace_activity():
    """
    Proxy endpoint to redeem a marketplace activity.
    This allows the UI to redeem activities through the UI server.
    """
    try:
        import requests
        data = request.get_json()
        
        response = requests.post(
            f'{MARKETPLACE_BASE_URL}/api/marketplace/redeem',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            'error': True,
            'message': f'Failed to redeem activity: {str(e)}'
        }), 500


@app.route('/api/ui/marketplace/patient/<int:patient_id>/coupons')
def get_patient_coupons_ui(patient_id):
    """
    Proxy endpoint to get patient coupons from marketplace.
    """
    try:
        import requests
        response = requests.get(f'{MARKETPLACE_BASE_URL}/api/marketplace/patient/{patient_id}/coupons')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            'error': True,
            'message': f'Failed to fetch coupons: {str(e)}'
        }), 500
    
@app.route('/api/ui/marketplace/patient/<int:patient_id>/coupons/<string:activity_id>')
def get_patient_coupon_ui(patient_id, activity_id):
    """
    Proxy endpoint to get a specific patient coupon from marketplace.
    """

    try:
        import requests
        response = requests.get(f'{MARKETPLACE_BASE_URL}/api/marketplace/patient/{patient_id}/coupons/{activity_id}')
        print(response.json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            'error': True,
            'message': f'Failed to fetch coupon: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("="*60)
    print("Starting Payout UI Server...")
    print("="*60)
    print("\nUI Dashboard: http://localhost:8000")
    print("\nThis server includes:")
    print("  - Patient payout data (local)")
    print("  - Marketplace integration (proxy to port 6000)")
    print("  - Payout update synchronization")
    print("\nMake sure marketplace server is running on port 6000:")
    print("  python marketplace_server.py")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8000)
