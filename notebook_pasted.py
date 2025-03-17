import requests
import time
import json
import re

from bs4 import BeautifulSoup

base_url = "https://j-archive.com/"

def sanitize_filename(filename):
    # Remove any characters not allowed in filenames (Windows/Linux/Mac)
    return re.sub(r'[<>:"/\\|?*]', '', filename)


# GET EVERY SEASON
list_seasons_URL = base_url + "listseasons.php"
list_seasons_page = requests.get(list_seasons_URL)
soup = BeautifulSoup(list_seasons_page.content, "html.parser")

seasons_json_array = []
seasons_trs = soup.find_all("tr")
for season_tr in seasons_trs:
    # init new episode json object
    season_json = {"name": None, "from_date": None, "to_date": None, "URL": None, "file_path": None, "episodes": []}

    #print(season_tr)

    # get 'a' tag for ID, air date, and URL
    a_tag = season_tr.find("a")
    #print(a_tag)
    #season_json["id"] = a_tag.string.split(",")[0].lstrip("#")
    #season_json["air_date"] = a_tag.string[-10:]
    season_json["URL"] = base_url + a_tag["href"]

    if a_tag.string is None:
        a_tag.string = "NoName"
    season_name = sanitize_filename(a_tag.string)
    season_name = season_name.replace(" ", "")
    season_json["name"] = sanitize_filename(season_name)

    # get 'td' tag for episode name
    td = season_tr.find_all('td')[1]
    string = td.string.lstrip().rstrip()
    if string.find(" to ") > 0:
        dates = string.split(" to ")
        #print(dates)
        season_json["from_date"] = dates[0]
        season_json["to_date"] = dates[1]

    # append episode json to array
    season_json["file_path"] = f"data/seasons/{season_json["name"]}"
    seasons_json_array.append(season_json)

print(seasons_json_array)

with open("data/seasons.json", "w") as file:
    json.dump(seasons_json_array, file, indent=4)


# GET A SEASON'S EPISODES
import os

for season in seasons_json_array:

    season_episodes_URL = season["URL"]
    season_episodes_page = requests.get(season_episodes_URL)
    soup = BeautifulSoup(season_episodes_page.content, "html.parser")
    
    folder_path = f"data/seasons/{season["name"]}"

    # Create the folder (if it doesn't exist)
    os.makedirs(folder_path, exist_ok=True)

    episodes_json_array = []
    episodes_json_array_with_game_data = []
    episodes = soup.find_all("tr")

    count = 0
    total_per_season = 1
    for episode in episodes:
        if count >= total_per_season:
            break
        # init new episode json object
        episode_json = {"id": None, "name": None, "air_date": None, "URL": None, "file_path": None, "game_data": None}

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

        ########################
        ### GET JEOPARDY Q/A ###
        ########################

        episode_url = episode_json["URL"]
        file_path = f"{folder_path}/episode_{episode_json["id"]}.json"
        
        # make request before status check
        try:
            response = requests.get(episode_url, timeout=5)  # Set timeout
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {episode_url}: {e}")
            continue


        if response.status_code != 200: # status check
            print(f"HTTP request unsuccessful for {episode_url}")
            continue # skips to next episode

        soup = BeautifulSoup(response.content, "html.parser")  # Parse the HTML

        jeopardy_round = soup.find("div", id="jeopardy_round")
        double_jeopardy_round = soup.find("div", id="double_jeopardy_round")
        final_jeopardy_round = soup.find("div", id="final_jeopardy_round")

        if jeopardy_round:
            single_categories = [cat.text.strip() for cat in jeopardy_round.find_all("td", class_="category_name")]
        if double_jeopardy_round:
            double_categories = [cat.text.strip() for cat in double_jeopardy_round.find_all("td", class_="category_name")]
        if final_jeopardy_round:
            final_category = [cat.text.strip() for cat in final_jeopardy_round.find_all("td", class_="category_name")]

        clues = soup.find_all("td", class_="clue_text")

        # Initialize game_data
        game_data = {"Jeopardy Round": {}}

        # Helper function to parse clue IDs
        def parse_clue_id(clue_id):
            parts = clue_id.split("_")
            if len(parts) < 4:
                return None, None
            return int(parts[2]), int(parts[3])  # Extract X (category) and Y (row)

        # Loop through all clues
        for clue in soup.find_all("td", class_="clue_text"):
            clue_id = clue.get("id", "No ID")
            clue_text = clue.text.strip()

            # Parse clue ID to get category (X) and row index (Y)
            X, Y = parse_clue_id(clue_id)
            if X is None or Y is None:
                continue  # Skip invalid clues

            # Get the actual category name
            category = single_categories[X - 1] if 1 <= X <= len(single_categories) else "Unknown Category"

            # Generate the corresponding answer ID
            answer_id = clue_id.replace("clue_", "clue_", 1) + "_r"
            answer_tag = soup.find(id=answer_id)
            answer = answer_tag.find("em", class_="correct_response").text.strip() if answer_tag else "No Answer"

            # Ensure category exists in game_data
            if category not in game_data["Jeopardy Round"]:
                game_data["Jeopardy Round"][category] = []

            # Store the clue in game_data
            game_data["Jeopardy Round"][category].append({
                "value": Y * 200,  # Convert row index to clue value
                "question": clue_text,
                "answer": answer
            })

        #print(f"Game data for {episode_json["id"]}: {episode_json["game_data"]}")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(game_data, f, indent=4)
            print(f"Saved episode {episode_json["id"]} to {file_path}")
        

        # append episode json to array
        episodes_json_array.append(episode_json)
        episode_json["game_data"] = game_data
        episodes_json_array_with_game_data.append(episode_json)

        count += 1
    
    # wait one second as to not get blocked from the website
    #time.sleep(0.1)

    season["episodes"] = episodes_json_array
    

with open("data/all_data.json", "w") as file:
    json.dump(seasons_json_array, file, indent=4)