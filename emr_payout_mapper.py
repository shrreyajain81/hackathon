import csv
from typing import Dict, Tuple


class EMRPayoutMapper:
    """
    Handles reading EMR codes from a CSV file and mapping them to payout assets.
    
    CSV Format:
    - Column 1: EMR Code
    - Column 2: Asset Value (payout amount)
    """
    
    def __init__(self, csv_file_path: str):
        """
        Initialize the mapper with a CSV file path.
        
        Args:
            csv_file_path: Path to the CSV file containing EMR codes and asset values
        """
        self.csv_file_path = csv_file_path
        self.emr_mapping: Dict[str, float] = {}
    
    def load_from_csv(self, skip_header: bool = False) -> None:
        """
        Load EMR codes and payout assets from a CSV file.
        
        Args:
            skip_header: If True, skips the first row (assumes it's a header)
        
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV doesn't have the required columns
        """
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                # Skip header if requested
                if skip_header:
                    next(reader, None)
                
                for row_num, row in enumerate(reader, start=1):
                    if len(row) < 2:
                        raise ValueError(f"Row {row_num} has fewer than 2 columns")
                    
                    emr_code = row[0].strip()
                    
                    try:
                        asset_value = float(row[1].strip())
                    except ValueError:
                        raise ValueError(f"Row {row_num}: Asset value '{row[1]}' is not a valid number")
                    
                    if emr_code:  # Only add non-empty codes
                        self.emr_mapping[emr_code] = asset_value
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
    
    def get_payout(self, emr_code: str) -> float:
        """
        Get the payout asset value for a specific EMR code.
        
        Args:
            emr_code: The EMR code to look up
        
        Returns:
            The payout asset value, or None if the code doesn't exist
        """
        return self.emr_mapping.get(emr_code.strip())
    
    def assign_payout(self, emr_code: str, asset_value: float) -> None:
        """
        Manually assign or update a payout asset value for an EMR code.
        
        Args:
            emr_code: The EMR code to assign
            asset_value: The payout asset value
        """
        if not isinstance(asset_value, (int, float)):
            raise ValueError(f"Asset value must be a number, got {type(asset_value)}")
        
        self.emr_mapping[emr_code.strip()] = float(asset_value)
    
    def get_all_mappings(self) -> Dict[str, float]:
        """
        Get all EMR code to payout asset mappings.
        
        Returns:
            Dictionary of all EMR code to asset value mappings
        """
        return self.emr_mapping.copy()
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the loaded EMR codes and payouts.
        
        Returns:
            Dictionary containing statistics (count, total, average, min, max)
        """
        if not self.emr_mapping:
            return {"count": 0, "total": 0, "average": 0, "min": None, "max": None}
        
        values = list(self.emr_mapping.values())
        return {
            "count": len(self.emr_mapping),
            "total": sum(values),
            "average": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }
    
    def save_to_csv(self, output_path: str) -> None:
        """
        Save the current EMR to payout mappings to a CSV file.
        
        Args:
            output_path: Path where the CSV file will be saved
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['EMR Code', 'Payout Asset'])
            for emr_code, asset_value in sorted(self.emr_mapping.items()):
                writer.writerow([emr_code, asset_value])


# Example usage
if __name__ == "__main__":
    # Create mapper instance
    mapper = EMRPayoutMapper("emr_codes.csv")
    
    # Load from CSV (skip header if present)
    mapper.load_from_csv(skip_header=True)
    
    # Look up a specific EMR code
    payout = mapper.get_payout("EMR001")
    print(f"Payout for EMR001: ${payout}")
    
    # Manually assign a payout
    mapper.assign_payout("EMR999", 500.00)
    
    # Get all mappings
    print("\nAll Mappings:")
    for code, value in mapper.get_all_mappings().items():
        print(f"  {code}: ${value:.2f}")
    
    # Get statistics
    stats = mapper.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total EMR Codes: {stats['count']}")
    print(f"  Total Payout: ${stats['total']:.2f}")
    print(f"  Average Payout: ${stats['average']:.2f}")
    print(f"  Min Payout: ${stats['min']:.2f}")
    print(f"  Max Payout: ${stats['max']:.2f}")
    
    # Save to output file
    mapper.save_to_csv("output_emr_payouts.csv")
