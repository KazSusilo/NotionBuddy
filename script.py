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

# Load API key and Database ID from .env file
load_dotenv()
SOURCE_DATABASE_ID = os.getenv("SOURCE_DATABASE_ID")
TARGET_DATABASE_ID = os.getenv("TARGET_DATABASE_ID")

"""Extracts the 'block-sets' pairs from the given rows (database)"""
def extract_block_sets_reps(content):
    data = []
    rows = content
    for row in rows:
        block_id = row["id"]
        properties = row["properties"]
        if ( #[col_name][col_type]
            properties["Block"]["title"] and 
            properties["Sets"]["number"] and
            properties["Reps"]["number"]
        ):    
            block = properties["Block"]["title"][0]["text"]["content"]
            sets = properties["Sets"]["number"]
            reps = properties["Reps"]["number"]
            data.append((block_id, block, sets, reps))
    return data

def gym_database_properties():
    payload = {
        "properties": {
            "": {"checkbox": {}},  # Unnamed checkbox column
            "BlockSet": {"title": {}},  # BlockSet as Title
            "Reps": {"number": {}},
            "lbs": {"number": {}},
            "Volume": {"formula": {"expression": "prop(\"Reps\") * prop(\"lbs\")"}},
            "Pass/Fails": {"rich_text": {}},
            "Notes": {"rich_text": {}}
        }
    }
    return payload["properties"]


"""Syncs target_database to source_database, creating blockSet, reps, and relation"""
def sync_databases(gym_database_id, data):
    for block_id, block, sets, reps in data:
        BlockSet_ids = []
        
        # Create BlockSet items in WDB-G and auto populate reps from WDB
        for i in range(1, sets + 1):
            BlockSet = f"{block}{i}"
            content = {
                "properties": {
                    "BlockSet": {"title": [{"text": {"content": BlockSet}}]},
                    "Reps": {"number": reps}
                },
            }
            BlockSet_id = append_DB_item(gym_database_id, content["properties"])
            BlockSet_ids.append({"id": BlockSet_id})

        # Add BlockSet items to Record Relation in 'WDB'
        content = {
            "properties": {
                "Record": {
                    "relation": BlockSet_ids
                }
            }
        }
        update_DB_item(block_id, content["properties"])

def sync_workouts():
    """Synchronize all workouts in page
        * Must have source_databases created
        * Must have target_databases created
    """
    return

def sync_workout_week():
    """Synchronize a weeks worth of workouts
        * Must have a week's worth of source_databases predefined
        * Must have a week's worth of target_databases predefined
        * Creates all the BlockSet items in respective target_databases
        * Relates all BlockSet items back to respective source_databases
    """
    # Get workout database details
    ### Dynamically get Source_DB
    workout_database_id = SOURCE_DATABASE_ID
    workout_database_name, parent_page_id = get_DB_metadata(workout_database_id)
    
    # Creates '-G' database
    ### New DB needs correct column(property) order, column size, and sort 
    new_page_id = create_page(parent_page_id, "Week X")
    gym_database_name = f"{workout_database_name}-T"
    gym_database_id = create_DB(new_page_id, gym_database_name, gym_database_properties())

    # Create and append BlockSet data
    content = get_DB_content(workout_database_id)
    block_sets_data = extract_block_sets_reps(content)
    sync_databases(workout_database_id, gym_database_id, block_sets_data)

def sync_workout():
    """Synchronize a workout
        * Must have a source_database predefined
        * Must have a target_database predefined
        * Creates all the BlockSet items in target_database
        * Relates all BlockSet items back to source_database
    """
    content = get_DB_content(SOURCE_DATABASE_ID)
    data = extract_block_sets_reps(content)
    sync_databases(TARGET_DATABASE_ID, data)

if __name__ == "__main__":
    sync_workout()