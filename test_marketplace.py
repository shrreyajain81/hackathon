"""
Test script to verify marketplace server connectivity
Run this to diagnose connection issues
"""

import requests
import json

MARKETPLACE_URL = "http://localhost:6000"

def test_health():
    """Test if marketplace server is running"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/api/marketplace/health")
        print(f"✅ Marketplace health check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Marketplace health check failed: {e}")
        return False

def test_activities():
    """Test if activities endpoint works"""
    try:
        response = requests.get(f"{MARKETPLACE_URL}/api/marketplace/activities")
        print(f"\n✅ Activities endpoint: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"\n❌ Activities endpoint failed: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    try:
        response = requests.options(f"{MARKETPLACE_URL}/api/marketplace/activities")
        print(f"\n✅ CORS preflight: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        return True
    except Exception as e:
        print(f"\n❌ CORS preflight failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("MARKETPLACE SERVER CONNECTIVITY TEST")
    print("="*60)
    
    print(f"\nTesting connection to: {MARKETPLACE_URL}\n")
    
    # Run tests
    health_ok = test_health()
    activities_ok = test_activities()
    cors_ok = test_cors()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Activities Endpoint: {'✅ PASS' if activities_ok else '❌ FAIL'}")
    print(f"CORS Preflight: {'✅ PASS' if cors_ok else '❌ FAIL'}")
    
    if not health_ok:
        print("\n⚠️  MARKETPLACE SERVER IS NOT RUNNING!")
        print("Start it with: python marketplace_server.py")
    elif not cors_ok:
        print("\n⚠️  CORS IS NOT PROPERLY CONFIGURED!")
        print("Make sure flask-cors is installed: pip install flask-cors")
    elif activities_ok:
        print("\n✅ ALL TESTS PASSED - Everything should work!")
    
    print("="*60)
