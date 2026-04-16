# Notion to G-code

Type a journal entry in Notion and have a pen plotter handwrite it on paper.

![Demo](https://github.com/user-attachments/assets/51bdfdb8-0941-4a09-b654-102c9a651283)

## How It Works

1. **Poll Notion** -- monitors a Notion database for entries with the "Print" checkbox toggled on
2. **Generate G-code** -- converts the entry text into G-code using [vpype](https://github.com/abey79/vpype) and [vpype-gcode](https://github.com/plottertools/vpype-gcode)
3. **Print** -- sends the G-code to a pen plotter over serial

## Setup

### Prerequisites

- Python 3.10+
- A Notion integration token ([create one here](https://www.notion.so/my-integrations))
- A pen plotter connected via USB serial

### Installation

```bash
python -m venv myenv
source myenv/bin/activate
pip install vpype vpype-gcode python-dotenv notion-client pyserial
```

### Configuration

Create a `.env` file in the project root:

```
NOTION_API_TOKEN=your_notion_api_token
PARENT_DATABASE_ID=your_parent_database_id
```

The Notion database should have:
- A `Month` (number) and `Year` (number) property on the parent database
- A child database inside each month's page containing entries
- A `Print` (checkbox) property on each entry

### G-code Profile

Plotter settings are configured in `adjusted.toml`. Edit the offsets, Z heights, and feed rates to match your machine.

## Usage

```bash
source myenv/bin/activate
python notionPoll.py
```

The script polls Notion every 2 seconds. When you check the "Print" box on an entry, it generates G-code and sends it to the plotter.

## Project Structure

```
notionPoll.py    -- Entry point; polls Notion and orchestrates printing
script.py        -- Text-to-gcode generation and serial communication
adjusted.toml    -- vpype-gcode profile for the plotter
```
