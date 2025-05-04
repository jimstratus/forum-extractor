import os
import subprocess
import datetime
import yaml
import csv

def log_message(message):
    """Log a message to console with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def process_forum(forum_name, forum_url, max_topics=3):
    """Process a single forum with limited topics for quick testing"""
    log_message(f"Processing {forum_name} forum ({forum_url})")
    
    # Create directories
    os.makedirs(f"Scenarios/{forum_name}", exist_ok=True)
    os.makedirs(f"Reports/{forum_name}", exist_ok=True)
    
    # Extract sample topics with a smaller timeout and limited number
    cmd = [
        "python", "-c", 
        f"""
import sys
import os
import re
import time
import datetime
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import yaml

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{{timestamp}}] {{msg}}")

def get_soup(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        else:
            log_message(f"HTTP Error {{response.status_code}} for {{url}}")
    except Exception as e:
        log_message(f"Error fetching {{url}}: {{str(e)}}")
    return None

def extract_year_from_title(title):
    iry_match = re.search(r'\\[(\\d+)\\s*IRY\\]', title)
    if iry_match:
        return f"{{iry_match.group(1)}} IRY"
    
    ufy_match = re.search(r'\\[(\\d+)\\s*UFY\\]', title)
    if ufy_match:
        return f"{{ufy_match.group(1)}} UFY"
    
    return "Unknown"

# Sample a few topics from the forum
forum_url = "{forum_url}"
log_message(f"Fetching up to {max_topics} topics from {{forum_url}}")
soup = get_soup(forum_url)
if not soup:
    sys.exit(1)

topics = []
topic_elements = soup.select(".ipsDataItem.ipsDataItem_responsivePhoto")[:int({max_topics})]
for topic in topic_elements:
    title_element = topic.select_one(".ipsDataItem_title a")
    if not title_element:
        continue
    
    title = title_element.text.strip()
    topic_url = title_element.get("href")
    
    author_element = topic.select_one(".ipsDataItem_main .ipsDataItem_meta a")
    author = author_element.text.strip() if author_element else "Unknown"
    
    year = extract_year_from_title(title)
    
    topics.append({{
        "title": title,
        "url": topic_url,
        "author": author,
        "year": year,
        "status": "New"
    }})
    
    log_message(f"Found topic: {{title}}")

# Write topics to a file for processing
os.makedirs("Scenarios/{forum_name}", exist_ok=True)
with open("Scenarios/{forum_name}/topics.yaml", "w", encoding="utf-8") as f:
    yaml.dump(topics, f, default_flow_style=False)

log_message(f"Saved {{len(topics)}} topics for {forum_name}")
        """
    ]
    
    subprocess.run(cmd)
    
    # Check if topics were found
    topics_file = f"Scenarios/{forum_name}/topics.yaml"
    if not os.path.exists(topics_file):
        log_message(f"No topics found for {forum_name}")
        return []
    
    # Load topics
    with open(topics_file, 'r', encoding='utf-8') as f:
        topics = yaml.safe_load(f)
    
    if not topics:
        log_message(f"No topics found for {forum_name}")
        return []
    
    log_message(f"Processing {len(topics)} topics for {forum_name}")
    
    # Process each topic
    for i, topic in enumerate(topics):
        topic_title = topic['title']
        topic_url = topic['url']
        safe_title = "".join(c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in topic_title)
        safe_title = safe_title.replace(' ', '_')
        
        log_message(f"Processing topic {i+1}/{len(topics)}: {topic_title}")
        
        # Create scenario directory
        scenario_dir = f"Scenarios/{forum_name}/{safe_title}"
        os.makedirs(scenario_dir, exist_ok=True)
        
        # Extract basic information and save to files
        content_file = f"{scenario_dir}/content.md"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(f"# {topic_title}\n\n")
            f.write(f"Year: {topic['year']}\n")
            f.write(f"URL: {topic_url}\n")
            f.write(f"Author: {topic['author']}\n\n")
            f.write("Content to be extracted later - this is a quick run.\n")
        
        # Create placeholder files
        with open(f"{scenario_dir}/dramatis_personae.md", 'w', encoding='utf-8') as f:
            f.write(f"# Dramatis Personae - {topic_title}\n\nTo be extracted later.\n")
        
        with open(f"{scenario_dir}/timeline.md", 'w', encoding='utf-8') as f:
            f.write(f"# Timeline of Events - {topic_title}\n\nTo be extracted later.\n")
        
        with open(f"{scenario_dir}/plot_development.md", 'w', encoding='utf-8') as f:
            f.write(f"# Plot Development Suggestions - {topic_title}\n\nTo be determined manually.\n")
        
        # Create metadata file
        metadata = {
            "title": topic_title,
            "year": topic['year'],
            "url": topic_url,
            "author": topic['author'],
            "forum": forum_name,
            "status": "New",
            "post_count": 0,
            "extracted_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "quick_run": True
        }
        
        with open(f"{scenario_dir}/metadata.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False)
        
        # Create a simple report
        report_dir = f"Reports/{forum_name}"
        os.makedirs(report_dir, exist_ok=True)
        report_file = f"{report_dir}/{safe_title}_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# {topic_title}\n\n")
            f.write("## Scenario Metadata\n\n")
            f.write(f"- **Year**: {topic['year']}\n")
            f.write(f"- **Forum**: {forum_name}\n")
            f.write(f"- **Author**: {topic['author']}\n")
            f.write(f"- **Status**: New\n")
            f.write(f"- **URL**: [{topic_url}]({topic_url})\n")
            f.write(f"- **Quick Run**: Yes\n")
            f.write(f"- **Generated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("*This is a placeholder report created during quick run mode.*\n")
    
    return topics

def create_excel_compatible_index(all_topics):
    """Create an Excel-compatible CSV index of all scenarios"""
    log_message("Creating Excel-compatible CSV index")
    
    # Output file
    csv_file = "scenario_index.csv"
    
    # Column headers
    headers = [
        "Forum", "Title", "Year", "Status", "Author", "URL", 
        "Quick Run", "Date Extracted"
    ]
    
    scenarios = []
    
    # Add scenarios to list
    for forum, topics in all_topics.items():
        for topic in topics:
            scenarios.append({
                "Forum": forum,
                "Title": topic["title"],
                "Year": topic["year"],
                "Status": "New",
                "Author": topic["author"],
                "URL": topic["url"],
                "Quick Run": "Yes",
                "Date Extracted": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Sort by forum and title
    scenarios.sort(key=lambda x: (x["Forum"], x["Title"]))
    
    # Write CSV file
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(scenarios)
    
    log_message(f"Created CSV index with {len(scenarios)} scenarios: {csv_file}")

def create_readme():
    """Create a quick README file"""
    content = """# EOTIR Scenario Quick Run

This directory contains a quick extraction of scenarios from the EOTIR forums.

- **Scenarios/** - Contains extracted scenario data
- **Reports/** - Contains simple reports for each scenario
- **scenario_index.csv** - Excel-compatible index of all scenarios

These files are placeholders for demonstration purposes.
"""
    
    with open("README_QUICK_RUN.md", 'w', encoding='utf-8') as f:
        f.write(content)

def create_indices(all_topics):
    """Create index files for all forums"""
    # Ensure Indexes directory exists
    os.makedirs("Scenarios/Indexes", exist_ok=True)
    
    # Create individual forum indices
    for forum, topics in all_topics.items():
        index_file = f"Scenarios/Indexes/{forum}_index.md"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"# Index of {forum} Scenarios\n\n")
            f.write("| Title | Year | Status | Author | URL |\n")
            f.write("|-------|------|--------|--------|-----|\n")
            
            for topic in topics:
                f.write(f"| {topic['title']} | {topic['year']} | New | {topic['author']} | [{topic['url']}]({topic['url']}) |\n")
    
    # Create combined index
    combined_file = "Scenarios/Indexes/combined_index.md"
    
    with open(combined_file, 'w', encoding='utf-8') as f:
        f.write("# Combined Index of All Scenarios\n\n")
        f.write("| Forum | Title | Year | Status | Author | URL |\n")
        f.write("|-------|-------|------|--------|--------|-----|\n")
        
        for forum, topics in all_topics.items():
            for topic in topics:
                f.write(f"| {forum} | {topic['title']} | {topic['year']} | New | {topic['author']} | [{topic['url']}]({topic['url']}) |\n")
    
    log_message("Created index files")

def main():
    """Run a quick extraction process"""
    log_message("Starting quick extraction process")
    
    # Define forums to process
    forums = {
        "Palace_Situation_Room": "https://nexus.eotir.com/forum/6-palace-situation-room/",
        "Red_Scenario": "https://nexus.eotir.com/forum/59-red-scenario/",
        "Blue_Scenario": "https://nexus.eotir.com/forum/69-blue-scenario/"
    }
    
    # Ensure directories exist
    os.makedirs("Scenarios", exist_ok=True)
    os.makedirs("Reports", exist_ok=True)
    
    all_topics = {}
    
    # Process each forum
    for forum_name, forum_url in forums.items():
        topics = process_forum(forum_name, forum_url)
        all_topics[forum_name] = topics
    
    # Create indices
    create_indices(all_topics)
    
    # Create Excel-compatible index
    create_excel_compatible_index(all_topics)
    
    # Create README
    create_readme()
    
    # List all scenarios with their status
    log_message("Listing all scenarios:")
    subprocess.run(["python", "update_scenario_status.py", "--list"])
    
    log_message("Quick extraction process completed")
    log_message("This was a limited run for demonstration purposes.")
    log_message("Placeholder files have been created in the Scenarios and Reports directories.")
    log_message("For a full extraction, modify the settings in run_full_extraction.py.")

if __name__ == "__main__":
    main()
