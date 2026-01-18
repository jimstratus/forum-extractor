#!/usr/bin/env python3
"""
EOTIR Character Profile Scraper

Extracts character profiles from EOTIR Nexus forum and converts them
to markdown files compatible with eotir-admin-tools data/characters format.

Forum Sources:
- Primary Characters: https://nexus.eotir.com/forum/62-character-profiles/
- Secondary Characters: https://nexus.eotir.com/forum/125-secondary-characters/
- Character Archives: https://nexus.eotir.com/forum/124-character-archives/
"""

import os
import re
import sys
import json
import logging
import argparse
from datetime import datetime
from time import sleep
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration
BASE_URL = "https://nexus.eotir.com"
CHARACTER_FORUM_URLS = {
    "Primary_Characters": "/forum/62-character-profiles/",
    "Secondary_Characters": "/forum/125-secondary-characters/",
    "Character_Archives": "/forum/124-character-archives/"
}

# Output directories
OUTPUT_DIR = "Characters"
EOTIR_ADMIN_TOOLS_DIR = os.path.normpath("c:/EOTIR/eotir-admin-tools/data/characters")
LOG_FILE = "character_extraction_log.txt"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CharacterScraper:
    """Scraper for character profile pages with rate limiting."""
    
    def __init__(self, requests_per_minute=30):
        self.session = requests.Session()
        # Add User-Agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.requests_per_minute = requests_per_minute
        self.min_delay = 60.0 / self.requests_per_minute
        self.last_request_time = 0
        self.total_requests = 0
        
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limiting."""
        import time
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_delay:
                sleep_time = self.min_delay - elapsed
                if sleep_time > 0.1:
                    logger.debug(f"Rate limiting: waiting {sleep_time:.1f}s")
                sleep(sleep_time)
        self.last_request_time = time.time()
        
    def fetch_page(self, url, timeout=60, retries=3):
        """Fetch and parse a page, respecting rate limits."""
        for attempt in range(retries):
            try:
                self._wait_for_rate_limit()
                self.total_requests += 1
                response = self.session.get(url, timeout=timeout)
                
                if response.status_code == 429:
                    self.requests_per_minute = max(5, self.requests_per_minute - 5)
                    self.min_delay = 60.0 / self.requests_per_minute
                    logger.warning(f"Rate limit hit. Reducing to {self.requests_per_minute} req/min")
                    sleep(30)
                    continue
                    
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{retries} failed for {url}: {str(e)}")
                if attempt < retries - 1:
                    sleep(5 * (attempt + 1))  # Exponential backoff
                    continue
                logger.error(f"Failed to fetch {url} after {retries} attempts")
                return None
        return None


def slugify(text):
    """Convert text to a URL-friendly slug (kebab-case)."""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep spaces and hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text


def extract_character_name_from_title(title):
    """
    Extract character name from topic title.
    
    Forum titles often have formats like:
    - "John Smith"
    - "John Smith - Jedi Master"
    - "[NPC] John Smith"
    - "Admiral John Smith"
    """
    # Remove common prefixes/suffixes
    cleaned = title.strip()
    
    # Remove bracketed prefixes like [NPC], [WIP], etc.
    cleaned = re.sub(r'^\[[^\]]+\]\s*', '', cleaned)
    
    # Remove " - " suffix (job title or description after name)
    if ' - ' in cleaned:
        cleaned = cleaned.split(' - ')[0].strip()
    
    # Remove " | " suffix 
    if ' | ' in cleaned:
        cleaned = cleaned.split(' | ')[0].strip()
    
    return cleaned.strip()


def parse_species_from_content(content):
    """Try to extract species from character profile content."""
    species_patterns = [
        r'(?:Species|Race)[\s:]+([A-Za-z\'\-]+)',
        r'(?:is|was) (?:a|an) ([A-Za-z\'\-]+)',
        r'\|[\s]*Species[\s]*\|[\s]*([A-Za-z\'\-]+)',
    ]
    
    for pattern in species_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            species = match.group(1).strip()
            # Filter out common false positives
            if species.lower() not in ['the', 'a', 'an', 'is', 'was', 'born']:
                return species.title()
    
    return "Unknown"


def parse_homeworld_from_content(content):
    """Try to extract homeworld from character profile content."""
    homeworld_patterns = [
        r'(?:Homeworld|Home World|Home)[\s:]+([A-Za-z\'\-\s]+?)(?:\n|\||$)',
        r'(?:born on|from) ([A-Za-z\'\-]+)',
        r'\|[\s]*Homeworld[\s]*\|[\s]*([A-Za-z\'\-\s]+?)[\s]*\|',
    ]
    
    for pattern in homeworld_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            homeworld = match.group(1).strip()
            # Filter out common false positives
            if len(homeworld) > 2 and homeworld.lower() not in ['the', 'a', 'an']:
                return homeworld.title()
    
    return None


def parse_birth_year_from_content(content):
    """Try to extract birth year (IRY) from character profile content."""
    birth_patterns = [
        r'(?:Born|Birth|DOB|Date of Birth)[\s:]+(\-?\d+)\s*(?:IRY|BBY|ABY)?',
        r'(?:Born|Birth)[\s:]+.*?(\-?\d+)\s*IRY',
        r'\|[\s]*(?:Born|Birth|DOB)[\s]*\|[\s]*(\-?\d+)',
        r'(\-?\d+)\s*IRY[\s]*(?:\(|\-|–)',  # Pattern like "15 IRY (birth)"
    ]
    
    for pattern in birth_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            try:
                year = int(match.group(1))
                # Sanity check: reasonable year range
                if -100 <= year <= 100:
                    return year
            except ValueError:
                continue
    
    return None


def parse_death_year_from_content(content):
    """Try to extract death year (IRY) from character profile content."""
    death_patterns = [
        r'(?:Died|Death|Deceased)[\s:]+(\-?\d+)\s*(?:IRY)?',
        r'(?:Died|Death)[\s:]+.*?(\-?\d+)\s*IRY',
        r'\|[\s]*(?:Died|Death)[\s]*\|[\s]*(\-?\d+)',
    ]
    
    for pattern in death_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            try:
                year = int(match.group(1))
                if -100 <= year <= 100:
                    return year
            except ValueError:
                continue
    
    return None


def parse_status_from_content(content, death_iry):
    """Determine character status from content."""
    if death_iry is not None:
        return "deceased"
    
    status_patterns = {
        'deceased': [r'\b(?:deceased|dead|died|killed)\b'],
        'missing': [r'\b(?:missing|disappeared|vanished)\b'],
        'unknown': [r'\b(?:status unknown|whereabouts unknown)\b'],
    }
    
    content_lower = content.lower()
    for status, patterns in status_patterns.items():
        for pattern in patterns:
            if re.search(pattern, content_lower):
                return status
    
    return "alive"


def determine_character_tags(content, forum_category):
    """Generate relevant tags based on content and source."""
    tags = []
    
    # Add source category tag
    if forum_category == "Primary_Characters":
        tags.append("primary-character")
    elif forum_category == "Secondary_Characters":
        tags.append("secondary-character")
    elif forum_category == "Character_Archives":
        tags.append("archived")
    
    # Look for role/affiliation keywords
    content_lower = content.lower()
    
    # Military tags
    if any(term in content_lower for term in ['admiral', 'navy', 'fleet', 'naval']):
        tags.append("navy")
    if any(term in content_lower for term in ['general', 'army', 'soldier', 'colonel', 'major']):
        tags.append("army")
    if any(term in content_lower for term in ['military', 'forces']):
        tags.append("military")
    
    # Political/government tags
    if any(term in content_lower for term in ['sovereign', 'emperor', 'empress', 'throne']):
        tags.append("sovereign")
    if any(term in content_lower for term in ['minister', 'ministry', 'government']):
        tags.append("government")
    if any(term in content_lower for term in ['senator', 'legislature', 'council']):
        tags.append("legislature")
    if any(term in content_lower for term in ['high council']):
        tags.append("high-council")
    
    # Agency tags
    if 'compnor' in content_lower:
        tags.append("compnor")
    if 'iris' in content_lower:
        tags.append("iris")
    if 'irin' in content_lower:
        tags.append("irin")
    
    # Noble/house tags
    if any(term in content_lower for term in ['noble', 'house', 'lord', 'lady', 'duke', 'duchess']):
        tags.append("noble")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return unique_tags


# Topic titles to skip (forum meta topics, not actual character profiles)
SKIP_TOPICS = {
    "character archives",
    "secondary characters", 
    "new character profile format",
    "(old) character profile format",
    "request to update your character profile",
    "character creation notice",
    "thoughts on age",
    "character profile format",
    "character profile template",
    "how to create a character",
    "rules",
    "announcements",
    "pinned",
}


def should_skip_topic(title):
    """Check if a topic should be skipped (not a character profile)."""
    title_lower = title.lower().strip()
    
    # Skip exact matches
    if title_lower in SKIP_TOPICS:
        return True
    
    # Skip topics that are clearly forum links (link to other forums)
    if title_lower.startswith("→"):
        return True
        
    # Skip topics starting with certain keywords
    skip_prefixes = ["how to", "rules:", "announcement:", "notice:"]
    for prefix in skip_prefixes:
        if title_lower.startswith(prefix):
            return True
    
    return False


def extract_character_topics(forum_category, forum_path, scraper):
    """Get all character topics from a forum."""
    forum_url = urljoin(BASE_URL, forum_path)
    logger.info(f"Fetching character topics from {forum_category} at {forum_url}")
    
    topics = []
    seen_urls = set()  # Track URLs to detect when we're getting duplicates
    page = 1
    max_pages = 50  # Safety limit to prevent infinite loops
    
    while page <= max_pages:
        page_url = f"{forum_url}?page={page}"
        soup = scraper.fetch_page(page_url)
        
        if not soup:
            logger.warning(f"Failed to fetch page {page} from {forum_url}")
            break
        
        # Try multiple selectors for topic elements
        topic_elements = soup.select(".ipsDataItem")
        if not topic_elements:
            topic_elements = soup.select("li.ipsDataItem")
        if not topic_elements:
            topic_elements = soup.select("[data-rowid]")
        
        logger.info(f"Page {page}: Found {len(topic_elements)} topic elements")
        
        if not topic_elements:
            if page == 1:
                logger.warning(f"No topics found on first page of {forum_category}")
            break
        
        new_topics_on_page = 0
        
        for topic in topic_elements:
            try:
                # Find title element
                title_element = topic.select_one(".ipsDataItem_title a")
                if not title_element:
                    title_element = topic.select_one("a.ipsDataItem_title")
                if not title_element:
                    title_element = topic.select_one("h4 a")
                
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                topic_url = title_element.get("href")
                
                # Skip meta/admin topics that aren't character profiles
                if should_skip_topic(title):
                    logger.debug(f"Skipping non-character topic: {title}")
                    continue
                
                # Skip if this is a subforum link (URL contains /forum/ instead of /topic/)
                if topic_url and '/forum/' in topic_url:
                    logger.debug(f"Skipping subforum link: {title}")
                    continue
                
                # Ensure absolute URL
                if topic_url and not topic_url.startswith('http'):
                    topic_url = urljoin(BASE_URL, topic_url)
                
                # Skip if we've already seen this URL (indicates we're looping)
                if topic_url in seen_urls:
                    continue
                seen_urls.add(topic_url)
                new_topics_on_page += 1
                
                # Find author
                author_element = topic.select_one(".ipsDataItem_main .ipsDataItem_meta a")
                if not author_element:
                    author_element = topic.select_one(".ipsDataItem_meta a[href*='profile']")
                author = author_element.text.strip() if author_element else "Unknown"
                
                topics.append({
                    "title": title,
                    "url": topic_url,
                    "author": author,
                    "forum_category": forum_category
                })
                
            except Exception as e:
                logger.error(f"Error parsing topic: {str(e)}")
        
        logger.info(f"Page {page}: {new_topics_on_page} new topics (total: {len(topics)})")
        
        # If no new topics found on this page, we're done (reached end or looping)
        if new_topics_on_page == 0:
            logger.info(f"No new topics on page {page}, stopping pagination")
            break
        
        # Check for next page using multiple selectors
        next_page = soup.select_one("a[rel='next']")
        if not next_page:
            # Try alternative pagination selectors
            next_page = soup.select_one(".ipsPagination_next a:not(.ipsPagination_inactive)")
            if not next_page:
                next_page = soup.select_one("li.ipsPagination_next:not(.ipsPagination_inactive) a")
        
        if not next_page:
            logger.info(f"No next page link found after page {page}")
            break
        
        page += 1
        sleep(1)
    
    if page > max_pages:
        logger.warning(f"Hit max page limit ({max_pages}) for {forum_category}")
    
    logger.info(f"Found {len(topics)} character topics in {forum_category}")
    return topics


def extract_character_profile(topic_url, scraper):
    """Extract the first post content from a character profile topic."""
    logger.info(f"Extracting character profile from {topic_url}")
    
    soup = scraper.fetch_page(topic_url)
    if not soup:
        return None
    
    # Find the first post (the character profile)
    post_element = soup.select_one(".ipsComment")
    if not post_element:
        post_element = soup.select_one("article.ipsComment")
    if not post_element:
        post_element = soup.select_one("[data-commentid]")
    if not post_element:
        post_element = soup.select_one(".cPost")
    
    if not post_element:
        logger.warning(f"No post content found at {topic_url}")
        return None
    
    # Extract author
    author_element = post_element.select_one(".cAuthorPane_author")
    if not author_element:
        author_element = post_element.select_one(".ipsComment_author a")
    author = author_element.text.strip() if author_element else "Unknown"
    
    # Extract date
    date_element = post_element.select_one(".ipsComment_meta time")
    if not date_element:
        date_element = post_element.select_one("time[datetime]")
    post_date = date_element.get("datetime") if date_element else None
    
    # Extract content
    content_element = post_element.select_one(".ipsComment_content")
    if not content_element:
        content_element = post_element.select_one(".cPost_content")
    if not content_element:
        content_element = post_element.select_one("[data-role='commentContent']")
    
    if not content_element:
        logger.warning(f"No content element found at {topic_url}")
        return None
    
    # Clean up the content
    for elem in content_element.select(".ipsComment_reportLink, .ipsBadge, .ipsButton"):
        elem.decompose()
    
    # Get both raw HTML and markdown versions
    html_content = str(content_element)
    markdown_content = md(html_content)
    
    # Clean up markdown
    markdown_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown_content)
    markdown_content = markdown_content.strip()
    
    return {
        "author": author,
        "post_date": post_date,
        "html": html_content,
        "markdown": markdown_content
    }


def create_character_file(topic, profile_data, output_dir):
    """
    Create a character markdown file in eotir-admin-tools format.
    
    Returns the path to the created file.
    """
    title = topic["title"]
    character_name = extract_character_name_from_title(title)
    character_id = slugify(character_name)
    
    content = profile_data["markdown"]
    
    # Extract metadata from content
    species = parse_species_from_content(content)
    homeworld = parse_homeworld_from_content(content)
    birth_iry = parse_birth_year_from_content(content)
    death_iry = parse_death_year_from_content(content)
    status = parse_status_from_content(content, death_iry)
    tags = determine_character_tags(content, topic["forum_category"])
    
    # Build frontmatter
    frontmatter = {
        "id": character_id,
        "name": character_name,
        "species": species,
        "birth_iry": birth_iry if birth_iry is not None else 0,
        "status": status,
    }
    
    # Add optional fields
    if death_iry is not None:
        frontmatter["death_iry"] = death_iry
    else:
        frontmatter["death_iry"] = None
    
    if homeworld:
        frontmatter["homeworld"] = homeworld
    
    frontmatter["house"] = None
    frontmatter["image"] = None
    frontmatter["tags"] = tags
    
    today = datetime.now().strftime("%Y-%m-%d")
    frontmatter["created_at"] = today
    frontmatter["updated_at"] = today
    
    # Add source metadata
    frontmatter["source_url"] = topic["url"]
    frontmatter["source_forum"] = topic["forum_category"]
    frontmatter["source_author"] = topic["author"]
    
    # Create markdown content
    file_content = "---\n"
    file_content += yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    file_content += "---\n\n"
    
    # Add character name header
    file_content += f"# {character_name}\n\n"
    
    # Add a note about extraction
    file_content += f"> ⚠️ **AUTO-EXTRACTED** from [forum post]({topic['url']}) — Review and edit for accuracy.\n\n"
    
    # Add the original profile content
    file_content += "## Original Profile\n\n"
    file_content += content
    file_content += "\n\n"
    
    # Add placeholder sections for the eotir-admin-tools format
    file_content += "## Roles\n\n"
    file_content += "<!-- TODO: Extract roles from profile content above -->\n\n"
    file_content += "| Organization | Title | Rank | Start IRY | End IRY | Notes |\n"
    file_content += "|--------------|-------|------|-----------|---------|-------|\n"
    file_content += "| unknown | Unknown | — | 0 | — | Needs research |\n\n"
    
    file_content += "## Relationships\n\n"
    file_content += "<!-- TODO: Extract relationships from profile content -->\n\n"
    
    file_content += "## Notes\n\n"
    file_content += f"- **Source:** {topic['forum_category']}\n"
    file_content += f"- **Original Author:** {topic['author']}\n"
    if profile_data.get("post_date"):
        file_content += f"- **Posted:** {profile_data['post_date']}\n"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Write file
    filename = f"{character_id}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Handle duplicate filenames
    counter = 1
    while os.path.exists(filepath):
        filename = f"{character_id}-{counter}.md"
        filepath = os.path.join(output_dir, filename)
        counter += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    logger.info(f"Created character file: {filepath}")
    return filepath


def create_extraction_index(all_characters, output_dir):
    """Create an index of all extracted characters."""
    index_path = os.path.join(output_dir, "_extraction_index.md")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# Character Extraction Index\n\n")
        f.write(f"**Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for category in ["Primary_Characters", "Secondary_Characters", "Character_Archives"]:
            chars = [c for c in all_characters if c.get("forum_category") == category]
            if chars:
                f.write(f"## {category.replace('_', ' ')}\n\n")
                f.write("| Name | Status | File |\n")
                f.write("|------|--------|------|\n")
                for char in chars:
                    name = extract_character_name_from_title(char["title"])
                    status = char.get("extraction_status", "unknown")
                    filepath = char.get("filepath", "—")
                    if filepath and filepath != "—":
                        filename = os.path.basename(filepath)
                        f.write(f"| {name} | {status} | [{filename}](./{filename}) |\n")
                    else:
                        f.write(f"| {name} | {status} | — |\n")
                f.write("\n")
    
    logger.info(f"Created extraction index: {index_path}")


def main():
    """Main function to extract all character profiles."""
    parser = argparse.ArgumentParser(description="Extract EOTIR character profiles from forum")
    parser.add_argument("--output", "-o", default=OUTPUT_DIR,
                        help=f"Output directory (default: {OUTPUT_DIR})")
    parser.add_argument("--admin-tools", "-a", action="store_true",
                        help="Also copy to eotir-admin-tools data/characters")
    parser.add_argument("--forum", "-f", choices=list(CHARACTER_FORUM_URLS.keys()) + ["all"],
                        default="all", help="Which forum to extract from")
    parser.add_argument("--limit", "-l", type=int, default=None,
                        help="Limit number of characters to extract (for testing)")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="List topics without extracting")
    
    args = parser.parse_args()
    
    logger.info("Starting character profile extraction")
    logger.info(f"Output directory: {args.output}")
    
    # Create output directories
    os.makedirs(args.output, exist_ok=True)
    
    scraper = CharacterScraper()
    all_characters = []
    
    # Determine which forums to process
    forums_to_process = CHARACTER_FORUM_URLS if args.forum == "all" else {
        args.forum: CHARACTER_FORUM_URLS[args.forum]
    }
    
    for forum_category, forum_path in forums_to_process.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {forum_category}")
        logger.info(f"{'='*60}")
        
        # Create category subdirectory
        category_dir = os.path.join(args.output, forum_category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Get all topics
        topics = extract_character_topics(forum_category, forum_path, scraper)
        
        if args.dry_run:
            logger.info(f"\nDRY RUN - Would extract {len(topics)} characters:")
            for i, topic in enumerate(topics[:20] if args.limit else topics):
                logger.info(f"  {i+1}. {topic['title']}")
            if len(topics) > 20:
                logger.info(f"  ... and {len(topics) - 20} more")
            all_characters.extend(topics)
            continue
        
        # Apply limit if specified
        if args.limit:
            topics = topics[:args.limit]
        
        # Process each topic
        for i, topic in enumerate(topics):
            logger.info(f"\nProcessing {i+1}/{len(topics)}: {topic['title']}")
            
            try:
                profile_data = extract_character_profile(topic["url"], scraper)
                
                if profile_data:
                    filepath = create_character_file(topic, profile_data, category_dir)
                    topic["filepath"] = filepath
                    topic["extraction_status"] = "success"
                else:
                    topic["extraction_status"] = "no_content"
                    logger.warning(f"No content extracted for: {topic['title']}")
                    
            except Exception as e:
                topic["extraction_status"] = "error"
                logger.error(f"Error processing {topic['title']}: {str(e)}")
            
            all_characters.append(topic)
            
            # Rate limiting pause between topics
            sleep(1)
    
    # Create index
    create_extraction_index(all_characters, args.output)
    
    # Copy to admin-tools if requested
    if args.admin_tools and not args.dry_run:
        logger.info(f"\nCopying to {EOTIR_ADMIN_TOOLS_DIR}")
        import shutil
        
        os.makedirs(EOTIR_ADMIN_TOOLS_DIR, exist_ok=True)
        
        # Copy all .md files (excluding index and schema)
        for root, dirs, files in os.walk(args.output):
            for file in files:
                if file.endswith('.md') and not file.startswith('_'):
                    src = os.path.join(root, file)
                    dst = os.path.join(EOTIR_ADMIN_TOOLS_DIR, file)
                    
                    # Don't overwrite existing files
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
                        logger.info(f"Copied: {file}")
                    else:
                        logger.info(f"Skipped (exists): {file}")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("EXTRACTION SUMMARY")
    logger.info(f"{'='*60}")
    
    success = len([c for c in all_characters if c.get("extraction_status") == "success"])
    no_content = len([c for c in all_characters if c.get("extraction_status") == "no_content"])
    errors = len([c for c in all_characters if c.get("extraction_status") == "error"])
    
    logger.info(f"Total topics found: {len(all_characters)}")
    if not args.dry_run:
        logger.info(f"Successfully extracted: {success}")
        logger.info(f"No content found: {no_content}")
        logger.info(f"Errors: {errors}")
        logger.info(f"\nOutput directory: {os.path.abspath(args.output)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
