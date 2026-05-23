from flask import Flask, jsonify, request
import json
import random
import string
from datetime import datetime, timedelta
import requests

try:
    from flask_cors import CORS
except ImportError:
    print("ERROR: flask-cors not installed!")
    print("Run: pip install flask-cors")
    exit(1)

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/marketplace/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# API Server URL for patient payouts
API_SERVER_URL = "http://localhost:5000"

# Available activities and their attributes
ACTIVITIES = {
    "gym": {
        "name": "Gym Membership",
        "description": "Access to state-of-the-art fitness facilities",
        "icon": "🏋️",
        "discount_amount": 15,
        "max_redemptions": 100
    },
    "pilates": {
        "name": "Pilates Classes",
        "description": "Professional pilates instruction and classes",
        "icon": "🧘",
        "discount_amount": 25,
        "max_redemptions": 50
    },
    "spa": {
        "name": "Spa & Wellness",
        "description": "Relaxing spa treatments and wellness services",
        "icon": "💆",
        "discount_amount": 35,
        "max_redemptions": 30
    },
    "yoga": {
        "name": "Yoga Sessions",
        "description": "Guided yoga classes for all levels",
        "icon": "🧘‍♀️",
        "discount_amount": 20,
        "max_redemptions": 75
    },
    "swimming": {
        "name": "Swimming Pool",
        "description": "Olympic-size swimming pool access",
        "icon": "🏊",
        "discount_amount": 12,
        "max_redemptions": 120
    },
    "nutrition": {
        "name": "Nutrition Counseling",
        "description": "Professional nutrition and diet planning",
        "icon": "🥗",
        "discount_amount": 40,
        "max_redemptions": 40
    }
}

# Store for issued coupons (in production, use a database)
issued_coupons = {}


def generate_coupon_code(activity_id: str) -> str:
    """Generate a unique coupon code."""
    prefix = activity_id[:3].upper()
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{random_suffix}"


def get_coupon_key(patient_id: int, activity_id: str) -> str:
    """Generate a key for storing coupon info."""
    return f"patient_{patient_id}_{activity_id}"


def update_patient_payout_in_api(patient_id: int, new_payout: float) -> bool:
    """
    Update patient payout in the API server.
    
    Args:
        patient_id: The ID of the patient
        new_payout: The new payout amount
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.post(
            f'{API_SERVER_URL}/api/patient/{patient_id}/payout',
            json={'new_payout': new_payout},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"✅ Updated patient {patient_id} payout in API server: ${new_payout}")
            return True
        else:
            print(f"⚠️  API server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Failed to update patient payout in API server: {e}")
        return False


@app.route('/api/marketplace/activities', methods=['GET', 'OPTIONS'])
def get_activities():
    """
    Get list of available activities in the marketplace.
    
    Returns:
        JSON response with all available activities
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    activities_list = []
    for activity_id, activity_info in ACTIVITIES.items():
        activities_list.append({
            'id': activity_id,
            'name': activity_info['name'],
            'description': activity_info['description'],
            'icon': activity_info['icon'],
            'discount_amount': activity_info['discount_amount']
        })
    
    return jsonify({
        'error': False,
        'total_activities': len(activities_list),
        'activities': activities_list
    }), 200


@app.route('/api/marketplace/redeem', methods=['POST', 'OPTIONS'])
def redeem_activity():
    """
    Redeem an activity for a patient and get a coupon code.
    Also updates the patient's payout in the API server.
    
    Request body:
    {
        "patient_id": 1,
        "activity_id": "gym",
        "current_payout": 79.00
    }
    
    Returns:
        JSON response with coupon code and adjusted payout
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        patient_id = data.get('patient_id')
        activity_id = data.get('activity_id')
        current_payout = data.get('current_payout')
        
        # Validation
        if not patient_id or not activity_id or current_payout is None:
            return jsonify({
                'error': True,
                'message': 'Missing required fields: patient_id, activity_id, current_payout'
            }), 400
        
        if activity_id not in ACTIVITIES:
            return jsonify({
                'error': True,
                'message': f'Activity "{activity_id}" not found'
            }), 404
        
        activity = ACTIVITIES[activity_id]
        coupon_key = get_coupon_key(patient_id, activity_id)
        
        # Check if patient already has a coupon for this activity
        if coupon_key in issued_coupons:
            return jsonify({
                'error': True,
                'message': f'Patient already has a coupon for {activity["name"]}'
            }), 409
        
        # Generate coupon code
        coupon_code = generate_coupon_code(activity_id)
        
        # Calculate new payout (subtract discount)
        discount_amount = activity['discount_amount']
        new_payout = current_payout - discount_amount
        
        # Ensure payout doesn't go negative
        if new_payout < 0:
            new_payout = 0
        
        # Update patient payout in API server
        api_update_success = update_patient_payout_in_api(patient_id, new_payout)
        
        # Store coupon info
        issued_coupons[coupon_key] = {
            'coupon_code': coupon_code,
            'activity_id': activity_id,
            'activity_name': activity['name'],
            'patient_id': patient_id,
            'discount_amount': discount_amount,
            'original_payout': current_payout,
            'new_payout': round(new_payout, 2),
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'api_synced': api_update_success
        }
        
        return jsonify({
            'error': False,
            'message': 'Coupon successfully generated',
            'coupon_code': coupon_code,
            'activity_name': activity['name'],
            'discount_amount': discount_amount,
            'original_payout': current_payout,
            'new_payout': round(new_payout, 2),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'api_synced': api_update_success
        }), 201
    
    except Exception as e:
        print(f"❌ Error in redeem_activity: {str(e)}")
        return jsonify({
            'error': True,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/marketplace/patient/<int:patient_id>/payout', methods=['GET'])
def get_patient_adjusted_payout(patient_id):
    """
    Get the adjusted payout for a patient from the API server.
    
    Args:
        patient_id: The ID of the patient
    
    Returns:
        JSON response with adjusted payout from API server
    """
    try:
        response = requests.get(f'{API_SERVER_URL}/api/patient/{patient_id}/payout')
        
        if response.status_code == 200:
            api_data = response.json()
            return jsonify({
                'error': False,
                'patient_id': patient_id,
                'adjusted_payout': api_data.get('payout', 0)
            }), 200
        else:
            return jsonify({
                'error': True,
                'message': f'Patient {patient_id} not found in API server'
            }), 404
    except Exception as e:
        return jsonify({
            'error': True,
            'message': f'Failed to fetch payout from API server: {str(e)}'
        }), 500


@app.route('/api/marketplace/patient/<int:patient_id>/coupons', methods=['GET'])
def get_patient_coupons(patient_id):
    """
    Get all coupons issued to a patient.
    
    Args:
        patient_id: The ID of the patient
    
    Returns:
        JSON response with all coupons for the patient
    """
    coupons = []
    
    for coupon_key, coupon_data in issued_coupons.items():
        if coupon_data['patient_id'] == patient_id:
            coupons.append(coupon_data)
    
    return jsonify({
        'error': False,
        'patient_id': patient_id,
        'total_coupons': len(coupons),
        'coupons': coupons
    }), 200

@app.route('/api/marketplace/patient/<int:patient_id>/coupons/<string:activity_id>', methods=['GET'])
def get_patient_coupon(patient_id, activity_id):
    """
    Get coupons issued to a patient based on coupon key.
    
    Args:
        patient_id: The ID of the patient
    
    Returns:
        JSON response with coupon for the patient
    """
    coupon_key = get_coupon_key(patient_id, activity_id)
    print(f"Testing coupon key: {coupon_key}")
    if coupon_key not in issued_coupons.keys():
        return jsonify({
            'error': True,
            'message': f'No coupon found for patient {patient_id}'
        }), 404
    

    print(f"✅ Coupon provided: {issued_coupons[coupon_key]['coupon_code']} for patient {patient_id}")

    return jsonify({
        'error': False,
        'patient_id': patient_id,
        'coupon_code': issued_coupons[coupon_key]['coupon_code'],
        'activity_name': issued_coupons[coupon_key]['activity_name'],
        'discount_amount': issued_coupons[coupon_key]['discount_amount'],
        'original_payout': issued_coupons[coupon_key]['original_payout'],
        'new_payout': issued_coupons[coupon_key]['new_payout'],
        'expires_at': issued_coupons[coupon_key]['expires_at']
    }), 200

@app.route('/api/marketplace/health', methods=['GET', 'OPTIONS'])
def health_check():
    """
    Health check endpoint for the marketplace server.
    
    Returns:
        JSON response indicating API is running
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    # Try to reach API server
    api_healthy = False
    try:
        response = requests.get(f'{API_SERVER_URL}/api/health', timeout=2)
        api_healthy = response.status_code == 200
    except:
        api_healthy = False
    
    return jsonify({
        'status': 'healthy',
        'message': 'Marketplace API is running',
        'total_activities': len(ACTIVITIES),
        'total_coupons_issued': len(issued_coupons),
        'api_server_connected': api_healthy
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': True,
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': True,
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    print("="*60)
    print("Starting Marketplace Server...")
    print("="*60)
    print(f"\nAPI Server URL: {API_SERVER_URL}")
    print("\nAvailable endpoints:")
    print("  GET  http://localhost:6000/api/marketplace/health")
    print("  GET  http://localhost:6000/api/marketplace/activities")
    print("  POST http://localhost:6000/api/marketplace/redeem")
    print("  GET  http://localhost:6000/api/marketplace/patient/<id>/payout")
    print("  GET  http://localhost:6000/api/marketplace/patient/<id>/coupons")
    print("\nCORS enabled for all routes")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=6000)
