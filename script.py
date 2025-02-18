import os
import requests
import json
from dotenv import load_dotenv

# Load API key and Database ID from .env file
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
SOURCE_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
TARGET_DATABASE_ID = "19d1f53b7fd98110a8c9fb3f0b622892"

# Notion API Headers
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

"""Fetches the rows of the given database"""
def get_database_rows(database_id):
    # Notion API REQUIRES 'post' for querying databases, even if only reading
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        print("Error fetching database:", response.text)
        return None
    return response.json().get("results", [])

"""Extracts the 'block-sets' pairs from the given rows (database)"""
def extract_block_sets(rows):
    data = []
    for row in rows:
        properties = row["properties"]
        if properties["Block"]["title"] and properties["Sets"]["number"]:    # [col_name][col_type]
            block = properties["Block"]["title"][0]["text"]["content"]
            sets = properties["Sets"]["number"]
            data.append((block, sets))
    return data


def get_database_metadata(database_id):
    return

def create_gym_database(page_id, gym_database_name):
    payload = {
        "title": [{"text": {"content": gym_database_name}}],
        "properties": {
            "": {"checkbox": {}},
            "BlockSet": {"title": {}},
            "Reps": {"number": {}},
            "lbs": {"number": {}},
            "kg": {"formula": {"expression": "prop('lbs') / 2.205"}},
            "Pass/Fails": {"rich_text": {}},
        },
    }

"""Creates the 'BlockSets' rows in '-G' database and adds them to 'Records' in workout database"""
def create_block_sets(workout_database_id, gym_database_id, block_sets_data):
    for block, sets, in block_sets_data:
        for i in range(1, sets + 1):
            content = f"{block}{i}"
            populate_gym_database(gym_database_id, content)
        #populate_workout_database(workout_database_id, content)

def populate_gym_database(gym_database_id, content):
    url = f"https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": gym_database_id},
        "properties": {
            "Block/Set": {"title": [{"text": {"content": content}}]}
        }
    }
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    if response.status_code == 200:
        print("gymSuccess")
    else:
        print("gymFailed")

def main():
    # Find workout_database(s)
    workout_database_id = SOURCE_DATABASE_ID
    
    # Obtains data from workout_database(s)
    rows = get_database_rows(workout_database_id)
    block_sets_data = extract_block_sets(rows)
    
    # Creates '-G' database(s)
    """
    gym_database_id = create_gym_database(workout_database_id)
    workout_database_name, page_id = get_database_metadata(workout_database_id)
    gym_database_name = f"{workout_database_name}-G"
    gym_database_id = create_gym_database(page_id, gym_database_name)
    """
    gym_database_id = TARGET_DATABASE_ID

    # Create block_sets for gym and workout database
    create_block_sets(workout_database_id, gym_database_id, block_sets_data)

if __name__ == "__main__":
    main()