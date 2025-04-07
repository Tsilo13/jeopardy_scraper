CREATE TABLE GAMES (
  game_id VARCHAR2(20) PRIMARY KEY,
  AIR_DATE DATE,
  SEASON NUMBER
);

CREATE TABLE categories (
  category_id VARCHAR2(32) PRIMARY KEY,
  game_id VARCHAR2(20),
  round_name VARCHAR2(30),
  category_name VARCHAR2(100),
  FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE clues (
  clue_id VARCHAR2(32) PRIMARY KEY,
  category_id VARCHAR2(32),
  game_id VARCHAR2(20),
  value VARCHAR2(20),
  clue_text CLOB,
  correct_response CLOB,
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (game_id) REFERENCES games(game_id)
);
