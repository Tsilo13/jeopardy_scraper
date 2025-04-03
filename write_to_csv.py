import json
from processor import DataProcessor
import os

if __name__ == "__main__":
    # check if data folder exists
    os.makedirs("data/csv", exist_ok=True)
    # Load the data
    with open("data/all_data.json", "r", encoding="utf-8") as f:
        all_data = json.load(f)
    
    #flatten list of seasons into list of games
    #using nested list comprehension
    flat_data = [game for season in all_data for game in season]

    # Process and export
    processor = DataProcessor()
    processor.process(flat_data)
    processor.save_all_csvs()

    print("CSV export complete.")
