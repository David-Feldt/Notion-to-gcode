import time
import os
from datetime import datetime

from notion_client import Client
from dotenv import load_dotenv

from script import vpype_layout_paragraph, send_gcode_file_to_printer

load_dotenv()

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
PARENT_DATABASE_ID = os.getenv('PARENT_DATABASE_ID', '261c30aa25d649898320e41125292a9a')

notion = Client(auth=NOTION_API_TOKEN)

last_entry_states = {}


def get_inner_database_id():
    response = notion.databases.query(database_id=PARENT_DATABASE_ID)

    current_date = datetime.now()
    current_month = current_date.month

    if not response['results']:
        raise ValueError("No inner database found in the parent database")

    for r in response['results']:
        if r['properties']['Month']['number'] == current_month and r['properties']['Year']['number']:
            inner_page_id = r['id']
            page_content = notion.blocks.children.list(inner_page_id)
            for block in page_content['results']:
                if isinstance(block, dict) and block.get('type') == 'child_database':
                    return block['id']

    print("Can't find database for current month")
    return None


def check_for_switch_changes(database_id):
    response = notion.databases.query(database_id=database_id)
    return response


def process_page_text(page_id):
    text_blocks = notion.blocks.children.list(page_id)
    all_text = []
    for block in text_blocks['results']:
        if block['type'] == 'paragraph' and len(block['paragraph']['rich_text']) > 0:
            all_text.append(block['paragraph']['rich_text'][0]['plain_text'])

    return "\n".join(all_text)


def gcode_stuff(text):
    output_file = "entry.gcode"
    vpype_layout_paragraph(text, text_size=15, width=200, height=200, output_file=output_file)

    port = "/dev/ttyUSB0"
    send_gcode_file_to_printer(output_file, port)


def poll_notion_database():
    global last_entry_states
    inner_database_id = get_inner_database_id()
    print("Polling Notion database...")

    while True:
        result = check_for_switch_changes(inner_database_id)
        if result['results']:
            for entry in result['results']:
                page_id = entry['id']
                print_value = entry['properties']['Print']['checkbox']

                last_print_value = last_entry_states.get(page_id, None)

                if last_print_value is False and print_value is True:
                    print(f"Print triggered for page: {page_id}")

                    page_text = process_page_text(page_id)
                    print(f"Processing entry: {page_text[:80]}...")

                    gcode_stuff(page_text)

                last_entry_states[page_id] = print_value

        time.sleep(2)


if __name__ == "__main__":
    poll_notion_database()
