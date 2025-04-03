# Jeopardy Data Pipeline (Python → CSV → Oracle → R)

This project scrapes and processes Jeopardy! game data from [J! Archive](https://j-archive.com), structures it into relational form, and prepares it for database and analytics work. The primary focus is on data wrangling with Python, exporting to CSV, and setting up for SQL + R-based analysis.

---

## Data Structure

The processed data is modeled as three normalized tables:

### `games`
| Column     | Type      | Notes                  |
|------------|-----------|------------------------|
| game_id    | string PK | J! Archive game ID     |
| air_date   | date      | Episode air date       |
| season     | integer   | Extracted from file path |

### `categories`
| Column       | Type       | Notes                        |
|--------------|------------|------------------------------|
| category_id  | string PK  | Hashed from game+round+name  |
| game_id      | string FK  | References `games.game_id`   |
| round_name   | string     | "Jeopardy Round", etc.       |
| category_name| string     | The category title           |

### `clues`
| Column           | Type       | Notes                            |
|------------------|------------|----------------------------------|
| clue_id          | string PK  | Hashed from category + text      |
| category_id      | string FK  | References `categories.category_id` |
| game_id          | string FK  | Redundant for easier joins       |
| value            | number     | Dollar amount of clue            |
| clue_text        | string     | The Jeopardy-style clue text     |
| correct_response | string     | The correct answer               |

---

## Project Structure

data/ ├── all_data.json # All game data combined ├── seasons.json # Season/episode metadata ├── seasons/└──episode#.json
└── csv/ ├── games.csv ├── categories.csv |── clues.csv 
scraper.py # Scrapes J! Archive for jeaopardy data and stores it in vraious json structures in data folder 
processor.py # DataProcessor class (cleans + exports) 
write_to_csv.py # Script to create CSVs from all_data.json 
README.md # You're here


---
## Step 1: Scrape the Data
To scrape Jeopardy! game data from the J! Archive and organize it into structured JSON:
1. Step 1: Run the scraper script (make sure you're connected to the internet):
--This will:
---Crawl the J! Archive episode list by season
----Save game data into individual episode JSON files (e.g., data/seasons/Season41/episode_9291.json)
----Combine all games into a single JSON file:
----data/all_data.json — for processing
----Also generate a season index:
----data/seasons.json — for metadata & file paths
## Step 2: Process and Export to CSV:
Once all_data.json is generated, use the write_to_csv.py script to flatten and export the data into structured CSVs.
-How It Works
--The script uses a custom DataProcessor class (defined in processor.py) to:
---Extract and flatten nested game data
---Assign unique IDs using MD5 hashing for categories and clues
---Normalize the data into three lists: games, categories, and clues
---Export these lists into relational CSVs inside data/csv/

This will generate:
-data/csv/games.csv
-data/csv/categories.csv
-data/csv/clues.csv

Each file is ready for import into an Oracle database or use with R for analysis.

## IMPORTANT! Make sure all_data.json exists before running this step.




