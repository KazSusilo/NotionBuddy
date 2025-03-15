import os
from dotenv import load_dotenv
from notion_actions import (
    get_database_content as get_DB_content, 
    get_database_metadata as get_DB_metadata,
    create_database as create_DB,
    create_page,
    append_database_item as append_DB_item,
    sort_database as sort_DB,
    update_database_item as update_DB_item,
)

load_dotenv()
CYCLES_DB_ID = os.getenv("CYCLES_DATABASE_ID")
WEEKS_DB_ID = os.getenv("WEEKS_DATABASE_ID")

def sync_cycle_weeks():
    data = ''
    append_database_item(CYCLES_DB_ID, data)

def process_data(data):
    

if __name__ == "__main__":
    sync_cycle_weeks()