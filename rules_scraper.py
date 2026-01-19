"""
EOTIR Rules Scraper

Extracts game rules from the EOTIR Nexus Game Rules forum.
Adapted from the scenario forum scraper for rule-specific content.

Usage:
    python rules_scraper.py                    # Extract all rules
    python rules_scraper.py --url <topic_url>  # Extract single rule topic
"""

import os
import re
import json
import time
import logging
import argparse
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
RULES_FORUM_URL = "/forum/145-game-rules/"
OUTPUT_DIR = "Rules"
INDEX_DIR = os.path.join(OUTPUT_DIR, "Indexes")
LOG_FILE = "rules_extraction_log.txt"

# Rule ID patterns (e.g., CAT-001, FATE-005, MIL-003)
RULE_ID_PATTERN = r'\[?([A-Z]{2,6})-(\d{3})\]?'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RulesScraper:
    """Scraper for EOTIR game rules forum."""
    
    def __init__(self, requests_per_minute=30):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60.0 / self.requests_per_minute
        self.last_request_time = 0
        self.rate_limit_hits = 0
        self.total_requests = 0

    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limiting."""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_delay:
                sleep_time = self.min_delay - elapsed
                if sleep_time > 0.1:
                    logger.debug(f"Rate limiting: waiting {sleep_time:.1f}s")
                sleep(sleep_time)
        self.last_request_time = time.time()

    def extract_page(self, url, timeout=30):
        """Extract and parse a page, respecting rate limits."""
        try:
            self._wait_for_rate_limit()
            self.total_requests += 1
            response = self.session.get(url, timeout=timeout)

            if response.status_code == 429:
                self.rate_limit_hits += 1
                self.requests_per_minute = max(5, self.requests_per_minute - 5)
                self.min_delay = 60.0 / self.requests_per_minute
                logger.warning(f"Rate limit hit. Reducing rate to {self.requests_per_minute} requests/minute")
                time.sleep(30)
                return self.extract_page(url, timeout)

            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None


def extract_rule_id_from_title(title):
    """Extract rule ID (e.g., CAT-001) from title if present."""
    match = re.search(RULE_ID_PATTERN, title)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None


def extract_rule_category(rule_id):
    """Determine rule category from rule ID prefix."""
    if not rule_id:
        return "other"
    
    prefix = rule_id.split('-')[0] if '-' in rule_id else rule_id
    
    categories = {
        'CAT': 'character',       # Character Administration Team
        'FATE': 'force',          # Force Administration & Training Enforcement
        'MIL': 'military',        # Military rules
        'GOV': 'government',      # Government rules
        'RP': 'roleplay',         # Roleplay rules
        'GEN': 'general',         # General rules
        'ADM': 'admin',           # Admin rules
        'SEN': 'senate',          # Senate rules
    }
    
    return categories.get(prefix, 'other')


def get_rules_topics():
    """Get all rule topics from the Game Rules forum."""
    forum_url = urljoin(BASE_URL, RULES_FORUM_URL)
    logger.info(f"Fetching rules from {forum_url}")

    topics = []
    page = 1
    scraper = RulesScraper()

    while True:
        page_url = f"{forum_url}?page={page}"
        soup = scraper.extract_page(page_url)

        if not soup:
            logger.warning(f"Failed to fetch page {page} from {forum_url}")
            break

        # Try multiple selectors for topic elements
        topic_elements = soup.select(".ipsDataItem")
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

                rule_id = extract_rule_id_from_title(title)
                category = extract_rule_category(rule_id)

                topics.append({
                    "title": title,
                    "url": topic_url,
                    "author": author,
                    "rule_id": rule_id,
                    "category": category,
                    "status": "active"  # Default status
                })

            except Exception as e:
                logger.error(f"Error parsing topic: {str(e)}")

        next_page = soup.select_one("a[rel='next']")
        if not next_page:
            break

        page += 1
        sleep(1)

    logger.info(f"Found {len(topics)} rules topics")
    return topics


def extract_rule_content(topic_url):
    """Extract rule content from a topic (typically just the first post)."""
    logger.info(f"Extracting rule content from {topic_url}")
    scraper = RulesScraper()
    
    soup = scraper.extract_page(topic_url)
    if not soup:
        return None
    
    # Rules are typically in the first post only
    post_elements = soup.select(".ipsComment")
    if not post_elements:
        post_elements = soup.select("article.ipsComment")
    if not post_elements:
        post_elements = soup.select("[data-commentid]")
        
    if not post_elements:
        logger.warning(f"No posts found at {topic_url}")
        return None
    
    # Get the first post (the rule itself)
    first_post = post_elements[0]
    
    try:
        # Extract author
        author_element = first_post.select_one(".cAuthorPane_author")
        if not author_element:
            author_element = first_post.select_one(".ipsComment_author a")
        author = author_element.text.strip() if author_element else "Unknown"
        
        # Extract date
        date_element = first_post.select_one(".ipsComment_meta time")
        if not date_element:
            date_element = first_post.select_one("time[datetime]")
        date = date_element.get("datetime") if date_element else "Unknown"
        
        # Extract content
        content_element = first_post.select_one(".ipsComment_content")
        if not content_element:
            content_element = first_post.select_one(".cPost_content")
        if not content_element:
            content_element = first_post.select_one("[data-role='commentContent']")
            
        if not content_element:
            return None
        
        # Clean up content
        for report_link in content_element.select(".ipsComment_reportLink"):
            report_link.decompose()
        for element in content_element.select(".ipsBadge, .ipsQuote_citation, .ipsButton"):
            element.decompose()
        
        content = md(str(content_element))
        
        # Clean up markdown
        content = re.sub(r'\*\s+\+\s+\[Report\].*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'Posted.*?\d{4}', '', content)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        return {
            "author": author,
            "date": date,
            "content": content
        }
        
    except Exception as e:
        logger.error(f"Error extracting rule content: {str(e)}")
        return None


def save_rule_file(topic):
    """Save a rule to a markdown file."""
    # Create safe filename
    if topic.get("rule_id"):
        safe_name = topic["rule_id"]
    else:
        safe_name = re.sub(r'[^\w\s-]', '', topic["title"]).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
    
    # Create category directory
    category = topic.get("category", "other")
    category_dir = os.path.join(OUTPUT_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    
    logger.info(f"→ Extracting '{topic['title']}'...")
    rule_content = extract_rule_content(topic["url"])
    
    if not rule_content:
        logger.warning(f"No content found for {topic['title']}")
        return False
    
    # Create the rule file
    rule_file = os.path.join(category_dir, f"{safe_name}.md")
    
    with open(rule_file, "w", encoding="utf-8") as f:
        # Write YAML frontmatter
        f.write("---\n")
        f.write(f"id: {topic.get('rule_id') or safe_name}\n")
        f.write(f"title: \"{topic['title']}\"\n")
        f.write(f"category: {category}\n")
        f.write(f"author: {topic['author']}\n")
        f.write(f"url: {topic['url']}\n")
        f.write(f"status: {topic.get('status', 'active')}\n")
        f.write(f"extracted_date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("---\n\n")
        
        # Write the title
        f.write(f"# {topic['title']}\n\n")
        
        # Write metadata
        if topic.get("rule_id"):
            f.write(f"**Rule ID:** {topic['rule_id']}  \n")
        f.write(f"**Category:** {category.title()}  \n")
        f.write(f"**Author:** {rule_content['author']}  \n")
        f.write(f"**Posted:** {rule_content['date']}  \n")
        f.write(f"**Source:** [{topic['url']}]({topic['url']})\n\n")
        
        f.write("---\n\n")
        
        # Write the rule content
        f.write(rule_content["content"])
    
    logger.info(f"Saved rule: {rule_file}")
    return True


def create_rules_index(topics):
    """Create an index of all rules."""
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    # Combined index
    index_file = os.path.join(INDEX_DIR, "rules_index.md")
    
    with open(index_file, "w", encoding="utf-8") as f:
        f.write("# EOTIR Game Rules Index\n\n")
        f.write(f"*Extracted on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(f"**Total Rules:** {len(topics)}\n\n")
        
        # Group by category
        categories = {}
        for topic in topics:
            cat = topic.get("category", "other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(topic)
        
        f.write("## Rules by Category\n\n")
        
        for category, cat_topics in sorted(categories.items()):
            f.write(f"### {category.title()} ({len(cat_topics)} rules)\n\n")
            f.write("| Rule ID | Title | Author | Status |\n")
            f.write("|---------|-------|--------|--------|\n")
            
            for topic in sorted(cat_topics, key=lambda x: x.get("rule_id") or "ZZZ"):
                rule_id = topic.get("rule_id") or "—"
                f.write(f"| {rule_id} | [{topic['title']}]({topic['url']}) | {topic['author']} | {topic.get('status', 'active')} |\n")
            
            f.write("\n")
    
    logger.info(f"Created rules index with {len(topics)} rules")
    
    # Also save as JSON for programmatic access
    json_file = os.path.join(INDEX_DIR, "rules_index.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)


def main():
    """Main function to extract all game rules."""
    parser = argparse.ArgumentParser(description="Extract EOTIR game rules from forum")
    parser.add_argument("--url", help="Extract a single rule topic by URL")
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    if args.url:
        # Extract single topic
        logger.info(f"Extracting single rule from: {args.url}")
        topic = {
            "title": "Single Rule",
            "url": args.url,
            "author": "Unknown",
            "rule_id": None,
            "category": "other"
        }
        save_rule_file(topic)
    else:
        # Extract all rules
        logger.info("Starting rules extraction process")
        
        topics = get_rules_topics()
        
        if not topics:
            logger.error("No rule topics found!")
            return
        
        create_rules_index(topics)
        
        for i, topic in enumerate(topics):
            logger.info(f"Processing rule {i+1}/{len(topics)}: {topic['title']}")
            success = save_rule_file(topic)
            
            if not success:
                logger.error(f"Failed to process rule: {topic['title']}")
            
            sleep(2)  # Be respectful with requests
        
        logger.info(f"Rules extraction completed. Extracted {len(topics)} rules.")


if __name__ == "__main__":
    main()
