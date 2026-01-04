#!/usr/bin/env python3
"""
EOTIR Scenario Scraper
This script extracts scenarios from forum topics.
It wraps the forum_scraper module to provide a consistent interface for the scenario manager.
"""

import os
import re
import sys
import logging
import argparse
from datetime import datetime

# Import the actual scraper implementation
try:
    from forum_scraper import (
        get_forum_topics,
        save_scenario_files,
        create_index,
        create_combined_index,
        extract_posts_from_topic,
        OUTPUT_DIR,
        FORUM_URLS
    )
    FORUM_SCRAPER_AVAILABLE = True
except ImportError:
    FORUM_SCRAPER_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base directories
SCENARIOS_DIR = os.path.join("Scenarios")


def sanitize_filename(text):
    """Sanitize a string to be used as a filename"""
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


def scrape_forum(forum_url, login=False):
    """
    Scrape scenarios from a forum.
    
    Uses the forum_scraper module if available, otherwise returns placeholder data.
    """
    logger.info(f"Scraping forum: {forum_url}")
    
    if login:
        logger.info("Login required. Would prompt for credentials in the actual implementation.")
    
    if FORUM_SCRAPER_AVAILABLE:
        # Use the actual forum scraper
        logger.info("Using forum_scraper module for extraction")
        try:
            # Determine forum name from URL
            forum_name = "Unknown"
            for name, path in FORUM_URLS.items():
                if forum_url.endswith(path) or path in forum_url or name.lower() in forum_url.lower():
                    forum_name = name
                    break
            
            # Get topics from forum
            topics = get_forum_topics(forum_name, forum_url)
            
            if topics:
                # Create index for this forum
                create_index(forum_name, topics)
                
                # Process each topic
                for topic in topics:
                    save_scenario_files(forum_name, topic)
                
                return True
            else:
                logger.warning(f"No topics found in {forum_url}")
                return False
        except Exception as e:
            logger.error(f"Error using forum_scraper: {e}")
            return False
    else:
        # Fallback to placeholder
        logger.info("forum_scraper module not available, using placeholder data")
        
        # Create a simple placeholder scenario
        scenario_data = {
            "title": "Sample Scenario [34 IRY]",
            "forum": "Red_Scenario",
            "year": "34 IRY",
            "status": "In Progress",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "url": forum_url + "/topic/sample-scenario-34-iry/",
            "content": "# Sample Scenario [34 IRY]\n\n*Posted by Example_User - May 1, 2025*\n\nThis is a placeholder scenario that would be replaced with actual content scraped from the forum.\n\n---\n\n*Posted by Another_User - May 2, 2025*\n\nThis is a reply to the scenario."
        }
        
        # Save the scenario
        save_scenario(scenario_data)
        
        return True

def save_scenario(scenario_data, scenarios_dir=None):
    """Save a scenario to a Markdown file with YAML frontmatter"""
    # Use provided directory or default
    base_dir = scenarios_dir if scenarios_dir else SCENARIOS_DIR
    
    # Extract forum and year for directory structure
    forum = sanitize_filename(scenario_data.get("forum", "Unknown"))
    year = sanitize_filename(scenario_data.get("year", "Unknown_Year"))
    year_dir = year.replace(" ", "_")
    
    # Create directory structure
    scenario_dir = os.path.join(base_dir, forum, year_dir)
    os.makedirs(scenario_dir, exist_ok=True)
    
    # Create filename from title
    title = sanitize_filename(scenario_data.get("title", "Untitled_Scenario"))
    filename = os.path.join(scenario_dir, f"{title}.md")
    
    # Create frontmatter
    frontmatter = {
        "title": scenario_data.get("title", "Untitled Scenario"),
        "forum": scenario_data.get("forum", "Unknown"),
        "year": scenario_data.get("year", ""),
        "status": scenario_data.get("status", "Unknown"),
        "extraction_date": scenario_data.get("extraction_date", datetime.now().strftime("%Y-%m-%d")),
        "url": scenario_data.get("url", "")
    }
    
    # Create the Markdown file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("---\n")
        for key, value in frontmatter.items():
            f.write(f"{key}: {value}\n")
        f.write("---\n\n")
        f.write(scenario_data.get("content", ""))
    
    logger.info(f"Saved scenario to {filename}")
    return filename

def extract_single_topic(topic_url, output_dir=None):
    """
    Extract posts from a single topic URL and save as scenario.
    
    Args:
        topic_url: URL of the topic to extract
        output_dir: Optional output directory for the scenario
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Extracting single topic: {topic_url}")
    
    scenarios_dir = output_dir if output_dir else SCENARIOS_DIR
    
    if not FORUM_SCRAPER_AVAILABLE:
        logger.error("forum_scraper module not available for single topic extraction")
        return False
    
    try:
        # Extract posts from the topic
        posts = extract_posts_from_topic(topic_url)
        
        if not posts:
            logger.warning(f"No posts found in topic: {topic_url}")
            return False
        
        # Extract title from first post or URL
        title = "Extracted_Topic"
        year = "Unknown"
        
        # Try to extract title from URL path (before query parameters)
        # Handle different URL formats gracefully
        try:
            url_parts = topic_url.split('?')[0].rstrip('/').split('/')
            if url_parts and url_parts[-1] and len(url_parts[-1]) > 1:
                # Only use if it looks like a topic slug (not just a single character)
                title = url_parts[-1].replace('-', ' ').title()
        except (IndexError, AttributeError):
            # Fallback to default if URL parsing fails
            logger.warning(f"Could not extract title from URL: {topic_url}")
        
        # Try to extract year from title or content
        if posts:
            first_content = posts[0].get("content", "")
            year_from_content = extract_year_from_title(title) or extract_year_from_title(first_content)
            if year_from_content:
                year = year_from_content
        
        # Create scenario data
        scenario_data = {
            "title": title,
            "forum": "Single_Topic",
            "year": year,
            "status": "Extracted",
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "url": topic_url,
            "content": ""
        }
        
        # Build content from posts
        content_parts = [f"# {title}\n\n"]
        content_parts.append(f"URL: {topic_url}\n")
        content_parts.append(f"Year: {year}\n\n")
        
        for i, post in enumerate(posts):
            author = post.get("author", "Unknown")
            date = post.get("date", "Unknown")
            post_content = post.get("content", "")
            
            content_parts.append(f"## Post {i+1} by {author} on {date}\n\n")
            content_parts.append(post_content)
            content_parts.append("\n\n---\n\n")
        
        scenario_data["content"] = "".join(content_parts)
        
        # Save the scenario
        save_scenario(scenario_data, scenarios_dir)
        
        logger.info(f"Successfully extracted {len(posts)} posts from topic")
        return True
        
    except Exception as e:
        logger.error(f"Error extracting single topic: {e}")
        return False

def extract_scenarios_from_forums(forums, output_dir=None, login=False):
    """Extract scenarios from multiple forums"""
    # Note: output_dir modification only affects fallback mode (when forum_scraper unavailable)
    # When forum_scraper is available, it uses its own OUTPUT_DIR configuration
    if output_dir:
        global SCENARIOS_DIR
        SCENARIOS_DIR = output_dir
    
    results = []
    all_topics = {}
    
    for forum in forums:
        result = scrape_forum(forum, login)
        results.append((forum, result))
        
        # Collect topics for combined index
        if FORUM_SCRAPER_AVAILABLE:
            forum_name = "Unknown"
            for name, path in FORUM_URLS.items():
                if forum.endswith(path) or path in forum or name.lower() in forum.lower():
                    forum_name = name
                    break
            
            try:
                topics = get_forum_topics(forum_name, forum)
                if topics:
                    all_topics[forum_name] = topics
            except Exception as e:
                logger.error(f"Error getting topics for combined index: {e}")
    
    # Create combined index after all forums are processed
    if FORUM_SCRAPER_AVAILABLE and all_topics:
        try:
            create_combined_index(all_topics)
            logger.info("Combined index created successfully")
        except Exception as e:
            logger.error(f"Error creating combined index: {e}")
    
    return results

def main(args=None):
    """Main execution function"""
    if args is None:
        parser = argparse.ArgumentParser(description="EOTIR Scenario Scraper - Extract scenarios from forum topics")
        parser.add_argument("--forum", help="URL of the forum to scrape")
        parser.add_argument("--topic", help="URL of a single topic to extract")
        parser.add_argument("--login", action="store_true", help="Login to the forum (will prompt for credentials)")
        parser.add_argument("--output", help="Output directory for scenarios")
        args = parser.parse_args()
    
    # Setup output directory
    if args.output:
        global SCENARIOS_DIR
        SCENARIOS_DIR = args.output
    
    # Ensure scenarios directory exists
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    
    # Handle single topic extraction
    if args.topic:
        logger.info("Single topic extraction mode")
        success = extract_single_topic(args.topic, args.output)
        status = "Success" if success else "Failed"
        logger.info(f"Single topic extraction: {status}")
        return
    
    # Default forums to scrape if none specified
    forums = []
    if args.forum:
        forums.append(args.forum)
    else:
        # Default forums
        forums = [
            "https://nexus.eotir.com/forum/59-red-scenario/",
            "https://nexus.eotir.com/forum/6-palace-situation-room/",
            "https://nexus.eotir.com/forum/69-blue-scenario/"
        ]
    
    # Extract scenarios
    results = extract_scenarios_from_forums(forums, args.output, args.login)
    
    # Print results
    logger.info("Extraction complete")
    for forum, success in results:
        status = "Success" if success else "Failed"
        logger.info(f"{forum}: {status}")

if __name__ == "__main__":
    main()
