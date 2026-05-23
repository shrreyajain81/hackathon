import requests
import json
from typing import Optional, Dict, Any


class PayoutAPIClient:
    """
    Client for interacting with the Payout API to retrieve patient payout information.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server (default: localhost:5000)
        """
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the API is healthy and running.
        
        Returns:
            Response data from health check endpoint
        
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            response = requests.get(f"{self.base_url}/api/health", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            raise
    
    def get_patient_payout(self, patient_id: int) -> Dict[str, Any]:
        """
        Get payout information for a specific patient.
        
        Args:
            patient_id: The ID of the patient (1-based index)
        
        Returns:
            Patient payout information
        
        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If patient is not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/patient/{patient_id}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                raise ValueError(response.json()['message'])
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get patient {patient_id}: {e}")
            raise
    
    def get_all_patients(self) -> Dict[str, Any]:
        """
        Get all patient records.
        
        Returns:
            All patient records
        
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            response = requests.get(f"{self.base_url}/api/patients", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get all patients: {e}")
            raise
    
    def filter_patients(
        self,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        min_payout: Optional[float] = None,
        max_payout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Filter patients by various criteria.
        
        Args:
            age: Filter by exact age
            gender: Filter by gender (Male/Female)
            min_payout: Filter by minimum payout amount
            max_payout: Filter by maximum payout amount
        
        Returns:
            Filtered patient records
        
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {}
        if age is not None:
            params['age'] = age
        if gender is not None:
            params['gender'] = gender
        if min_payout is not None:
            params['min_payout'] = min_payout
        if max_payout is not None:
            params['max_payout'] = max_payout
        
        try:
            response = requests.get(
                f"{self.base_url}/api/patients/filter",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to filter patients: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all patient payouts.
        
        Returns:
            Payout statistics
        
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/statistics",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get statistics: {e}")
            raise


def print_patient_payout(patient_data: Dict[str, Any]) -> None:
    """
    Pretty print patient payout information.
    
    Args:
        patient_data: Patient information dictionary
    """
    print("\n" + "="*60)
    print("PATIENT PAYOUT INFORMATION")
    print("="*60)
    print(f"Patient ID:      {patient_data.get('patient_id', 'N/A')}")
    print(f"Age:             {patient_data.get('age', 'N/A')}")
    print(f"Gender:          {patient_data.get('gender', 'N/A')}")
    print(f"Codes Completed: {patient_data.get('codes_completed', 'N/A')}")
    print(f"Bundle:          {patient_data.get('bundle', 'N/A')}")
    print(f"Payout Amount:   ${patient_data.get('payout', 0):.2f} {patient_data.get('currency', 'USD')}")
    print("="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = PayoutAPIClient("http://localhost:5000")
    
    try:
        # Check if API is healthy
        print("Checking API health...")
        health = client.health_check()
        print(f"API Status: {health['status']}")
        print(f"Message: {health['message']}")
        print(f"Total Patients in System: {health['total_patients']}\n")
        
        # Example 1: Get a specific patient's payout (Patient ID 1)
        print("\n--- Example 1: Get Patient #1 Payout ---")
        try:
            patient_1 = client.get_patient_payout(1)
            print_patient_payout(patient_1)
        except ValueError as e:
            print(f"Error: {e}")
        
        # Example 2: Get another patient's payout (Patient ID 3)
        print("\n--- Example 2: Get Patient #3 Payout ---")
        try:
            patient_3 = client.get_patient_payout(3)
            print_patient_payout(patient_3)
        except ValueError as e:
            print(f"Error: {e}")
        
        # Example 3: Filter patients by age
        print("\n--- Example 3: Filter Patients by Age 35 ---")
        filtered = client.filter_patients(age=35)
        print(f"Found {filtered['total_records']} patient(s) with age 35:")
        for patient in filtered['patients']:
            print(f"  Patient #{patient['patient_id']}: Payout = ${patient['payout']:.2f}")
        
        # Example 4: Filter patients by payout range
        print("\n--- Example 4: Filter Patients by Payout Range ($100-$200) ---")
        filtered = client.filter_patients(min_payout=100, max_payout=200)
        print(f"Found {filtered['total_records']} patient(s) with payout between $100-$200:")
        for patient in filtered['patients']:
            print(f"  Patient #{patient['patient_id']}: Age {patient['age']}, Payout = ${patient['payout']:.2f}")
        
        # Example 5: Get statistics
        print("\n--- Example 5: Payout Statistics ---")
        stats = client.get_statistics()
        print(f"Total Records:    {stats['total_records']}")
        print(f"Total Payout:     ${stats['total_payout']:.2f}")
        print(f"Average Payout:   ${stats['average_payout']:.2f}")
        print(f"Min Payout:       ${stats['min_payout']:.2f}")
        print(f"Max Payout:       ${stats['max_payout']:.2f}")
        
        # Example 6: Get all patients
        print("\n--- Example 6: All Patients ---")
        all_patients = client.get_all_patients()
        print(f"Total patients: {all_patients['total_records']}")
        for patient in all_patients['patients']:
            print(f"  Patient #{patient['patient_id']}: Age {patient['age']}, Gender {patient['gender']}, Payout ${patient['payout']:.2f}")
    
    except Exception as e:
        print(f"Fatal error: {e}")
        print("\nMake sure the API server is running!")
        print("Start the server with: python payout_api_server.py")
