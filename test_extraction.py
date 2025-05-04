import os
import sys
from forum_scraper import get_forum_topics, extract_posts_from_topic, save_scenario_files, create_index

# Test forum extraction for just Red Scenario forum
def test_extraction():
    forum_name = "Red_Scenario"
    forum_path = "/forum/59-red-scenario/"
    
    print(f"Testing extraction for {forum_name} forum...")
    
    # Ensure output directories exist
    os.makedirs(os.path.join("Scenarios", forum_name), exist_ok=True)
    os.makedirs(os.path.join("Scenarios", "Indexes"), exist_ok=True)
    
    # Get topics from forum
    topics = get_forum_topics(forum_name, forum_path)
    
    if not topics:
        print("No topics found in the forum.")
        return
    
    print(f"Found {len(topics)} topics in {forum_name} forum.")
    
    # Create index for this forum
    create_index(forum_name, topics)
    
    # Process topics for testing (skip first if it's a rules/announcement post)
    if topics:
        # Try to process the second topic if available (skipping potential pinned announcement)
        test_topic_index = min(1, len(topics) - 1)
        topic = topics[test_topic_index]
        print(f"Processing topic: {topic['title']}")
        success = save_scenario_files(forum_name, topic)
        
        if success:
            print(f"Successfully processed topic: {topic['title']}")
        else:
            print(f"Failed to process topic: {topic['title']}")
            
            # If the second topic fails, try one more
            if len(topics) > 2:
                topic = topics[2]
                print(f"Trying another topic: {topic['title']}")
                success = save_scenario_files(forum_name, topic)
                
                if success:
                    print(f"Successfully processed topic: {topic['title']}")
                else:
                    print(f"Failed to process topic: {topic['title']}")

if __name__ == "__main__":
    test_extraction()
