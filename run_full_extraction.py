import os
import subprocess
import time
import datetime
import csv
import yaml

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

def extract_forum(forum_name, forum_url, max_topics=5):
    """Extract scenarios from a specific forum with a limit on the number of topics"""
    log_message(f"Processing {forum_name} forum ({forum_url})")
    
    # Ensure directories exist
    os.makedirs(f"Scenarios/{forum_name}", exist_ok=True)
    os.makedirs(f"Reports/{forum_name}", exist_ok=True)
    
    # Run a targeted extraction for this forum
    cmd = [
        "python", "-c", 
        f"""
import os
import re
import time
import datetime
import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{{timestamp}}] {{msg}}")

def extract_year_from_title(title):
    iry_match = re.search(r'\\[(\\d+)\\s*IRY\\]', title)
    if iry_match:
        return f"{{iry_match.group(1)}} IRY"
    
    ufy_match = re.search(r'\\[(\\d+)\\s*UFY\\]', title)
    if ufy_match:
        return f"{{ufy_match.group(1)}} UFY"
    
    return "Unknown"

def get_soup(url, retry_count=3, delay=3):
    for attempt in range(retry_count):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                log_message(f"HTTP Error {{response.status_code}} for {{url}}")
        except Exception as e:
            log_message(f"Error fetching {{url}}: {{str(e)}}")
        
        if attempt < retry_count - 1:
            log_message(f"Retrying in {{delay}} seconds...")
            time.sleep(delay)
    
    return None

def identify_characters(content):
    characters = set()
    name_pattern = r'\\b[A-Z][a-z]+\\s+[A-Z][a-z]+\\b'
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
        first_lines = content.split('\\n', 2)[0]
        if len(first_lines) > 150:
            summary = first_lines[:150] + "..."
        else:
            summary = first_lines
        
        timeline.append({{
            "event_number": i + 1,
            "date": date,
            "author": author,
            "summary": summary
        }})
    
    return timeline

def suggest_plot_development(posts):
    if not posts:
        return {{
            "current_state": "No posts available",
            "main_themes": ["To be identified manually"],
            "open_questions": ["To be identified manually"],
            "potential_directions": ["To be determined manually"]
        }}
    
    total_content = "\\n".join([p["content"] for p in posts])
    word_count = len(total_content.split())
    
    return {{
        "current_state": f"Scenario with {{len(posts)}} posts and approximately {{word_count}} words",
        "main_themes": ["To be identified manually"],
        "open_questions": ["To be identified manually"],
        "potential_directions": ["To be determined manually"]
    }}

# Process the forum
forum_url = "{forum_url}"
log_message(f"Fetching topics from {{forum_url}}")

# Get topics
page = 1
topics = []
max_topics = {max_topics}
topic_count = 0

while topic_count < max_topics:
    page_url = f"{{forum_url}}?page={{page}}"
    soup = get_soup(page_url)
    
    if not soup:
        break
    
    # Find topic elements
    topic_elements = soup.select(".ipsDataItem.ipsDataItem_responsivePhoto")
    
    if not topic_elements:
        break
    
    for topic in topic_elements:
        if topic_count >= max_topics:
            break
        
        title_element = topic.select_one(".ipsDataItem_title a")
        if not title_element:
            continue
        
        title = title_element.text.strip()
        topic_url = title_element.get("href")
        
        # Get author
        author_element = topic.select_one(".ipsDataItem_main .ipsDataItem_meta a")
        author = author_element.text.strip() if author_element else "Unknown"
        
        # Extract year from title
        year = extract_year_from_title(title)
        
        topics.append({{
            "title": title,
            "url": topic_url,
            "author": author,
            "year": year,
            "status": "New"
        }})
        
        topic_count += 1
        log_message(f"Found topic: {{title}}")
    
    # Check if there's a next page
    next_page = soup.select_one("a[rel='next']")
    if not next_page:
        break
    
    page += 1
    time.sleep(1)  # Respectful delay

log_message(f"Found {{len(topics)}} topics for {forum_name}")

# Process each topic
for i, topic in enumerate(topics):
    log_message(f"Processing topic {{i+1}}/{{len(topics)}}: {{topic['title']}}")
    
    # Get posts from topic
    url = topic["url"]
    posts = []
    page = 1
    
    while True:
        if "?" in url:
            page_url = f"{{url}}&page={{page}}"
        else:
            page_url = f"{{url}}?page={{page}}"
        
        soup = get_soup(page_url)
        
        if not soup:
            break
        
        # Find post elements
        post_elements = soup.select(".ipsComment")
        
        if not post_elements:
            break
        
        for post in post_elements:
            try:
                # Get author
                author_element = post.select_one(".cAuthorPane_author")
                author = author_element.text.strip() if author_element else "Unknown"
                
                # Get date
                date_element = post.select_one(".ipsComment_meta time")
                date = date_element.get("datetime") if date_element else "Unknown"
                
                # Get content
                content_element = post.select_one(".ipsComment_content")
                
                # Skip if no content
                if not content_element:
                    continue
                
                # Clean up the content
                for report_link in content_element.select(".ipsComment_reportLink"):
                    report_link.decompose()
                
                for element in content_element.select(".ipsBadge, .ipsQuote_citation, .ipsButton"):
                    element.decompose()
                
                # Convert to markdown
                content = md(str(content_element))
                
                # Clean up markdown
                content = re.sub(r'\\*\\s+\\+\\s+\\[Report\\].*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'Posted.*?\\d{{4}}', '', content)
                content = re.sub(r'\\n\\s*\\n\\s*\\n+', '\\n\\n', content)
                
                posts.append({{
                    "author": author,
                    "date": date,
                    "content": content
                }})
                
            except Exception as e:
                log_message(f"Error parsing post: {{str(e)}}")
        
        # Check for next page
        next_page = soup.select_one("a[rel='next']")
        if not next_page:
            break
        
        page += 1
        time.sleep(1)
    
    log_message(f"Found {{len(posts)}} posts in topic")
    
    # Skip if no posts
    if not posts:
        log_message(f"No posts found for {{topic['title']}}")
        continue
    
    # Create safe filename
    safe_title = re.sub(r'[^\\w\\s-]', '', topic["title"]).strip()
    safe_title = re.sub(r'[-\\s]+', '_', safe_title)
    
    # Create directory
    scenario_dir = f"Scenarios/{forum_name}/{{safe_title}}"
    os.makedirs(scenario_dir, exist_ok=True)
    
    # Save content file
    content_file = f"{{scenario_dir}}/content.md"
    with open(content_file, "w", encoding="utf-8") as f:
        f.write(f"# {{topic['title']}}\\n\\n")
        f.write(f"Year: {{topic['year']}}\\n")
        f.write(f"URL: {{topic['url']}}\\n")
        f.write(f"Author: {{topic['author']}}\\n\\n")
        
        for j, post in enumerate(posts):
            f.write(f"## Post {{j+1}} by {{post['author']}} on {{post['date']}}\\n\\n")
            f.write(post["content"])
            f.write("\\n\\n---\\n\\n")
    
    # Identify characters
    all_content = "\\n".join([p["content"] for p in posts])
    characters = identify_characters(all_content)
    
    # Save characters file
    chars_file = f"{{scenario_dir}}/dramatis_personae.md"
    with open(chars_file, "w", encoding="utf-8") as f:
        f.write(f"# Dramatis Personae - {{topic['title']}}\\n\\n")
        if characters:
            for character in characters:
                f.write(f"- {{character}}\\n")
        else:
            f.write("No characters automatically identified. Please add manually.\\n")
    
    # Create timeline
    timeline = create_timeline(posts)
    timeline_file = f"{{scenario_dir}}/timeline.md"
    with open(timeline_file, "w", encoding="utf-8") as f:
        f.write(f"# Timeline of Events - {{topic['title']}}\\n\\n")
        for event in timeline:
            f.write(f"## Event {{event['event_number']}} - {{event['date']}}\\n\\n")
            f.write(f"Author: {{event['author']}}\\n\\n")
            f.write(f"{{event['summary']}}\\n\\n")
    
    # Suggest plot development
    plot_dev = suggest_plot_development(posts)
    plot_file = f"{{scenario_dir}}/plot_development.md"
    with open(plot_file, "w", encoding="utf-8") as f:
        f.write(f"# Plot Development Suggestions - {{topic['title']}}\\n\\n")
        f.write(f"## Current State\\n\\n{{plot_dev['current_state']}}\\n\\n")
        
        f.write("## Main Themes\\n\\n")
        for theme in plot_dev["main_themes"]:
            f.write(f"- {{theme}}\\n")
        
        f.write("\\n## Open Questions\\n\\n")
        for question in plot_dev["open_questions"]:
            f.write(f"- {{question}}\\n")
        
        f.write("\\n## Potential Directions\\n\\n")
        for direction in plot_dev["potential_directions"]:
            f.write(f"- {{direction}}\\n")
    
    # Create metadata
    metadata = {{
        "title": topic["title"],
        "year": topic["year"],
        "url": topic["url"],
        "author": topic["author"],
        "forum": "{forum_name}",
        "status": "New",
        "post_count": len(posts),
        "extracted_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }}
    
    # Save metadata
    meta_file = f"{{scenario_dir}}/metadata.yaml"
    with open(meta_file, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, default_flow_style=False)
    
    log_message(f"Saved scenario files for '{{topic['title']}}'")
    time.sleep(1)  # Respectful delay

# Create index file
index_file = "Scenarios/Indexes/{forum_name}_index.md"
os.makedirs("Scenarios/Indexes", exist_ok=True)

with open(index_file, "w", encoding="utf-8") as f:
    f.write(f"# Index of {forum_name} Scenarios\\n\\n")
    f.write("| Title | Year | Status | Author | URL |\\n")
    f.write("|-------|------|--------|--------|-----|\\n")
    
    for topic in topics:
        f.write(f"| {{topic['title']}} | {{topic['year']}} | {{topic['status']}} | {{topic['author']}} | [Link]({{topic['url']}}) |\\n")

log_message(f"Created index for {forum_name} with {{len(topics)}} topics")
        """
    ]
    
    subprocess.run(cmd)
    return

def main():
    """Run the full extraction process"""
    log_message("Starting full extraction process")
    
    # Ensure directories exist
    os.makedirs("Scenarios", exist_ok=True)
    os.makedirs("Scenarios/Indexes", exist_ok=True)
    os.makedirs("Reports", exist_ok=True)
    
    # Process forums in specified order:
    # 1. Palace Situation Room
    log_message("Processing Palace_Situation_Room forum first")
    extract_forum("Palace_Situation_Room", "https://nexus.eotir.com/forum/6-palace-situation-room/", max_topics=5)
    
    # 2. Blue Scenario
    log_message("Processing Blue_Scenario forum second")
    extract_forum("Blue_Scenario", "https://nexus.eotir.com/forum/69-blue-scenario/", max_topics=5)
    
    # 3. Red Scenario
    log_message("Processing Red_Scenario forum third")
    extract_forum("Red_Scenario", "https://nexus.eotir.com/forum/59-red-scenario/", max_topics=5)
    
    # Step 2: Generate reports for all extracted scenarios
    log_message("Running generate_combined_report.py to create reports")
    subprocess.run(["python", "generate_combined_report.py"])
    
    # Step 3: Create Excel-compatible index
    create_excel_compatible_index()
    
    # Step 4: List all scenarios with their status
    log_message("Listing all scenarios with their status:")
    subprocess.run(["python", "update_scenario_status.py", "--list"])
    
    log_message("Extraction process completed")
    log_message("Reports can be found in the Reports directory")
    log_message("Scenario data can be found in the Scenarios directory")
    log_message("Index files can be found in Scenarios/Indexes directory")
    log_message("Excel-compatible index: scenario_index.csv")

if __name__ == "__main__":
    main()
