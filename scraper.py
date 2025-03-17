
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
    file_path = f"data/episode_{episode["id"]}.json"
    
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

    single_categories = [cat.text.strip() for cat in jeopardy_round.find_all("td", class_="category_name")]
    double_categories = [cat.text.strip() for cat in double_jeopardy_round.find_all("td", class_="category_name")]
    final_category = [cat.text.strip() for cat in final_jeopardy_round.find_all("td", class_="category_name")]
    clues = soup.find_all("td", class_="clue_text")

    # Initialize game_data
    game_data = {"Jeopardy Round": {},
        "Double Jeopardy": {},
        "Final Jeopardy": {}
        }

    # Helper function to parse clue IDs
    def parse_clue_id(clue_id):
        parts = clue_id.split("_")
        if len(parts) < 4:
                return None, None, None

        round_prefix = parts[1] # Round (J, DJ, or FJ)
        X = int(parts[2]) # Cat
        Y = int(parts[3]) # Value

        return round_prefix, X, Y # Extract Round Prefix (J, DJ, FJ) X (category) and Y (row)

    # Loop through all clues
    for clue in soup.find_all("td", class_="clue_text"):
        clue_id = clue.get("id", "No ID")

        if clue_id.endswith("_r"):
             continue

        clue_text = clue.text.strip()

        # Parse clue ID to get category (X) and row index (Y)
        round_prefix, X, Y = parse_clue_id(clue_id)
        if round_prefix is None or X is None or Y is None:
            continue  # Skip invalid clues

        if round_prefix == "J":
            round_name = "Jeopardy Round"
            category_list = single_categories
            clue_value = Y * 200
        elif round_prefix == "DJ":
            round_name = "Double Jeopardy"
            category_list = double_categories
            clue_value = Y * 400
        else:
            continue

        
        category = category_list[X - 1] if 1 <= X <= len(category_list) else "Unknown Category"


        # Generate the corresponding answer ID
        answer_id = clue_id + "_r"
        answer_tag = soup.find(id=answer_id)
        answer = answer_tag.find("em", class_="correct_response").text.strip() if answer_tag else "No Answer"

        # Ensure category exists in game_data
        if category not in game_data[round_name]:
            game_data[round_name][category] = []

        # Store the clue in game_data
        game_data[round_name][category].append({
            "value": clue_value, 
            "question": clue_text,
            "answer": answer
        })

        final_jeopardy_clue = soup.find("td", id="clue_FJ")
        if final_jeopardy_clue:
            fj_text = final_jeopardy_clue.text.strip()

            
            fj_answer_tag = soup.find("td", id="clue_FJ_r")
            fj_answer = fj_answer_tag.find("em", class_="correct_response").text.strip() if answer_tag else "No Answer"


            fj_category = final_category[0] if final_category else "Final Jeopardy"

            game_data["Final Jeopardy"][fj_category] = [{
                "value": "Final Jeopardy",
                "question": fj_text,
                "answer": fj_answer
            }]
        else:
            print("No final Jeopardy question found!")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(game_data, f, indent=4)
        print(f"Saved episode {episode['id']} to {file_path}")
    