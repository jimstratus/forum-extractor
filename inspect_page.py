import requests
from bs4 import BeautifulSoup
import json
import sys

def inspect_page(url):
    print(f"Inspecting URL: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Response status: {response.status_code} OK")
            soup = BeautifulSoup(response.text, "html.parser")
            
            # First check: Find post containers
            posts = soup.select(".ipsComment")
            print(f"Found {len(posts)} post elements with .ipsComment selector")
            
            # Examine post elements in detail
            if posts:
                print("\nExamining post elements:")
                for i, post in enumerate(posts[:2]):  # Look at first 2 posts max
                    print(f"\nPost #{i+1}:")
                    
                    # Check for author element
                    author_element = post.select_one(".ipsComment_author .ipsComment_content .cAuthorPane_author")
                    if author_element:
                        print(f"  Author element found: {author_element.text.strip()}")
                    else:
                        print("  Author element not found with selector '.ipsComment_author .ipsComment_content .cAuthorPane_author'")
                        
                        # Try alternative author selectors
                        alt_author_selectors = [
                            ".ipsComment_author", 
                            ".cAuthorPane_author",
                            ".author", 
                            ".username"
                        ]
                        for selector in alt_author_selectors:
                            alt_author = post.select_one(selector)
                            if alt_author:
                                print(f"  Alternative author element found with '{selector}': {alt_author.text.strip()}")
                    
                    # Check for date element
                    date_element = post.select_one(".ipsComment_meta time")
                    if date_element:
                        print(f"  Date element found: {date_element.get('datetime')}")
                    else:
                        print("  Date element not found with selector '.ipsComment_meta time'")
                    
                    # Check for content element
                    content_element = post.select_one(".ipsComment_content .cPost_content")
                    if content_element:
                        content_sample = content_element.text.strip()[:100]
                        print(f"  Content element found: {len(content_sample)} chars, sample: {content_sample}...")
                    else:
                        print("  Content element not found with selector '.ipsComment_content .cPost_content'")
                        
                        # Try alternative content selectors
                        alt_content_selectors = [
                            ".post_body", 
                            ".post-content",
                            ".message-body",
                            ".content"
                        ]
                        for selector in alt_content_selectors:
                            alt_content = post.select_one(selector)
                            if alt_content:
                                content_sample = alt_content.text.strip()[:100]
                                print(f"  Alternative content element found with '{selector}': {len(content_sample)} chars, sample: {content_sample}...")
            
            if len(posts) == 0:
                print("\nTrying alternative selectors for posts...")
                # Try other possible selectors for posts
                alternative_selectors = [
                    ".post",
                    ".message",
                    ".topic-post",
                    ".comment",
                    ".ipb_table",
                    ".ipsfocus_post",
                    "article",
                    ".cPost"
                ]
                
                for selector in alternative_selectors:
                    elements = soup.select(selector)
                    print(f"Selector '{selector}': {len(elements)} elements found")
            
            # Print the main content area ID or class names
            main_content = soup.select_one("#content, .ipsLayout_content, main, .main-content")
            if main_content:
                print(f"Main content container found: {main_content.name} with classes: {main_content.get('class', [])}")
                
                # Count top-level children
                children = list(main_content.children)
                print(f"Main content has {len(children)} top-level children")
                
                # Find all div elements with ID attributes in main content
                divs_with_id = main_content.select("div[id]")
                print(f"Found {len(divs_with_id)} divs with IDs in main content:")
                for div in divs_with_id[:5]:  # Show first 5 as examples
                    print(f"  - #{div.get('id')} with classes: {div.get('class', [])}")
            else:
                print("Could not identify main content container.")
            
            # Save a sample of the HTML for further analysis
            with open("page_sample.html", "w", encoding="utf-8") as f:
                # Get the first 10000 characters as a sample
                f.write(response.text[:10000])
            print("Saved first 10000 characters of HTML to page_sample.html")
            
            # Print some basic page info
            title = soup.title.text if soup.title else "No title found"
            print(f"Page title: {title}")
            
            # Check for login forms which might indicate authentication required
            login_forms = soup.select("form[action*='login']")
            if login_forms:
                print("WARNING: Login form detected - page may require authentication")
            
        else:
            print(f"Error: HTTP status {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    # Use a topic URL from the Red Scenario forum
    url = "https://nexus.eotir.com/topic/168-red-scenario-rules/"
    
    # If URL provided as command line argument, use that instead
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    inspect_page(url)
