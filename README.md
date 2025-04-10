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
| round_name   | string     | "Double Jeopardy", etc.       |
| category_name| string     | The category title           |

### `clues`
| Column           | Type       | Notes                            |
|------------------|------------|----------------------------------|
| clue_id          | string PK  | Hashed from category + text      |
| category_id      | string FK  | References `categories.category_id` |
| game_id          | string FK  | Redundant for easier joins       |
| value            | number     | Dollar amount of clue            |
| clue_text        | clob       | The Jeopardy-style clue text     |
| correct_response | clob       | The correct answer               |

---

## Project Structure

data/
├── all_data.json         # Combined game data
├── seasons.json          # Metadata index of seasons
├── seasons/              # Raw scraped episodes by season
└── csv/
    ├── games.csv
    ├── categories.csv
    ├── clues.csv
    ├── clean_games.csv
    ├── clean_categories.csv
    └── clean_clues.csv

scripts/
├── scraper.py            # Scrapes J! Archive to JSON
├── processor.py          # Flattens JSON into relational format
├── write_to_csv.py       # Outputs raw CSVs
├── clean_data.py         # Validates and cleans data
├── insert_data.py        # Inserts into Oracle DB
└── .env                  # (not tracked) Oracle credentials



---
## Step 1: Scrape the Data
To scrape Jeopardy! game data from the J! Archive and organize it into structured JSON:
1. Run the scraper script (make sure you're connected to the internet):
--This will:
---Crawl the J! Archive episode list by season
----Save game data into individual episode JSON files (e.g., data/seasons/Season41/episode_9291.json)
----Combine all games into a single JSON file:
----data/all_data.json — for processing
----Also generate a season index:
----data/seasons.json — for metadata & file paths
## Step 2: Process and Export to CSV:
Once all_data.json is generated, use the write_to_csv.py script to flatten and export the data into structured CSVs.
1. Run the write_to_csv script
-How It Works
--The script uses a custom DataProcessor class (defined in processor.py) to:
---Extract and flatten nested game data
---Assign unique IDs using MD5 hashing for categories and clues
## Note: 
    -we initially used category_id and clue text to generate unique hashes for clue ids.
    however we found that jeopardy reuses clue text in some categories
    *see: Show #8674 - Thursday, June 30, 2022, **"STAN" COUNTRIES** for $800 and $1000 respectively.
    we encountered 404 hash collisions with this logic. we revised the logic to generate hashes off of 
    an enumerated unique value.
    -there were several reasons why we had to add enumeration to the clues to give them uniqueness:
        -there were boards and categories where clues were blank
        -reused categories and boards
        -combinations of these factors led to a minimum of 118 colliding md5 hash ids 
---Normalize the data into three lists: games, categories, and clues
---Export these lists into relational CSVs inside data/csv/

This will generate:
-data/csv/games.csv
-data/csv/categories.csv
-data/csv/clues.csv

Each file is ready for import into an Oracle database or use with R for analysis.

## IMPORTANT! Make sure all_data.json exists before running this step.

## Step 3: Set Up Oracle XE:

This project uses Oracle DB, if you dont already have a local or cloud SQL db set up, I recomend Oracle XE. Install and follow the instructions on Oracle's website for guidance.

-To connect to the Oracle XE database without exposing credentials, this project uses environment variables and the python-dotenv package.
-Create a .env file in your project root with your Oracle credentials:

ORACLE_USER=jeopardy_user
ORACLE_PASS=YourSecurePassword
ORACLE_DSN=localhost/XEPDB1

# note: XEPDB1 is the default "pluggable database" name in Oracle XE.

When you connect to Oracle with cx_Oracle, you have to specify:
"username/password@host/service_name"
The service_name here is XEPDB1, which tells Oracle:
"Connect me to that specific pluggable database."
If you used a different Oracle edition or made a custom pluggable DB, you'd use that name instead.

-Be sure to add .env to your .gitignore to avoid exposing secrets in version control.

# Running the Script in VSCode with WSL: If you're using VSCode with a WSL terminal, you might need to run your insert_data.py script from Windows command prompt instead of the WSL terminal. Alternatively, you may need to install Oracle for Linux if you're running the script from a Linux environment.

https://oracle.github.io/python-oracledb/
for information on the oracledb driver

## Step 4: Insert data

You should be able to run the script as is, assuming you have properly installed and connected to you local database. 

# What this does: 
-Loads the CSVs into a pandas dataframe
-does some last minute cleaning 
-df.to_dict(orient='records') converts each row in the DataFrame into a dictionary, where the column names are the keys.
    -This is useful because executemany() expects a list of dictionaries, where each dictionary contains values to be inserted into the database, with the keys matching the placeholders in your SQL query.

Execute bulk inserts into Oracle using cursor.executemany()

Commit and close the connection

The script assumes that your database schema already exists with matching tables.

## Bonus: Validation & Logging
The project includes robust defensive programming features:

-Uniqueness checks on IDs to prevent silent data corruption

-Logging for dropped records, conflicts, and type issues

-Automatic null-handling and string standardization for Oracle compatibility

-Tested against 500k+ clue entries, ensuring stable long-term performance

# Jeopardy Category Theme Analysis (R Project)

This project uses an Oracle-based Jeopardy database to explore and visualize recurring category themes across seasons. It generates two primary outputs:

1. **Word Cloud** of the most common category terms
2. **Bar Chart Race** showing how popular category themes evolve over time

---

## Outputs

### 1. Word Cloud
- Generated using [`wordcloud2`](https://cran.r-project.org/web/packages/wordcloud2/)
- Saved as an **HTML widget** (PNG exportable)

**File:**  
data/theme_wordcloud.html

pgsql
Copy
Edit

### 2. Bar Chart Race (Wide Format CSV)
- Each row represents a season (by air date of first episode)
- Each column is a frequent category word
- Cell values = number of times the word appears in that season’s category titles

**File:**  
data/seasonal_charts/theme_word_race_wide.csv

yaml
Copy
Edit

> **NOTE:** Some bar chart race tools like Flourish or AlienArt may require you to **swap the axis** (transpose rows and columns) before importing this CSV.

---

## 🔧 Setup Instructions

### 1. Set Working Directory

Update your working directory to the root of your local project:

setwd("~/jeopardy_scraper")  # Update this path as needed
2. Install Required R Packages
Install the following packages before running the script:

r
Copy
Edit
install.packages(c(
  "DBI", "odbc", "dplyr", "tidytext", "ggplot2", 
  "wordcloud2", "stringr", "forcats", 
  "htmlwidgets", "tidyr", "lubridate"
))
3. Set Secure Oracle Environment Variables
You must provide your Oracle credentials securely via environment variables.

Option A – In your R session:

r
Copy
Edit
Sys.setenv(ORACLE_USER = "your_username")
Sys.setenv(ORACLE_PASS = "your_password")
Sys.setenv(ORACLE_DSN  = "your_dsn_name")
Option B – In a .Renviron file: Add this to your ~/.Renviron file:

ini
Copy
Edit
ORACLE_USER=your_username
ORACLE_PASS=your_password
ORACLE_DSN=your_dsn_name
Restart RStudio after editing .Renviron.

#Visualizations
Word Cloud
Automatically generated using the top 150 most frequent category words

Filters out stop words like "the", "of", etc.

Font used: Korinna (Jeopardy-style) — must be installed on your system

To export a PNG:

Open the theme_wordcloud.html in your browser

Take a screenshot or export using browser tools or widget functions

Bar Chart Race
Produces a wide-format CSV file

Use in Flourish, AlienArt, or similar web animation tools

Includes proper date formatting for smooth timeline animation

Can be styled with captions in your web platform of choice (e.g. Canva + Flourish)

#Folder Structure
cpp
Copy
Edit
jeopardy_scraper/
├── data/
│   ├── csv/
│   │   └── theme_frequency.csv
│   └── seasonal_charts/
│       ├── theme_word_race_wide.csv
│       └── theme_word_race_long.csv (optional, not generated here)
├── theme_wordcloud.html
├── theme_word_analysis.R
└── README.md

# Final Notes
Ensure that Korinna is installed on your system for best word cloud appearance

Bar chart race tools may have strict formatting requirements; test a few rows first

This project is a great foundation for deeper theme-based analysis of Jeopardy data
