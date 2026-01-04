import os
from pathlib import Path

# Define the base directory relative to the current working directory
base_dir = Path(os.getcwd())
llm_dir = base_dir / "LLM"

def check_directory_structure():
    """Check if the LLM directory structure is properly set up."""
    print("Checking LLM directory structure...")
    
    # Define expected directories
    expected_dirs = [
        "character_profiles",
        "in_game_documents/laws_policies",
        "in_game_documents/intelligence",
        "in_game_documents/technical", 
        "in_game_documents/diplomatic",
        "narratives/completed_scenarios",
        "narratives/unfinished_scenarios",
        "worldbuilding",
        "ooc_content/rules",
        "ooc_content/admin",
        "ooc_content/templates",
        "timeline",
        "metadata",
        "metadata/training_examples"
    ]
    
    # Check if each expected directory exists
    for dir_path in expected_dirs:
        full_path = llm_dir / dir_path
        if full_path.exists():
            print(f"✓ {dir_path} directory exists")
        else:
            print(f"✗ {dir_path} directory does not exist")
    
    # Check if training examples were created
    examples = [
        "metadata/training_examples/character_profile_example.jsonl",
        "metadata/training_examples/document_generation_example.jsonl",
        "metadata/training_examples/scenario_continuation_example.jsonl",
        "metadata/training_examples/timeline_integration_example.jsonl"
    ]
    
    print("\nChecking training examples...")
    for example in examples:
        example_path = llm_dir / example
        if example_path.exists():
            print(f"✓ {example} exists")
        else:
            print(f"✗ {example} does not exist")

def count_files_in_directories():
    """Count how many files are in each directory."""
    print("\nCounting files in each directory...")
    
    for root, dirs, files in os.walk(llm_dir):
        # Skip the root directory itself
        if root == str(llm_dir):
            continue
            
        # Get relative path from LLM directory
        rel_path = os.path.relpath(root, llm_dir)
        file_count = len(files)
        
        if file_count > 0:
            print(f"{rel_path}: {file_count} files")

if __name__ == "__main__":
    if llm_dir.exists():
        print(f"LLM directory exists at: {llm_dir}")
        check_directory_structure()
        count_files_in_directories()
    else:
        print(f"LLM directory does not exist at: {llm_dir}")
        print("Run the extract_llm_data.py script first to create the directory structure.")
