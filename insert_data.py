import os
from dotenv import load_dotenv
import oracledb
import pandas as pd 

# loard the dotenv file
load_dotenv()

user = os.getenv("ORACLE_USER")
password = os.getenv("ORACLE_PASS")
dsn = os.getenv("ORACLE_DSN")

try: # try/except block for connecting to oracle db
    conn = oracledb.connect(f"{user}/{password}@{dsn}")
    print("Connected!")
except oracledb.DatabaseError as e:
    print("Connection failed:", e)

# load the CSVs into pandas dataframes
games_df = pd.read_csv('data/csv/clean_games.csv')
#make sure the air date stays a datetime object when reloading the csv
games_df['air_date'] = pd.to_datetime(games_df['air_date'], errors='coerce').dt.date
categories_df = pd.read_csv('data/csv/clean_categories.csv')
clues_df = pd.read_csv('data/csv/clean_clues.csv')

# Cleaning (again, even if it's from cleaned CSV)
for col in ['value', 'clue_text', 'correct_response']:
    clues_df[col] = clues_df[col].fillna('').astype(str).str.strip()

# now lets convert each DF into lists of dicts
games_data = games_df.to_dict(orient='records')
categories_data = categories_df.to_dict(orient='records')
clues_data = clues_df.to_dict(orient='records')


print(type(clues_data))
print(type(clues_data[0]))


# create the cursor object for executing SQL statements
cursor = conn.cursor()

# Insert data into the 'games' table
games_insert_query = """
    INSERT INTO games (game_id, air_date, season) 
    VALUES (:game_id, :air_date, :season)
"""
cursor.executemany(games_insert_query, games_data)

# Insert data into the 'categories' table
categories_insert_query = """
    INSERT INTO categories (category_id, game_id, round_name, category_name) 
    VALUES (:category_id, :game_id, :round_name, :category_name)
"""
cursor.executemany(categories_insert_query, categories_data)

# Insert data into the 'clues' table
clues_insert_query = """
    INSERT INTO clues (clue_id, category_id, game_id, value, clue_text, correct_response) 
    VALUES (:clue_id, :category_id, :game_id, :value, :clue_text, :correct_response)
"""
cursor.executemany(clues_insert_query, clues_data)

# commit the transactions to the database
conn.commit()

# close the cursor and connection
cursor.close()
conn.close()

print("Data inserted successfully!")