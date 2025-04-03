import json
from processor import DataProcessor

if __name__ == "__main__":
    # Load the data
    with open("data/all_data.json", "r", encoding="utf-8") as f:
        all_data = json.load(f)

    # Process and export
    processor = DataProcessor()
    processor.process(all_data)
    processor.save_all_csvs()

    print("CSV export complete.")
