import os
import re
import json
import time
import logging
from time import sleep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
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

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ForumScraper:
    def __init__(self, requests_per_minute=30):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        # Configure rate limiting
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60.0 / self.requests_per_minute  # Minimum seconds between requests
        self.last_request_time = 0
        self.rate_limit_hits = 0
        self.total_requests = 0

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limiting."""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_delay:
                sleep_time = self.min_delay - elapsed
                if sleep_time > 0.1:  # Only log if significant wait
                    logger.debug(f"Rate limiting: waiting {sleep_time:.1f}s")
                sleep(sleep_time)
        self.last_request_time = time.time()

    def extract_page(self, url, timeout=30):
        """Extract and parse a page, respecting rate limits."""
        try:
            self._wait_for_rate_limit()
            self.total_requests += 1
            response = self.session.get(url, timeout=timeout)

            if response.status_code == 429:  # Too Many Requests
                self.rate_limit_hits += 1
                self.requests_per_minute = max(5, self.requests_per_minute - 5)
                self.min_delay = 60.0 / self.requests_per_minute
                logger.warning(f"Rate limit hit. Reducing rate to {self.requests_per_minute} requests/minute")
                time.sleep(30)  # Wait 30 seconds before retrying
                return self.extract_page(url, timeout)

            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None

def extract_year_from_title(title):
    """Extract IRY or UFY year from title if present"""
    iry_match = re.search(IRY_PATTERN, title)
    if iry_match:
        return f"{iry_match.group(1)} IRY"

    ufy_match = re.search(UFY_PATTERN, title)
    if ufy_match:
        return f"{ufy_match.group(1)} UFY"

    return "Unknown"

def get_forum_topics(forum_name, forum_path):
    """Get all topics from a forum"""
    forum_url = urljoin(BASE_URL, forum_path)
    logger.info(f"Fetching topics from {forum_name} at {forum_url}")

    topics = []
    page = 1
    scraper = ForumScraper()

    while True:
        page_url = f"{forum_url}?page={page}"
        soup = scraper.extract_page(page_url)

        if not soup:
            logger.warning(f"Failed to fetch page {page} from {forum_url}")
            break

        # Try multiple selectors for topic elements (IPS4 compatibility)
        topic_elements = soup.select(".ipsDataItem")
        
        # If no topics found, try alternative selectors
        if not topic_elements:
            topic_elements = soup.select("li.ipsDataItem")
        if not topic_elements:
            topic_elements = soup.select(".cTopicList li")
        if not topic_elements:
            topic_elements = soup.select("[data-rowid]")
            
        logger.info(f"Page {page}: Found {len(topic_elements)} topic elements")

        if not topic_elements:
            if page == 1:
                logger.warning(f"No topics found on first page. Check CSS selectors.")
            break

        for topic in topic_elements:
            try:
                # Try multiple selectors for title
                title_element = topic.select_one(".ipsDataItem_title a")
                if not title_element:
                    title_element = topic.select_one("a.ipsDataItem_title")
                if not title_element:
                    title_element = topic.select_one(".ipsContained a")
                if not title_element:
                    title_element = topic.select_one("h4 a")
                    
                if not title_element:
                    continue

                title = title_element.text.strip()
                topic_url = title_element.get("href")

                # Try multiple selectors for author
                author_element = topic.select_one(".ipsDataItem_main .ipsDataItem_meta a")
                if not author_element:
                    author_element = topic.select_one(".ipsDataItem_meta a[href*='profile']")
                if not author_element:
                    author_element = topic.select_one(".cTopicList_author a")
                    
                author = author_element.text.strip() if author_element else "Unknown"

                year = extract_year_from_title(title)

                topics.append({
                    "title": title,
                    "url": topic_url,
                    "author": author,
                    "year": year,
                    "status": "New"
                })

            except Exception as e:
                logger.error(f"Error parsing topic: {str(e)}")

        next_page = soup.select_one("a[rel='next']")
        if not next_page:
            break

        page += 1
        sleep(1)

    logger.info(f"Found {len(topics)} topics in {forum_name}")
    return topics

def extract_posts_from_topic(topic_url):
    """Extract all posts from a topic"""
    logger.info(f"Extracting posts from {topic_url}")
    posts = []
    page = 1
    scraper = ForumScraper()

    while True:
        if "?" in topic_url:
            page_url = f"{topic_url}&page={page}"
        else:
            page_url = f"{topic_url}?page={page}"

        soup = scraper.extract_page(page_url)

        if not soup:
            logger.warning(f"Failed to fetch page {page} from {topic_url}")
            break

        # Try multiple selectors for post elements
        post_elements = soup.select(".ipsComment")
        if not post_elements:
            post_elements = soup.select("article.ipsComment")
        if not post_elements:
            post_elements = soup.select("[data-commentid]")
        if not post_elements:
            post_elements = soup.select(".cPost")
            
        logger.info(f"Page {page}: Found {len(post_elements)} post elements")

        if not post_elements:
            if page == 1:
                logger.warning(f"No posts found on first page. Check CSS selectors.")
            break

        for post in post_elements:
            try:
                # Try multiple selectors for author
                author_element = post.select_one(".cAuthorPane_author")
                if not author_element:
                    author_element = post.select_one(".ipsComment_author a")
                if not author_element:
                    author_element = post.select_one("[data-author]")
                    if author_element:
                        author = author_element.get("data-author", "Unknown")
                    else:
                        author = "Unknown"
                else:
                    author = author_element.text.strip()

                # Try multiple selectors for date
                date_element = post.select_one(".ipsComment_meta time")
                if not date_element:
                    date_element = post.select_one("time[datetime]")
                date = date_element.get("datetime") if date_element else "Unknown"

                # Try multiple selectors for content
                content_element = post.select_one(".ipsComment_content")
                if not content_element:
                    content_element = post.select_one(".cPost_content")
                if not content_element:
                    content_element = post.select_one("[data-role='commentContent']")

                if not content_element:
                    continue

                # Clean up the content
                for report_link in content_element.select(".ipsComment_reportLink"):
                    report_link.decompose()

                for element in content_element.select(".ipsBadge, .ipsQuote_citation, .ipsButton"):
                    element.decompose()

                content = md(str(content_element))

                content = re.sub(r'\*\s+\+\s+\[Report\].*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'Posted.*?\d{4}', '', content)
                content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

                posts.append({
                    "author": author,
                    "date": date,
                    "content": content
                })

            except Exception as e:
                logger.error(f"Error parsing post: {str(e)}")

        next_page = soup.select_one("a[rel='next']")
        if not next_page:
            break

        page += 1
        sleep(1)

    logger.info(f"Found {len(posts)} posts in topic")
    return posts

def identify_characters(posts):
    """Identify potential characters from post content"""
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

    for post in posts:
        content = post["content"]
        matches = re.findall(name_pattern, content)
        for match in matches:
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
    if not posts:
        return {
            "current_state": "No posts available",
            "main_themes": [],
            "open_questions": [],
            "potential_directions": []
        }

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
    safe_title = re.sub(r'[^\w\s-]', '', topic["title"]).strip()
    safe_title = re.sub(r'[-\s]+', '_', safe_title)

    topic_dir = os.path.join(OUTPUT_DIR, forum_name, safe_title)
    os.makedirs(topic_dir, exist_ok=True)

    posts = extract_posts_from_topic(topic["url"])

    if not posts:
        logger.warning(f"No posts found for {topic['title']}")
        return False

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

    characters = identify_characters(posts)
    characters_file = os.path.join(topic_dir, "dramatis_personae.md")
    with open(characters_file, "w", encoding="utf-8") as f:
        f.write(f"# Dramatis Personae - {topic['title']}\n\n")
        if characters:
            for character in characters:
                f.write(f"- {character}\n")
        else:
            f.write("No characters automatically identified. Please add manually.\n")

    timeline = create_timeline(posts)
    timeline_file = os.path.join(topic_dir, "timeline.md")
    with open(timeline_file, "w", encoding="utf-8") as f:
        f.write(f"# Timeline of Events - {topic['title']}\n\n")
        for event in timeline:
            f.write(f"## Event {event['event_number']} - {event['date']}\n\n")
            f.write(f"Author: {event['author']}\n\n")
            f.write(f"{event['summary']}\n\n")

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

    logger.info(f"Saved scenario files for '{topic['title']}'")
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

    logger.info(f"Created index for {forum_name} with {len(topics)} topics")

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

    logger.info("Created combined index of all scenarios")

def main():
    """Main function to extract all scenario data"""
    logger.info("Starting extraction process")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)

    all_topics = {}

    for forum_name, forum_path in FORUM_URLS.items():
        logger.info(f"Processing {forum_name} forum")

        forum_dir = os.path.join(OUTPUT_DIR, forum_name)
        os.makedirs(forum_dir, exist_ok=True)

        topics = get_forum_topics(forum_name, forum_path)
        all_topics[forum_name] = topics

        create_index(forum_name, topics)

        for i, topic in enumerate(topics):
            logger.info(f"Processing topic {i+1}/{len(topics)}: {topic['title']}")
            success = save_scenario_files(forum_name, topic)

            if not success:
                logger.error(f"Failed to process topic: {topic['title']}")

            sleep(2)

    create_combined_index(all_topics)

    logger.info("Extraction process completed")

if __name__ == "__main__":

    main()