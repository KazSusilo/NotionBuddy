import os
import requests
import json
from dotenv import load_dotenv

# Load API key and Database ID from .env file
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

# Notion API Headers
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def create_page(parent_page_id, page_name):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {
            "title": {"title": [{"text": {"content": page_name}}]}
        }
    }
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    if response.status_code != 200:
        print("Error creating page:", response.text)
        return None
    return response.json()["id"]

"""Fetches the rows of the given database(id)"""
def get_database_content(database_id):
    # Notion API REQUIRES 'post' for querying databases, even if only reading
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        print("Error fetching database:", response.text)
        return None
    return response.json().get("results", [])

"""Fetches the metadata of the given database(id)"""
def get_database_metadata(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Error fetching database metadata:", response.text)
        return None, None
    data = response.json()
    database_name = data["title"][0]["text"]["content"]
    parent_page_id = data["parent"]["page_id"]  # page where database is
    return database_name, parent_page_id

def append_database_item(database_id, content):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": content
    }
    response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
    if response.status_code != 200:
        print("append_database_item failed", response.text)
    return response.json()["id"]


def update_database_item(item_id, content):
    url = f"https://api.notion.com/v1/pages/{item_id}"
    payload = {
        "properties": content
    }
    response = requests.patch(url, headers=HEADERS, data=json.dumps(payload))
    if response.status_code != 200:
        print("update_database_item failed", response.text)
    return