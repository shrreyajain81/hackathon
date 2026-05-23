import csv
import json
from typing import Dict, List, Optional, Tuple
from emr_payout_mapper import EMRPayoutMapper


class BundlePayoutCalculator:
    """
    Calculates payout for medical procedures based on CPT codes and optional bundles.
    
    A bundle is a predefined set of CPT codes that must all be completed to receive
    the full payout. If codes don't match the bundle exactly, no payout is given.
    """
    
    def __init__(self, emr_mapper: EMRPayoutMapper):
        """
        Initialize the calculator with an EMR payout mapper.
        
        Args:
            emr_mapper: EMRPayoutMapper instance containing CPT code to payout mappings
        """
        self.emr_mapper = emr_mapper
        self.records: List[Dict] = []
    
    def _parse_codes(self, codes_string: str) -> set:
        """
        Parse a comma-separated string of CPT codes into a set.
        
        Args:
            codes_string: Comma-separated CPT codes (e.g., "CPT12847, CPT58923")
        
        Returns:
            Set of cleaned CPT codes
        """
        if not codes_string or not codes_string.strip():
            return set()
        
        codes = [code.strip() for code in codes_string.split(',')]
        return {code for code in codes if code}
    
    def load_from_csv(self, csv_file_path: str, skip_header: bool = True) -> None:
        """
        Load bundle payout records from a CSV file.
        
        CSV Format:
        - Column 1: Age
        - Column 2: Gender
        - Column 3: Codes Completed (comma-separated CPT codes)
        - Column 4: Original Code Bundle (comma-separated CPT codes, optional)
        
        Args:
            csv_file_path: Path to the CSV file
            skip_header: If True, skips the first row
        
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If required columns are missing
        """
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                if skip_header:
                    next(reader, None)
                
                for row_num, row in enumerate(reader, start=2 if skip_header else 1):
                    if len(row) < 3:
                        raise ValueError(f"Row {row_num} has fewer than 3 columns")
                    
                    try:
                        age = int(row[0].strip()) if row[0].strip().isdigit() else None
                    except ValueError:
                        raise ValueError(f"Row {row_num}: Age '{row[0]}' is not a valid integer")
                    
                    gender = row[1].strip() if row[1].strip().isprintable() else None
                    codes_completed = row[2].strip()
                    bundle = row[3].strip() if len(row) > 3 else None
                    
                    record = {
                        'age': age,
                        'gender': gender,
                        'codes_completed': codes_completed,
                        'bundle': bundle if bundle else None
                    }
                    self.records.append(record)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    def calculate_payout(self, codes_completed: str, bundle: Optional[str] = None) -> float:
        """
        Calculate the payout for a record based on completed codes and optional bundle.
        
        Logic:
        - If no bundle is provided: Sum payout values for all completed codes
        - If bundle is provided:
          - If completed codes match bundle exactly: Sum payout values for all codes
          - If completed codes don't match bundle: Return 0 (bundle not fulfilled)
        
        Args:
            codes_completed: Comma-separated CPT codes that were completed
            bundle: Optional comma-separated CPT codes that represent the full bundle
        
        Returns:
            Total payout amount
        """
        completed_set = self._parse_codes(codes_completed)
        
        # If no bundle specified, just sum the payouts for completed codes
        if bundle is None:
            return self._sum_payouts(completed_set)
        
        # If bundle is specified, check if completed codes match the bundle exactly
        bundle_set = self._parse_codes(bundle)
        
        if completed_set != bundle_set:
            # Codes don't match the bundle, no payout
            return 0.0
        
        # Codes match the bundle, return sum of all payouts
        return self._sum_payouts(completed_set)
    
    def _sum_payouts(self, codes: set) -> float:
        """
        Sum the payout values for a set of CPT codes.
        
        Args:
            codes: Set of CPT codes
        
        Returns:
            Total payout amount
        """
        total = 0.0
        for code in codes:
            payout = self.emr_mapper.get_payout(code)
            if payout is not None:
                total += payout
            else:
                print(f"Warning: CPT code '{code}' not found in mapper")
        
        return total
    
    def process_record(self, record: Dict) -> Dict:
        """
        Process a single record and calculate its payout.
        
        Args:
            record: Dictionary with keys: age, gender, codes_completed, bundle
        
        Returns:
            Dictionary with original record data plus calculated payout
        """
        payout = self.calculate_payout(
            record['codes_completed'],
            record.get('bundle')
        )
        
        result = self._get_specialized_tokens(record, payout)
        return result
    
    def _get_specialized_tokens(self, record: Dict, payout: float) -> Dict:
        """
        Get specialized tokens from the record.
        
        Args:
            record: Dictionary with keys: age, gender, codes_completed, bundle
            payout: Total payout amount
        
        Returns:
            Dictionary with original record data
        """
        result = record.copy()
        if result.get('age') is not None:
            payout *= (1+ (record['age'] / 100))
        
        if result.get('gender') == 'F':
            payout *= 1.1
        
        result['payout'] = int(payout) + int(payout % 5 > 0)
        return result
    
    def process_all_records(self) -> List[Dict]:
        """
        Process all loaded records and calculate payouts.
        
        Returns:
            List of records with calculated payouts
        """
        return [self.process_record(record) for record in self.records]
    
    def save_results_to_json(self, output_path: str, results: List[Dict]) -> None:
        """
        Save processed records with payouts to a JSON file.
        
        Args:
            output_path: Path where the JSON file will be saved
            results: List of processed record dictionaries
        """
        if not results:
            print("No results to save")
            return
        
        json_data = []
        for result in results:
            json_record = {
                'age': result['age'],
                'gender': result['gender'],
                'codes_completed': result['codes_completed'],
                'bundle': result['bundle'],
                'payout': round(result['payout'], 2)
            }
            json_data.append(json_record)
        
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2)
    
    def get_statistics(self, results: List[Dict]) -> Dict:
        """
        Get statistics about the processed results.
        
        Args:
            results: List of processed record dictionaries
        
        Returns:
            Dictionary containing statistics
        """
        if not results:
            return {
                "total_records": 0,
                "total_payout": 0,
                "average_payout": 0,
                "records_with_zero_payout": 0
            }
        
        payouts = [r['payout'] for r in results]
        zero_payout_count = sum(1 for p in payouts if p == 0)
        
        return {
            "total_records": len(results),
            "total_payout": round(sum(payouts), 2),
            "average_payout": round(sum(payouts) / len(payouts), 2),
            "records_with_zero_payout": zero_payout_count,
            "min_payout": round(min(payouts), 2),
            "max_payout": round(max(payouts), 2)
        }


# Example usage
if __name__ == "__main__":
    # Load the EMR payout mapper
    mapper = EMRPayoutMapper("emr_codes.csv")
    mapper.load_from_csv(skip_header=True)
    
    # Create bundle payout calculator
    calculator = BundlePayoutCalculator(mapper)
    
    # Example 1: Manual calculation
    print("=== Manual Calculation Examples ===\n")
    
    # No bundle - just sum the payouts
    payout1 = calculator.calculate_payout("CPT12847, CPT58923")
    print(f"Payout for CPT12847, CPT58923 (no bundle): ${payout1:.2f}")
    
    # With bundle - codes match
    payout2 = calculator.calculate_payout(
        codes_completed="CPT12847, CPT58923, CPT50062",
        bundle="CPT12847, CPT58923, CPT50062"
    )
    print(f"Payout for CPT12847, CPT58923, CPT50062 (matched bundle): ${payout2:.2f}")
    
    # With bundle - codes don't match
    payout3 = calculator.calculate_payout(
        codes_completed="CPT12847, CPT58923",
        bundle="CPT12847, CPT58923, CPT50062"
    )
    print(f"Payout for CPT12847, CPT58923 (incomplete bundle): ${payout3:.2f}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Load from CSV and process - Matching records
    print("=== Processing Matching Records from CSV ===\n")
    
    try:
        calculator.load_from_csv("bundle_records_matching.csv", skip_header=True)
        results = calculator.process_all_records()
        
        # Display results
        for i, result in enumerate(results, 1):
            bundle_info = f" (Bundle: {result['bundle']})" if result['bundle'] else ""
            print(f"{i}. Age: {result['age']}, Gender: {result['gender']}, "
                  f"Codes: {result['codes_completed']}{bundle_info} => ${result['payout']:.2f}")
        
        # Show statistics
        stats = calculator.get_statistics(results)
        print("\n=== Statistics for Matching Records ===")
        print(f"Total Records: {stats['total_records']}")
        print(f"Total Payout: ${stats['total_payout']:.2f}")
        print(f"Average Payout: ${stats['average_payout']:.2f}")
        print(f"Records with Zero Payout: {stats['records_with_zero_payout']}")
        print(f"Min Payout: ${stats['min_payout']:.2f}")
        print(f"Max Payout: ${stats['max_payout']:.2f}")
        
        # Save results to JSON
        calculator.save_results_to_json("bundle_payout_results_matching.json", results)
        print("\nResults saved to bundle_payout_results_matching.json")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Load from CSV and process - Non-matching records
    print("=== Processing Non-Matching Records from CSV ===\n")
    
    calculator.records = []  # Reset records
    
    try:
        calculator.load_from_csv("emr_records.csv", skip_header=True)
        results = calculator.process_all_records()
        
        # Display results
        for i, result in enumerate(results, 1):
            bundle_info = f" (Bundle: {result['bundle']})" if result['bundle'] else ""
            print(f"{i}. Age: {result['age']}, Gender: {result['gender']}, "
                  f"Codes: {result['codes_completed']}{bundle_info} => ${result['payout']:.2f}")
        
        # Show statistics
        stats = calculator.get_statistics(results)
        print("\n=== Statistics for Non-Matching Records ===")
        print(f"Total Records: {stats['total_records']}")
        print(f"Total Payout: ${stats['total_payout']:.2f}")
        print(f"Average Payout: ${stats['average_payout']:.2f}")
        print(f"Records with Zero Payout: {stats['records_with_zero_payout']}")
        print(f"Min Payout: ${stats['min_payout']:.2f}")
        print(f"Max Payout: ${stats['max_payout']:.2f}")
        
        # Save results to JSON
        calculator.save_results_to_json("bundle_payout_results.json", results)
        print("\nResults saved to bundle_payout_results.json")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
