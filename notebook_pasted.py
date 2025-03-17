import requests
import time
import json

from bs4 import BeautifulSoup

base_url = "https://j-archive.com/"

# GET EVERY SEASON
list_seasons_URL = base_url + "listseasons.php"
list_seasons_page = requests.get(list_seasons_URL)
soup = BeautifulSoup(list_seasons_page.content, "html.parser")

seasons_json_array = []
seasons_trs = soup.find_all("tr")
for season_tr in seasons_trs:
    # init new episode json object
    season_json = {"name": None, "from_date": None, "to_date": None, "URL": None, "episodes": []}

    #print(season_tr)

    # get 'a' tag for ID, air date, and URL
    a_tag = season_tr.find("a")
    #print(a_tag)
    #season_json["id"] = a_tag.string.split(",")[0].lstrip("#")
    #season_json["air_date"] = a_tag.string[-10:]
    season_json["URL"] = base_url + a_tag["href"]
    season_json["name"] = a_tag.string

    # get 'td' tag for episode name
    td = season_tr.find_all('td')[1]
    string = td.string.lstrip().rstrip()
    if string.find(" to ") > 0:
        dates = string.split(" to ")
        #print(dates)
        season_json["from_date"] = dates[0]
        season_json["to_date"] = dates[1]

    # append episode json to array
    seasons_json_array.append(season_json)

#print(seasons_json_array)


# GET A SEASON'S EPISODES

for season in seasons_json_array:

    season_episodes_URL = season["URL"]
    season_episodes_page = requests.get(season_episodes_URL)
    soup = BeautifulSoup(season_episodes_page.content, "html.parser")

    episodes_json_array = []
    episodes = soup.find_all("tr")
    for episode in episodes:
        # init new episode json object
        episode_json = {"id": None, "name": None, "air_date": None, "URL": None}

        # get 'a' tag for ID, air date, and URL
        a_tag = episode.find("a")
        if a_tag.string is not None:
            episode_json["id"] = a_tag.string.split(",")[0].lstrip("#")
            episode_json["air_date"] = a_tag.string[-10:]
        episode_json["URL"] = base_url + a_tag["href"]

        # get 'td' tag for episode name
        td = episode.find_all('td')[1]
        string = td.string.lstrip().rstrip()
        episode_json["name"] = string

        # append episode json to array
        episodes_json_array.append(episode_json)
    
    # wait one second as to not get blocked from the website
    time.sleep(0.5)

    season["episodes"] = episodes_json_array


with open("data/seasons.json", "w") as file:
    json.dump(seasons_json_array, file, indent=4)