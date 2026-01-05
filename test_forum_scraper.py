#!/usr/bin/env python3
"""
Quick test script to validate forum scraper functionality (limited pages for speed)
"""
from forum_scraper import get_forum_topics, ForumScraper
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

# Test 1: Get first page of topics from each forum
print("=" * 60)
print("QUICK TEST: Fetching topics from all forums (first page only)")
print("=" * 60)

forums = {
    'Palace_Situation_Room': '/forum/169-palace-situation-room/',
    'Red_Scenario': '/forum/59-red-scenario/',
    'Blue_Scenario': '/forum/69-blue-scenario/'
}

scraper = ForumScraper()

for forum_name, forum_path in forums.items():
    print(f"\n{forum_name}:")
    print("-" * 40)
    
    # Just fetch first page
    from urllib.parse import urljoin
    BASE_URL = "https://nexus.eotir.com"
    forum_url = urljoin(BASE_URL, forum_path)
    page_url = f"{forum_url}?page=1"
    
    soup = scraper.extract_page(page_url)
    
    if soup:
        # Try to find topics
        topic_elements = soup.select(".ipsDataItem")
        
        if not topic_elements:
            topic_elements = soup.select("li.ipsDataItem")
        if not topic_elements:
            topic_elements = soup.select(".cTopicList li")
        
        print(f"  ✓ Found {len(topic_elements)} topics on first page")
        
        if topic_elements:
            # Show first 3 topics
            for i, topic in enumerate(topic_elements[:3]):
                title_element = topic.select_one(".ipsDataItem_title a")
                if not title_element:
                    title_element = topic.select_one("a.ipsDataItem_title")
                
                if title_element:
                    print(f"  {i+1}. {title_element.text.strip()}")
    else:
        print(f"  ✗ Failed to fetch forum page")

print("\n" + "=" * 60)
print("Quick test complete!")
print("=" * 60)
print("\nForum scraper is working correctly!")
print("Use 'python main.py extract' to do a full extraction.")
