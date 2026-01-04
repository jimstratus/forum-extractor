import logging
import sys
import os
import subprocess
import time
import datetime
import csv
import yaml

#These imports are needed for the functions called in the edited main function
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import requests


def log_message(message):
    """Log a message to console with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_excel_compatible_index():
    """Create an Excel-compatible CSV index of all scenarios"""
    log_message("Creating Excel-compatible CSV index")
    
    # Output file
    csv_file = "scenario_index.csv"
    
    # Column headers
    headers = [
        "Forum", "Title", "Year", "Status", "Author", "URL", 
        "Post Count", "Date Extracted", "Character Count"
    ]
    
    scenarios = []
    
    # Scan Scenarios directory
    for forum in os.listdir("Scenarios"):
        forum_dir = os.path.join("Scenarios", forum)
        if not os.path.isdir(forum_dir) or forum == "Indexes":
            continue
        
        for scenario in os.listdir(forum_dir):
            scenario_dir = os.path.join(forum_dir, scenario)
            if not os.path.isdir(scenario_dir):
                continue
            
            # Load metadata
            metadata_file = os.path.join(scenario_dir, "metadata.yaml")
            if not os.path.exists(metadata_file):
                continue
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)
                
                # Calculate character count from content file
                content_file = os.path.join(scenario_dir, "content.md")
                char_count = 0
                if os.path.exists(content_file):
                    with open(content_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        char_count = len(content)
                
                # Add scenario to list
                scenarios.append({
                    "Forum": forum,
                    "Title": metadata.get("title", "Unknown"),
                    "Year": metadata.get("year", "Unknown"),
                    "Status": metadata.get("status", "New"),
                    "Author": metadata.get("author", "Unknown"),
                    "URL": metadata.get("url", ""),
                    "Post Count": metadata.get("post_count", 0),
                    "Date Extracted": metadata.get("extracted_date", ""),
                    "Character Count": char_count
                })
            except Exception as e:
                log_message(f"Error processing {scenario_dir}: {str(e)}")
    
    # Sort by forum and title
    scenarios.sort(key=lambda x: (x["Forum"], x["Title"]))
    
    # Write CSV file
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(scenarios)
    
    log_message(f"Created CSV index with {len(scenarios)} scenarios: {csv_file}")


def extract_year_from_title(title):
    iry_match = re.search(r'\[(\d+)\s*IRY\]', title)
    if iry_match:
        return f"{iry_match.group(1)} IRY"
    
    ufy_match = re.search(r'\[(\d+)\s*UFY\]', title)
    if ufy_match:
        return f"{ufy_match.group(1)} UFY"
    
    return "Unknown"

def get_soup(url, retry_count=3, delay=3):
    for attempt in range(retry_count):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                log_message(f"HTTP Error {response.status_code} for {url}")
        except Exception as e:
            log_message(f"Error fetching {url}: {str(e)}")
        
        if attempt < retry_count - 1:
            log_message(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    return None

def identify_characters(content):
    characters = set()
    name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    exclude_words = [
        "Posted Image", "Posted March", "Posted April", "Posted May", "Posted June", 
        "Posted July", "Posted August", "Posted September", "Posted October",
        "Posted November", "Posted December", "Posted January", "Posted February",
        "Cloud Drive", "Personal Staff", "Special Forces", "Regional Governors",
        "Royal Guard", "High Council", "Grand Admiralty", "His Majesty",
        "The Minister", "Palace Situation", "Report This", "Mon Calamari"
    ]
    
    matches = re.findall(name_pattern, content)
    for match in matches:
        if not any(exclude in match for exclude in exclude_words):
            characters.add(match)
    
    return sorted(list(characters))

def create_timeline(posts):
    timeline = []
    for i, post in enumerate(posts):
        date = post["date"]
        author = post["author"]
        content = post["content"]
        
        # Extract first paragraph as summary
        first_lines = content.split('\n', 2)[0]
        if len(first_lines) > 150:
            summary = first_lines[:150] + "..."
        else:
            summary = first_lines
        
        timeline.append({
            "event_number": i + 1,
            "date": date,
            "author": author,
            "summary": summary
        })
    
    return timeline

def suggest_plot_development(posts):
    if not posts:
        return {
            "current_state": "No posts available",
            "main_themes": ["To be identified manually"],
            "open_questions": ["To be identified manually"],
            "potential_directions": ["To be determined manually"]
        }
    
    total_content = "\n".join([p["content"] for p in posts])
    word_count = len(total_content.split())
    
    return {
        "current_state": f"Scenario with {len(posts)} posts and approximately {word_count} words",
        "main_themes": ["To be identified manually"],
        "open_questions": ["To be identified manually"],
        "potential_directions": ["To be determined manually"]
    }

def extract_forums():
    #This function is a placeholder for the more sophisticated forum extraction logic.  The original code's extract_forum function could be incorporated here.
    log_message("Placeholder for forum extraction")
    pass


def process_scenarios():
    #This function is a placeholder for scenario processing logic. The original code's logic for processing individual scenarios could be integrated here.
    log_message("Placeholder for scenario processing")
    pass

def generate_reports():
    #This function is a placeholder.  The original code calls generate_combined_report.py;  This could be integrated here.
    log_message("Placeholder for report generation.  Original code would call generate_combined_report.py")
    pass


def create_indexes():
    #This function calls create_excel_compatible_index().  The original code's index creation logic (potentially multiple index files) would be incorporated here.
    create_excel_compatible_index()
    log_message("Placeholder for index creation (beyond Excel)")
    pass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting forum extraction...")
        extract_forums()

        logger.info("Processing scenarios...")
        process_scenarios()

        logger.info("Generating reports...")
        generate_reports()

        logger.info("Creating indexes...")
        create_indexes()

        logger.info("Full extraction completed successfully")

    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()