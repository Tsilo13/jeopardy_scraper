import pandas as pd
from functools import wraps
import logging

logging.basicConfig(
    filename='data_cleaning.log',
    filemode='a',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def validate_dataframe(required_columns, unique_columns=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            df = func(*args, **kwargs)
            missing = [col for col in required_columns if col not in df.columns]
            # check for missing columns/ null values and raise error if found
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            if df.isnull().any().any():
                raise ValueError(f"DataFrame has null values after cleaning: {func.__name__}")
            # check for uniqueness
            if unique_columns:
                for col in unique_columns:
                    if not df[col].is_unique:
                        raise ValueError(f"Column '{col}' is not unique in {func.__name__}")
            return df
        return wrapper
    return decorator

@validate_dataframe(
    required_columns=['game_id','air_date', 'season'],
    unique_columns=['game_id']
    )
def clean_games_df(df):
    df['game_id'] = df['game_id'].astype(int)
    df['air_date'] = pd.to_datetime(df['air_date'], errors='coerce')
    null_dates = df[df['air_date'].isna()]
    for game_id in null_dates['game_id']:
        logger.info(f"clean_games_df: Dropped game_id: {game_id} with null 'air_date'")
    df['season'] = df['season'].astype(int)
    return df.dropna(subset=['air_date'])

@validate_dataframe(
    required_columns=['category_id','game_id', 'round_name', 'category_name'],
    unique_columns=['category_id']
    )
def clean_categories_df(df):
    df = df.fillna('')
    df['category_id'] = df['category_id'].astype(int)
    df['game_id'] = df['game_id'].astype(int)
    df['round_name'] = df['round_name'].str.strip()
    df['category_name'] = df['category_name'].str.strip()
    return df

@validate_dataframe(
    required_columns=['clue_id' ,'category_id', 'game_id', 'value', 'clue_text', 'correct_response'],
    unique_columns=['clue_id']
    )
def clean_clues_df(df):
    df = df.fillna('')
    df['clue_id'] = df['clue_id'].astype(int)
    df['category_id'] = df['category_id'].astype(int)
    df['game_id'] = df['game_id'].astype(int)
    # just convert all clue values to str, considering values are fixed 
    # to accomodate final jeopardy
    for col in ['value', 'clue_text', 'correct_response']:
        df[col] = df[col].astype(str).str.strip() 
    return df

def main():
    logger.info("Reading Data")
    games = pd.read_csv('data/csv/games.csv')
    categories = pd.read_csv('data/csv/categories.csv')
    clues = pd.read_csv('data/csv/clues.csv')

    logger.info("Cleaning...")
    clean_games = clean_games_df(games)
    clean_categories = clean_categories_df(categories)
    clean_clues = clean_clues_df(clues)

    logger.info("Saving cleaned data")
    clean_games.to_csv('data/csv/clean_games.csv', index=False, encoding="utf-8")
    clean_categories.to_csv('data/csv/clean_categories.csv', index=False, encoding="utf-8")
    clean_clues.to_csv('data/csv/clean_clues.csv', index=False, encoding="utf-8")

    logger.info("Data has been successfully cleaned and saved!")
    


if __name__ == '__main__':
    main()
    
    


