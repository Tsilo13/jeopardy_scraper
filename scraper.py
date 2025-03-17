
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML
import json  # For storing scraped data
import os  # For file operations
import time  # To add delays between requests (avoid being blocked)

URL = "https://www.j-archive.com/showseason.php?season=33"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

base_url = "https://www.j-archive.com/"
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

# print(episodes_json_array)

for episode in episodes_json_array:
    episode_url = episode["URL"]
    file_path = f"data/episode_{"id"}.json"
    
    # make request before status check
    try:
        response = requests.get(episode_url, timeout=5)  # Set timeout
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {episode_url}: {e}")
        continue


    if response.status_code != 200: # status check
        print(f"HTTP request unsuccessful for {episode_url}")
        continue # skips to next episode

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(episode_data, f, indent=4)
        print(f"Saved episode {"id"} to {file_path}")

    soup = BeautifulSoup(response.content, "html.parser")  # Parse the HTML

    jeopardy_round = soup.find("div", id="jeopardy_round")
    double_jeopardy_round = soup.find("div", id="double_jeopardy_round")
    final_jeopardy_round = soup.find("div", id="final_jeopardy_round")

    single_categories = [cat.text.strip() for cat in jeopardy_round.find_all("td", class_="category_name")]
    double_categories = [cat.text.strip() for cat in double_jeopardy_round.find_all("td", class_="category_name")]
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
