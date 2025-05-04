#!/usr/bin/env python3
"""
EOTIR Forum Extractor
This script extracts scenarios from EOTIR forum topics and saves them as structured Markdown files.
"""

import os
import sys
import re
import json
import logging
import argparse
import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
from markdownify import markdownify as md
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("extraction_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base directories
SCENARIOS_DIR = "Scenarios"
FORUM_URLS = {
    "Red_Scenario": "https://nexus.eotir.com/forum/59-red-scenario/",
    "Palace_Situation_Room": "https://nexus.eotir.com/forum/6-palace-situation-room/",
    "Blue_Scenario": "https://nexus.eotir.com/forum/69-blue-scenario/"
}

def sanitize_filename(text):
    """Sanitize text to be used as a filename"""
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', text)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def extract_year_from_title(title):
    """Extract the year designation from a scenario title"""
    year_match = re.search(r'\[(\d+\s*(?:IRY|UFY))\]', title, re.IGNORECASE)
    if year_match:
        return year_match.group(1)
    return ""

def fetch_page(url, session=None):
    """Fetch a page from a URL, handling errors and retries"""
    if session is None:
        session = requests.Session()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed for {url}: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                return None

def extract_topic_links(forum_url, session=None):
    """Extract all topic links from a forum"""
    if session is None:
        session = requests.Session()
    
    logger.info(f"Extracting topic links from {forum_url}")
    
    topic_links = []
    page_num = 1
    
    while True:
        page_url = f"{forum_url}page/{page_num}/"
        html = fetch_page(page_url, session)
        
        if not html:
            break
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all topic links - this selector will need to be adjusted for the actual forum
        topics = soup.select('.topic-title a')
        
        if not topics:
            break
        
        for topic in topics:
            topic_url = topic.get('href')
            if topic_url:
                # Convert relative URLs to absolute URLs
                if topic_url.startswith('/'):
                    topic_url = 'https://nexus.eotir.com' + topic_url
                
                topic_links.append({
                    'title': topic.text.strip(),
                    'url': topic_url
                })
        
        # Check if there's a next page
        next_page = soup.select_one('.ipsPagination .ipsPagination_next:not(.ipsPagination_inactive)')
        if not next_page:
            break
        
        page_num += 1
    
    logger.info(f"Found {len(topic_links)} topics in {forum_url}")
    return topic_links

def extract_topic_content(topic_url, session=None):
    """Extract content from a forum topic"""
    if session is None:
        session = requests.Session()
    
    logger.info(f"Extracting content from {topic_url}")
    
    html = fetch_page(topic_url, session)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract topic title
    title_elem = soup.select_one('.ipsType_pageTitle')
    if not title_elem:
        title_elem = soup.select_one('h1.ipsType_pagetitle')
    
    title = title_elem.text.strip() if title_elem else "Untitled Scenario"
    
    # Extract year from title
    year = extract_year_from_title(title)
    
    # Extract posts
    posts = []
    
    # Find all post containers - selector may need adjustment
    post_containers = soup.select('.cPost')
    
    for post in post_containers:
        # Extract author
        author_elem = post.select_one('.cAuthorPane_author .ipsType_break')
        author = author_elem.text.strip() if author_elem else "Unknown"
        
        # Extract date
        date_elem = post.select_one('time')
        date = date_elem.get('datetime') if date_elem else ""
        display_date = date_elem.text.strip() if date_elem else ""
        
        # Extract content
        content_elem = post.select_one('.cPost_contentWrap')
        
        if content_elem:
            # Remove quotes and other unnecessary elements
            for quote in content_elem.select('.ipsQuote'):
                quote.decompose()
            
            # Convert HTML to Markdown
            content = md(str(content_elem))
            
            posts.append({
                'author': author,
                'date': date,
                'display_date': display_date,
                'content': content
            })
    
    # Get the forum name from the URL
    forum_name = "Unknown"
    for key, url in FORUM_URLS.items():
        if url in topic_url:
            forum_name = key
            break
    
    # Create result object
    result = {
        'title': title,
        'year': year,
        'url': topic_url,
        'forum': forum_name,
        'posts': posts
    }
    
    return result

def format_scenario_as_markdown(scenario):
    """Format a scenario as a Markdown document with YAML frontmatter"""
    # Create frontmatter
    frontmatter = {
        'title': scenario['title'],
        'forum': scenario['forum'],
        'year': scenario['year'],
        'status': 'Unknown',  # To be updated manually
        'extraction_date': datetime.now().strftime('%Y-%m-%d'),
        'url': scenario['url']
    }
    
    # Start with frontmatter
    md_content = "---\n"
    for key, value in frontmatter.items():
        md_content += f"{key}: {value}\n"
    md_content += "---\n\n"
    
    # Add title
    md_content += f"# {scenario['title']}\n\n"
    
    # Add posts
    for post in scenario['posts']:
        md_content += f"*Posted by {post['author']} - {post['display_date']}*\n\n"
        md_content += post['content'].strip() + "\n\n"
        md_content += "---\n\n"
    
    return md_content

def save_scenario(scenario_data):
    """Save a scenario to a file"""
    # Extract forum and year for directory structure
    forum = sanitize_filename(scenario_data['forum'])
    year = sanitize_filename(scenario_data['year']) if scenario_data['year'] else "Unknown_Year"
    year_dir = year.replace(" ", "_")
    
    # Create directory structure
    scenario_dir = os.path.join(SCENARIOS_DIR, forum, year_dir)
    os.makedirs(scenario_dir, exist_ok=True)
    
    # Create filename from title
    title = sanitize_filename(scenario_data['title'])
    filename = os.path.join(scenario_dir, f"{title}.md")
    
    # Format as Markdown
    md_content = format_scenario_as_markdown(scenario_data)
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    logger.info(f"Saved scenario to {filename}")
    return filename

def create_supplementary_file(scenario_path, suffix, content):
    """Create a supplementary file (characters, timeline, analysis, etc.)"""
    # Get the base path without extension
    base_path = os.path.splitext(scenario_path)[0]
    output_path = f"{base_path}_{suffix}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Created {suffix} file at {output_path}")
    return output_path

def create_empty_character_list(scenario_path, scenario_data):
    """Create an empty character list file with proper structure"""
    title = scenario_data['title']
    
    # Create YAML frontmatter
    frontmatter = {
        'character_count': 0,
        'generated_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Generate content
    content = "---\n"
    for key, value in frontmatter.items():
        content += f"{key}: {value}\n"
    content += "---\n\n"
    content += f"# Characters in {title}\n\n"
    content += "This is a placeholder character list file. Please add characters manually.\n\n"
    content += "## Character Template\n\n"
    content += "1. **Character Name**\n"
    content += "   - **Role**: (e.g., protagonist, antagonist, supporting character)\n"
    content += "   - **Affiliation**: (e.g., organization, faction, group)\n"
    content += "   - **Description**: (physical description, personality traits)\n"
    content += "   - **Background**: (character's history, motivation)\n"
    content += "   - **Development**: (how the character evolves)\n\n"
    
    return create_supplementary_file(scenario_path, "characters", content)

def create_empty_timeline(scenario_path, scenario_data):
    """Create an empty timeline file with proper structure"""
    title = scenario_data['title']
    
    # Create YAML frontmatter
    frontmatter = {
        'event_count': 0,
        'generated_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Generate content
    content = "---\n"
    for key, value in frontmatter.items():
        content += f"{key}: {value}\n"
    content += "---\n\n"
    content += f"# Timeline of Events in {title}\n\n"
    content += "This is a placeholder timeline file. Please add events manually.\n\n"
    content += "## Event Template\n\n"
    content += "1. **Event Title/Description**\n"
    content += "   - **Date/Time**: (in-story chronology)\n"
    content += "   - **Location**: (where the event occurred)\n"
    content += "   - **Participants**: (characters involved)\n"
    content += "   - **Description**: (what happened)\n"
    content += "   - **Consequences**: (the impact of this event on the story)\n\n"
    
    return create_supplementary_file(scenario_path, "timeline", content)

def create_empty_analysis(scenario_path, scenario_data):
    """Create an empty analysis file with proper structure"""
    title = scenario_data['title']
    
    # Create YAML frontmatter
    frontmatter = {
        'completion_status': 'Unknown',
        'generated_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Generate content
    content = "---\n"
    for key, value in frontmatter.items():
        content += f"{key}: {value}\n"
    content += "---\n\n"
    content += f"# Analysis of {title}\n\n"
    content += "This is a placeholder analysis file. Please complete the analysis manually.\n\n"
    content += "## Overall Status\n\n"
    content += "**Completion Status**: (Complete, Partially Complete, In Progress, or Incomplete)\n\n"
    content += "**Last Post Date**: (date of the most recent post)\n\n"
    content += "**Post Count**: (number of posts in the scenario)\n\n"
    content += "## Unfinished Plotlines\n\n"
    content += "List any plotlines that have been introduced but not resolved:\n\n"
    content += "1. (Plotline description)\n\n"
    
    return create_supplementary_file(scenario_path, "analysis", content)

def create_empty_development(scenario_path, scenario_data):
    """Create an empty development file with proper structure"""
    title = scenario_data['title']
    
    # Create YAML frontmatter
    frontmatter = {
        'suggestion_count': 0,
        'generated_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Generate content
    content = "---\n"
    for key, value in frontmatter.items():
        content += f"{key}: {value}\n"
    content += "---\n\n"
    content += f"# Development Suggestions for {title}\n\n"
    content += "This is a placeholder development file. Please add suggestions manually.\n\n"
    content += "## Suggestion Template\n\n"
    content += "1. **Suggestion Title**\n"
    content += "   - **Type**: (e.g., plot development, character development, world-building)\n"
    content += "   - **Description**: (detailed description of the suggestion)\n"
    content += "   - **Impact**: (how this suggestion would affect the story)\n"
    content += "   - **Implementation**: (how to implement this suggestion)\n\n"
    
    return create_supplementary_file(scenario_path, "development", content)

def extract_scenarios(forum_url=None, login=False):
    """Extract scenarios from a forum"""
    session = requests.Session()
    
    # Handle login if required
    if login:
        logger.info("Login functionality not implemented yet")
        # TODO: Implement login functionality
    
    # If no forum specified, process all forums
    if not forum_url:
        forums_to_process = FORUM_URLS.items()
    else:
        # Find the forum key that matches the URL
        forum_key = next((k for k, v in FORUM_URLS.items() if v in forum_url), None)
        if not forum_key:
            # If the URL doesn't match any predefined forum, use it directly
            forums_to_process = [("Custom_Forum", forum_url)]
        else:
            forums_to_process = [(forum_key, FORUM_URLS[forum_key])]
    
    # Process each forum
    results = []
    for forum_name, forum_url in forums_to_process:
        logger.info(f"Processing forum: {forum_name} ({forum_url})")
        
        try:
            # Extract topic links
            topic_links = extract_topic_links(forum_url, session)
            
            for topic in topic_links:
                try:
                    # Extract topic content
                    scenario_data = extract_topic_content(topic['url'], session)
                    
                    if scenario_data:
                        # Save scenario
                        scenario_path = save_scenario(scenario_data)
                        
                        # Create supplementary files
                        character_path = create_empty_character_list(scenario_path, scenario_data)
                        timeline_path = create_empty_timeline(scenario_path, scenario_data)
                        analysis_path = create_empty_analysis(scenario_path, scenario_data)
                        development_path = create_empty_development(scenario_path, scenario_data)
                        
                        results.append({
                            'title': scenario_data['title'],
                            'forum': forum_name,
                            'year': scenario_data['year'],
                            'url': topic['url'],
                            'scenario_path': scenario_path,
                            'character_path': character_path,
                            'timeline_path': timeline_path,
                            'analysis_path': analysis_path,
                            'development_path': development_path
                        })
                except Exception as e:
                    logger.error(f"Error processing topic {topic['url']}: {e}")
        except Exception as e:
            logger.error(f"Error processing forum {forum_url}: {e}")
    
    return results

def generate_index(scenarios):
    """Generate an index of scenarios"""
    # Create indexes directory
    indexes_dir = os.path.join(SCENARIOS_DIR, "Indexes")
    os.makedirs(indexes_dir, exist_ok=True)
    
    # Create a markdown index
    md_path = os.path.join(indexes_dir, "scenario_index.md")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# EOTIR Scenario Index\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Group by forum
        forums = {}
        for scenario in scenarios:
            forum = scenario['forum']
            if forum not in forums:
                forums[forum] = []
            forums[forum].append(scenario)
        
        # Write each forum section
        for forum, forum_scenarios in forums.items():
            f.write(f"## {forum.replace('_', ' ')}\n\n")
            
            # Group by year
            years = {}
            for scenario in forum_scenarios:
                year = scenario['year'] if scenario['year'] else "Unknown Year"
                if year not in years:
                    years[year] = []
                years[year].append(scenario)
            
            # Write each year section
            for year, year_scenarios in years.items():
                f.write(f"### {year}\n\n")
                
                for scenario in year_scenarios:
                    f.write(f"- **{scenario['title']}**\n")
                    f.write(f"  - URL: [{scenario['url']}]({scenario['url']})\n")
                    f.write(f"  - Scenario: [{os.path.basename(scenario['scenario_path'])}]({scenario['scenario_path']})\n")
                    f.write(f"  - Characters: [{os.path.basename(scenario['character_path'])}]({scenario['character_path']})\n")
                    f.write(f"  - Timeline: [{os.path.basename(scenario['timeline_path'])}]({scenario['timeline_path']})\n")
                    f.write(f"  - Analysis: [{os.path.basename(scenario['analysis_path'])}]({scenario['analysis_path']})\n")
                    f.write(f"  - Development: [{os.path.basename(scenario['development_path'])}]({scenario['development_path']})\n")
                    f.write("\n")
    
    logger.info(f"Generated index at {md_path}")
    return md_path

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EOTIR Forum Extractor - Extract scenarios from EOTIR forum topics")
    parser.add_argument("--forum", help="URL of the forum to scrape (default: all forums)")
    parser.add_argument("--login", action="store_true", help="Login to the forum (will prompt for credentials)")
    parser.add_argument("--output", help="Output directory for scenarios")
    args = parser.parse_args()
    
    # Setup output directory
    if args.output:
        global SCENARIOS_DIR
        SCENARIOS_DIR = args.output
    
    # Ensure scenarios directory exists
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    
    try:
        # Extract scenarios
        scenarios = extract_scenarios(args.forum, args.login)
        
        # Generate index
        index_path = generate_index(scenarios)
        
        logger.info(f"Extraction complete. Processed {len(scenarios)} scenarios.")
        logger.info(f"Index generated at {index_path}")
        
        return 0
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
