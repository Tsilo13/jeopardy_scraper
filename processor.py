'''
DataProcessor class for making the game tables notes
here im noting the values for the table column assigner
***workflow***
- process all games
    -  xtract data from json and append to lists
- write the lists to csvs using the csv import    
'''
# imports
import re
import hashlib
import csv

class DataProcessor:
    def __init__(self):
        self.games = []
        self.categories = []
        self.clues = []

    # first make a function for extracting a season number from the filepath in the dictionary
    def extract_season_number(self, file_path):
        match = re.search(r'Season(\d+)', file_path)
        return int(match.group(1)) if match else None

    # now make a hash helper fnction for generating unique IDs
    def hash_md5(self, string):
        return hashlib.md5(string.encode()).hexdigest() 

    def process(self, all_data):
        # sample loop for extracting game data     
        for game in all_data: # loop for games table
            file_path = game['file_path']
            if 'Season' not in file_path: # excludes special seasons
                continue
            # data to be extracted
            game_id = game['id']
            air_date = game['air_date']
            season = self.extract_season_number(file_path)

            # add the game info to the games list
            self.games.append({
                "game_id": game_id, #pk
                "air_date": air_date,
                "season": season
            })
            # move to next nested level in json, categories
            for round_name, round_data in game['game_data'].items():
                for category_name, clues in round_data.items():
                    # use the mash_md5 method for cat_id
                    category_id = self.hash_md5(f"{game_id}_{round_name}_{category_name}")
                    # append categories list
                    self.categories.append({
                        "category_id": category_id, #pk
                        "game_id": game_id, #fk
                        "round_name": round_name,
                        "category_name": category_name
                    })

                    # move to clue data
                    for i, clue in enumerate(clues):
                        clue_id = self.hash_md5(f"{game_id}_{round_name}_{category_name}_{clue['value']}_{i}")
                        self.clues.append({
                            "clue_id": clue_id, #pk
                            "category_id": category_id, #fk
                            "game_id": game_id, #fk
                            "value": clue["value"],
                            "clue_text": clue["question"],
                            "correct_response": clue["answer"]
                        })
    def write_csv(self, data, path, keys):
        with open(path, 'w', newline='', encoding= 'utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys) #map keys to columns using DictWriter
            writer.writeheader()#writes the column headers
            writer.writerows(data)#writes the rows
    #add function for writing and saving the csv files
    def save_all_csvs(self):
        self.write_csv(self.games, "data/csv/games.csv", ["game_id", "air_date", "season"])
        self.write_csv(self.categories, "data/csv/categories.csv", ["category_id", "game_id", "round_name", "category_name"])
        self.write_csv(self.clues, "data/csv/clues.csv", ["clue_id", "category_id", "game_id", "value", "clue_text", "correct_response"])