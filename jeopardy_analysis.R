#install libraries
library(DBI) #database interface
library(odbc) #for connecting oracle db
library(dplyr) #for dataframe manipulation
library(tidytext) #for analyzing category names
library(ggplot2) #for plotting
library(wordcloud2) #for making wordlcouds
library(stringr) #for us on string data
library(forcats) #for labeling and ordering
library(htmlwidgets) #for wordcloud widget size
library(tidyr)#for pivoting and word matrix 
library(lubridate)# for custom date time for the bar chart race
#------------------------------------------
#       Connect to the Database
#------------------------------------------
con <- dbConnect(odbc::odbc(), #tells R you'r using ODBC
                  Driver = "Oracle in OraDB21Home1", #your installed oracle driver
                  UID = Sys.getenv("ORACLE_USER"), #username stored securely
                  PWD = Sys.getenv("ORACLE_PASS"),#password    ^       ^
                  DBQ = Sys.getenv("ORACLE_DSN")) #host/service name
#-------------------------------------------
#       Common Category Themes
#-------------------------------------------
#assign category names to categories
categories <- dbGetQuery(con, "SELECT CATEGORY_NAME FROM CATEGORIES")
#tokenize cateogy names
data("stop_words")
category_words <- categories %>%
  unnest_tokens(word, CATEGORY_NAME) %>% #splits each cat into lowercase words
  count(word, sort = TRUE) %>% # count word frequency 
#filter words like "and", "the", "of" with tidytext "stop_words" list
  filter(!word %in% stop_words$word)
#save this data in the project directory
write.csv(category_words, "data/csv/theme_frequency.csv", row.names = FALSE)
#-----------------------------------------------------
#        Theme Word Cloud
#-----------------------------------------------------
#the theme_frequency has over 17_000 entries so you'll need to experiment 
#with the slice size to see what you consider readable
top_themes <- category_words %>%
  slice_max(n, n = 150)

saveWidget(
  wordcloud2(
    data = top_themes, 
    size = 1.2,
    gridSize = 12,
    color = "random-light",
    backgroundColor = "black",
    fontFamily = "Korinna" #requires install (jeopardy clue font)
    
  ),
  "data/theme_wordcloud.html", #save as html in project directory 
  selfcontained = TRUE 
)
#when you are ready to use the image just open the html file and download
#you'll have a stable PNG file for your usecase
#---------------------------------------------------------------------
#                    How Themes evolved over time(bar chart race)
#_____________________________________________________________________
#make sure you have a 'seasonal_charts' or similar folder in your project directory
# assign a table join to 'season_cats'
# Pull categories and air dates
season_cats <- dbGetQuery(con, "
  SELECT g.SEASON, g.AIR_DATE, c.CATEGORY_NAME
  FROM GAMES g
  JOIN CATEGORIES c ON g.GAME_ID = c.GAME_ID
")

# Reduce to 1 AIR_DATE per SEASON (first show of season)
# Get first AIR_DATE per season
season_dates <- season_cats %>%
  group_by(SEASON) %>%
  summarise(time = min(AIR_DATE, na.rm = TRUE))

# Tokenize category names and count words
season_words <- season_cats %>%
  unnest_tokens(word, CATEGORY_NAME) %>%
  filter(!word %in% stop_words$word) %>%
  count(SEASON, word, sort = TRUE)

# Top 10 words per season
top10 <- season_words %>%
  group_by(SEASON) %>%
  slice_max(n, n = 10) %>%
  ungroup()

top10 <- top10 %>%
  left_join(season_dates, by = "SEASON")

# Pivot to wide format
wide_format <- top10 %>%
  rename(date = time) %>%
  select(date, word, n) %>%
  pivot_wider(
    names_from = word,
    values_from = n,
    values_fill = list(n = 0)
  ) %>%
  arrange(date)


# Save
write.csv(wide_format, "data/seasonal_charts/theme_word_race_wide.csv", row.names = FALSE)
#NOTE: you may need to swap the axis of the csv when you use a web app program 
#to make bar chart race

#disconnect
dbDisconnect(con)






 
