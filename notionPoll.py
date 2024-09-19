import time
import requests
from notion_client import Client
import os
from dotenv import load_dotenv
from datetime import datetime

from script import vpype_layout_paragraph, send_gcode_file_to_printer

# Load environment variables from .env file
load_dotenv()

# Notion API Token
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
PARENT_DATABASE_ID = "261c30aa25d649898320e41125292a9a"

# Initialize the Notion client
notion = Client(auth=NOTION_API_TOKEN)

# Dictionary to keep track of the previous state of each entry
last_entry_states = {}

def get_inner_database_id():
    response = notion.databases.query(
        **{
            "database_id": PARENT_DATABASE_ID,
        }
    )
    # Assuming the first (and only) entry in the parent database contains the inner database
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    if response['results']:
        for r in response['results']:
            if(r['properties']['Month']['number'] == current_month and r['properties']['Year']['number']):
                inner_page_id = r['id']
                pageContent = notion.blocks.children.list(inner_page_id)
                for block in pageContent['results'] :
                    if isinstance(block, dict) and block.get('type') == 'child_database':
                        return block['id']
        print("cant find month db")
        return None
    else:
        raise ValueError("No inner database found in the parent database")

# Poll the Notion database for entries where the 'switch' property changed to True
def check_for_switch_changes(databse_id):
    response = notion.databases.query(
        **{
            "database_id": databse_id,
        }
    )
    return response

# Function to process the page text
def process_page_text(page_id):
    page = notion.pages.retrieve(page_id=page_id)
    
    # Extract the relevant text from the page properties (adjust this based on your page structure)
    text_blocks = notion.blocks.children.list(page_id)
    all_text = []
    for block in text_blocks['results']:
        if block['type'] == 'paragraph':
            all_text.append(block['paragraph']['rich_text'][0]['plain_text'])
    
    return "\n".join(all_text)

# Polling the Notion database periodically
def poll_notion_database():
    global last_entry_states
    inner_database_id = get_inner_database_id()

    while True:
        result = check_for_switch_changes(inner_database_id)
        if result['results']:
            #print(result['results'])
            for entry in result['results']:
                page_id = entry['id']
                # print("-----------")
                # print(entry)
                print_value = entry['properties']['Print']['checkbox']
                
                # Get the last known switch state
                last_print_value = last_entry_states.get(page_id, None)
                
                # Only process the entry if the switch changed from False to True
                if last_print_value == False and print_value == True:
                    print(f"Switch changed to True for page: {page_id}")
                    
                    # Fetch and process the text from the page
                    page_text = process_page_text(page_id)
                    print(f"Page text:\n{page_text}")
                    
                    # Call your custom function to handle the page text
                    gcode_stuff(page_text)
                
                # Update the last known switch value for the next polling cycle
                last_entry_states[page_id] = print_value
        
        # Poll every 60 seconds
        time.sleep(5)

# Define what you want to do with the page text
def gcode_stuff(text):
    # Example: print the text (you can store it, trigger other actions, etc.)
    print(f"Extracted text: {text}")
    output_file = "entry.gcode"
    vpype_layout_paragraph(text, text_size=15, width=200, height=200, output_file=output_file)
    
    port = "/dev/ttyUSB0"
    send_gcode_file_to_printer(output_file, port)
    # Add your custom processing logic here (e.g., store the text, call an API, etc.)

# Start polling the database
if __name__ == "__main__":
    poll_notion_database()
