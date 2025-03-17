import requests

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
    season_json = {"id": None, "name": None, "air_date": None, "URL": None}

    print(season_tr)

    # get 'a' tag for ID, air date, and URL
    a_tag = season_tr.find("a")
    print(a_tag)
    #season_json["id"] = a_tag.string.split(",")[0].lstrip("#")
    #season_json["air_date"] = a_tag.string[-10:]
    #season_json["URL"] = base_url + a_tag["href"]

    # get 'td' tag for episode name
    td = season_tr.find_all('td')[1]
    string = td.string.lstrip().rstrip()
    season_json["name"] = string

    # append episode json to array
    seasons_json_array.append(season_json)

print(seasons_json_array)





# GET A SEASON'S EPISODES
season_episodes_URL = base_url + "showseason.php?season=33"
season_episodes_page = requests.get(season_episodes_URL)
soup = BeautifulSoup(season_episodes_page.content, "html.parser")

episodes_json_array = []
episodes = soup.find_all("tr")
for episode in episodes:
    # init new episode json object
    episode_json = {"id": None, "name": None, "air_date": None, "URL": None}

    # get 'a' tag for ID, air date, and URL
    a_tag = episode.find("a")
    episode_json["id"] = a_tag.string.split(",")[0].lstrip("#")
    episode_json["air_date"] = a_tag.string[-10:]
    episode_json["URL"] = base_url + a_tag["href"]

    # get 'td' tag for episode name
    td = episode.find_all('td')[1]
    string = td.string.lstrip().rstrip()
    episode_json["name"] = string

    # append episode json to array
    episodes_json_array.append(episode_json)

print(episodes_json_array)




# GET AN EPISODE'S CLUES / ANSWERS
season_33 = base_url + "showseason.php?season=33"
page = requests.get(season_33)
soup = BeautifulSoup(page.content, "html.parser")

episodes_json_array = []
episodes = soup.find_all("tr")
for episode in episodes:
    # init new episode json object
    episode_json = {"id": None, "name": None, "air_date": None, "URL": None, "clues": []}

    # get 'a' tag for ID, air date, and URL
    a_tag = episode.find("a")
    episode_json["id"] = a_tag.string.split(",")[0].lstrip("#")
    episode_json["air_date"] = a_tag.string[-10:]
    episode_json["URL"] = base_url + a_tag["href"]

    # get 'td' tag for episode name
    td = episode.find_all('td')[1]
    string = td.string.lstrip().rstrip()
    episode_json["name"] = string

    # append episode json to array
    episodes_json_array.append(episode_json)

print(episodes_json_array)