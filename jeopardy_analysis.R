#install libraries
library(DBI) #database interface
library(odbc) #for connecting oracle db
library(dplyr) #for dataframe manipulation
library(tidytext) #for analyzing category names
library(ggplot2) #for plotting
library(wordcloud2) #for making wordlcouds
library(stringr) #for us on string data
library(forcats) #for labeling and ordering
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
#you'll have to screenshot the result for use outside rstudio


 
 
