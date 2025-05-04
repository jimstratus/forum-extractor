import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin
import datetime
import yaml

# Configuration
BASE_URL = "https://nexus.eotir.com"
FORUM_URLS = {
    "Red_Scenario": "/forum/59-red-scenario/",
    "Palace_Situation_Room": "/forum/6-palace-situation-room/",
    "Blue_Scenario": "/forum/69-blue-scenario/"
}
OUTPUT_DIR = "Scenarios"
INDEX_DIR = os.path.join(OUTPUT_DIR, "Indexes")
LOG_FILE = "forum_extraction_log.txt"

# Regular expressions
IRY_PATTERN = r'\[(\d+)\s*IRY\]'
UFY_PATTERN = r'\[(\d+)\s*UFY\]'

def log_message(message):
    """Write message to log file and print to console"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry + "\n")

def extract_year_from_title(title):
    """Extract IRY or UFY year from title if present"""
    iry_match = re.search(IRY_PATTERN, title)
    if iry_match:
        return f"{iry_match.group(1)} IRY"
    
    ufy_match = re.search(UFY_PATTERN, title)
    if ufy_match:
        return f"{ufy_match.group(1)} UFY"
    
    return "Unknown"

def get_soup(url, retry_count=3, delay=5):
    """Get BeautifulSoup object from URL with retries"""
    for attempt in range(retry_count):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            elif response.status_code == 404:
                log_message(f"404 Error: {url} not found.")
                return None
            else:
                log_message(f"HTTP Error {response.status_code} for {url}")
        except Exception as e:
            log_message(f"Error fetching {url}: {str(e)}")
        
        if attempt < retry_count - 1:
            log_message(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    return None

def get_forum_topics(forum_name, forum_path):
    """Get all topics from a forum"""
    forum_url = urljoin(BASE_URL, forum_path)
    log_message(f"Fetching topics from {forum_name} at {forum_url}")
    
    topics = []
    page = 1
    
    while True:
        page_url = f"{forum_url}?page={page}"
        soup = get_soup(page_url)
        
        if not soup:
            break
        
        # Find topic elements - this will need to be adjusted based on the forum's HTML structure
        topic_elements = soup.select(".ipsDataItem.ipsDataItem_responsivePhoto")
        
        if not topic_elements:
            break
        
        for topic in topic_elements:
            try:
                title_element = topic.select_one(".ipsDataItem_title a")
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                topic_url = title_element.get("href")
                
                # Extract other metadata as available
                author_element = topic.select_one(".ipsDataItem_main .ipsDataItem_meta a")
                author = author_element.text.strip() if author_element else "Unknown"
                
                # Extract year from title
                year = extract_year_from_title(title)
                
                topics.append({
                    "title": title,
                    "url": topic_url,
                    "author": author,
                    "year": year,
                    "status": "New"  # Default status, to be updated manually
                })
                
            except Exception as e:
                log_message(f"Error parsing topic: {str(e)}")
        
        # Check if there's a next page
        next_page = soup.select_one("a[rel='next']")
        if not next_page:
            break
        
        page += 1
        time.sleep(1)  # Respectful delay between requests
    
    log_message(f"Found {len(topics)} topics in {forum_name}")
    return topics

def extract_posts_from_topic(topic_url):
    """Extract all posts from a topic"""
    log_message(f"Extracting posts from {topic_url}")
    posts = []
    page = 1
    
    while True:
        if "?" in topic_url:
            page_url = f"{topic_url}&page={page}"
        else:
            page_url = f"{topic_url}?page={page}"
        
        soup = get_soup(page_url)
        
        if not soup:
            break
        
        # Find post elements - this will need to be adjusted based on the forum's HTML structure
        post_elements = soup.select(".ipsComment")
        
        if not post_elements:
            break
        
        for post in post_elements:
            try:
                # Get author - updated selector based on inspection
                author_element = post.select_one(".cAuthorPane_author")
                author = author_element.text.strip() if author_element else "Unknown"
                
                # Get date - this selector seems to work correctly
                date_element = post.select_one(".ipsComment_meta time")
                date = date_element.get("datetime") if date_element else "Unknown"
                
                # For content, we need to find the actual post content
                # Based on inspection, we need a different approach for content
                content_element = post.select_one(".ipsComment_content")
                
                # If we can't find the content, skip this post
                if not content_element:
                    continue
                
                # Get actual post content and clean it
                # Remove report links and other UI elements
                for report_link in content_element.select(".ipsComment_reportLink"):
                    report_link.decompose()
                
                # Remove any other UI elements we don't want
                for element in content_element.select(".ipsBadge, .ipsQuote_citation, .ipsButton"):
                    element.decompose()
                
                # Convert HTML to Markdown
                content = md(str(content_element))
                
                # Clean up the content
                content = re.sub(r'\*\s+\+\s+\[Report\].*$', '', content, flags=re.MULTILINE)  # Remove report links
                content = re.sub(r'Posted.*?\d{4}', '', content)  # Remove "Posted Date" lines
                content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Remove excessive newlines
                
                posts.append({
                    "author": author,
                    "date": date,
                    "content": content
                })
                
            except Exception as e:
                log_message(f"Error parsing post: {str(e)}")
        
        # Check if there's a next page
        next_page = soup.select_one("a[rel='next']")
        if not next_page:
            break
        
        page += 1
        time.sleep(1)  # Respectful delay between requests
    
    log_message(f"Found {len(posts)} posts in topic")
    return posts

def identify_characters(posts):
    """Identify potential characters from post content"""
    characters = set()
    
    # Simple character identification based on capitalized names
    name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    
    # Words to exclude from character identification (common false positives)
    exclude_words = [
        "Posted Image", "Posted March", "Posted April", "Posted May", "Posted June", 
        "Posted July", "Posted August", "Posted September", "Posted October",
        "Posted November", "Posted December", "Posted January", "Posted February",
        "Cloud Drive", "Personal Staff", "Special Forces", "Regional Governors",
        "Royal Guard", "High Council", "Grand Admiralty", "His Majesty",
        "The Minister", "Palace Situation", "Report This", "Mon Calamari"
    ]
    
    for post in posts:
        content = post["content"]
        
        # Find potential character names (simple heuristic)
        matches = re.findall(name_pattern, content)
        for match in matches:
            # Skip if it contains any excluded words
            if not any(exclude in match for exclude in exclude_words):
                characters.add(match)
    
    return sorted(list(characters))

def create_timeline(posts):
    """Create a simple timeline of events from posts"""
    timeline = []
    
    for i, post in enumerate(posts):
        date = post["date"]
        author = post["author"]
        content = post["content"]
        
        # Extract first paragraph or sentence as summary
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
    """Suggest plot development ideas based on content"""
    # This is a placeholder - in a real implementation, 
    # more sophisticated analysis would be needed
    
    if not posts:
        return {
            "current_state": "No posts available",
            "main_themes": [],
            "open_questions": [],
            "potential_directions": []
        }
    
    # Very basic analysis
    total_content = "\n".join([p["content"] for p in posts])
    word_count = len(total_content.split())
    
    plot_development = {
        "current_state": f"Scenario with {len(posts)} posts and approximately {word_count} words",
        "main_themes": ["To be identified manually"],
        "open_questions": ["To be identified manually"],
        "potential_directions": ["To be determined manually"]
    }
    
    return plot_development

def save_scenario_files(forum_name, topic):
    """Save all files related to a scenario"""
    # Create safe filename from title
    safe_title = re.sub(r'[^\w\s-]', '', topic["title"]).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    
    # Create directory path
    topic_dir = os.path.join(OUTPUT_DIR, forum_name, safe_title)
    os.makedirs(topic_dir, exist_ok=True)
    
    # Fetch posts
    posts = extract_posts_from_topic(topic["url"])
    
    if not posts:
        log_message(f"No posts found for {topic['title']}")
        return False
    
    # Save main content file
    content_file = os.path.join(topic_dir, "content.md")
    with open(content_file, "w", encoding="utf-8") as f:
        f.write(f"# {topic['title']}\n\n")
        f.write(f"Year: {topic['year']}\n")
        f.write(f"URL: {topic['url']}\n")
        f.write(f"Author: {topic['author']}\n\n")
        
        for i, post in enumerate(posts):
            f.write(f"## Post {i+1} by {post['author']} on {post['date']}\n\n")
            f.write(post["content"])
            f.write("\n\n---\n\n")
    
    # Identify characters and save to file
    characters = identify_characters(posts)
    characters_file = os.path.join(topic_dir, "dramatis_personae.md")
    with open(characters_file, "w", encoding="utf-8") as f:
        f.write(f"# Dramatis Personae - {topic['title']}\n\n")
        if characters:
            for character in characters:
                f.write(f"- {character}\n")
        else:
            f.write("No characters automatically identified. Please add manually.\n")
    
    # Create timeline and save to file
    timeline = create_timeline(posts)
    timeline_file = os.path.join(topic_dir, "timeline.md")
    with open(timeline_file, "w", encoding="utf-8") as f:
        f.write(f"# Timeline of Events - {topic['title']}\n\n")
        for event in timeline:
            f.write(f"## Event {event['event_number']} - {event['date']}\n\n")
            f.write(f"Author: {event['author']}\n\n")
            f.write(f"{event['summary']}\n\n")
    
    # Suggest plot development and save to file
    plot_dev = suggest_plot_development(posts)
    plot_file = os.path.join(topic_dir, "plot_development.md")
    with open(plot_file, "w", encoding="utf-8") as f:
        f.write(f"# Plot Development Suggestions - {topic['title']}\n\n")
        f.write(f"## Current State\n\n{plot_dev['current_state']}\n\n")
        
        f.write("## Main Themes\n\n")
        for theme in plot_dev["main_themes"]:
            f.write(f"- {theme}\n")
        
        f.write("\n## Open Questions\n\n")
        for question in plot_dev["open_questions"]:
            f.write(f"- {question}\n")
        
        f.write("\n## Potential Directions\n\n")
        for direction in plot_dev["potential_directions"]:
            f.write(f"- {direction}\n")
    
    # Create metadata file
    metadata = {
        "title": topic["title"],
        "year": topic["year"],
        "url": topic["url"],
        "author": topic["author"],
        "forum": forum_name,
        "status": topic["status"],
        "post_count": len(posts),
        "extracted_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    meta_file = os.path.join(topic_dir, "metadata.yaml")
    with open(meta_file, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, default_flow_style=False)
    
    log_message(f"Saved scenario files for '{topic['title']}'")
    return True

def create_index(forum_name, topics):
    """Create an index file for a forum"""
    index_file = os.path.join(INDEX_DIR, f"{forum_name}_index.md")
    
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(f"# Index of {forum_name} Scenarios\n\n")
        f.write("| Title | Year | Status | Author | URL |\n")
        f.write("|-------|------|--------|--------|-----|\n")
        
        for topic in topics:
            safe_title = re.sub(r'[^\w\s-]', '', topic["title"]).strip()
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            
            f.write(f"| {topic['title']} | {topic['year']} | {topic['status']} | {topic['author']} | [Link]({topic['url']}) |\n")
    
    log_message(f"Created index for {forum_name} with {len(topics)} topics")

def create_combined_index(all_topics):
    """Create a combined index of all scenarios"""
    index_file = os.path.join(INDEX_DIR, "combined_index.md")
    
    with open(index_file, "w", encoding="utf-8") as f:
        f.write("# Combined Index of All Scenarios\n\n")
        f.write("| Forum | Title | Year | Status | Author | URL |\n")
        f.write("|-------|-------|------|--------|--------|-----|\n")
        
        for forum, topics in all_topics.items():
            for topic in topics:
                f.write(f"| {forum} | {topic['title']} | {topic['year']} | {topic['status']} | {topic['author']} | [Link]({topic['url']}) |\n")
    
    log_message("Created combined index of all scenarios")

def main():
    """Main function to extract all scenario data"""
    log_message("Starting extraction process")
    
    # Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    all_topics = {}
    
    # Process each forum
    for forum_name, forum_path in FORUM_URLS.items():
        log_message(f"Processing {forum_name} forum")
        
        forum_dir = os.path.join(OUTPUT_DIR, forum_name)
        os.makedirs(forum_dir, exist_ok=True)
        
        # Get topics from forum
        topics = get_forum_topics(forum_name, forum_path)
        all_topics[forum_name] = topics
        
        # Create index for this forum
        create_index(forum_name, topics)
        
        # Process each topic
        for i, topic in enumerate(topics):
            log_message(f"Processing topic {i+1}/{len(topics)}: {topic['title']}")
            success = save_scenario_files(forum_name, topic)
            
            if not success:
                log_message(f"Failed to process topic: {topic['title']}")
            
            # Respectful delay between processing topics
            time.sleep(2)
    
    # Create combined index
    create_combined_index(all_topics)
    
    log_message("Extraction process completed")

if __name__ == "__main__":
    # Initialize log file
    with open(LOG_FILE, "w", encoding="utf-8") as log_file:
        log_file.write(f"=== Forum Extraction Log - Started at {datetime.datetime.now()} ===\n\n")
    
    main()
