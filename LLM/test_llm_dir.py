#!/usr/bin/env python3
"""
Test script to verify that the LLM directory structure is set up correctly.
This script simply checks that all required directories exist.
"""

import os
import sys
from pathlib import Path

def check_directory_structure(base_dir="LLM"):
    """Check that all required directories exist in the LLM directory"""
    base_path = Path(base_dir)
    
    # Define expected directories
    expected_dirs = [
        # Main category directories
        "character_profiles",
        "in_game_documents",
        "narratives",
        "worldbuilding",
        "ooc_content",
        "unknown",
        "metadata",
        
        # Subdirectories
        "in_game_documents/laws_policies",
        "in_game_documents/intelligence",
        "in_game_documents/technical",
        "in_game_documents/diplomatic",
        "narratives/completed_scenarios",
        "narratives/unfinished_scenarios",
        "ooc_content/rules",
        "ooc_content/admin",
        "ooc_content/templates",
        "metadata/training_examples",
    ]
    
    # Check each directory
    missing_dirs = []
    for dir_path in expected_dirs:
        full_path = base_path / dir_path
        if not full_path.exists() or not full_path.is_dir():
            missing_dirs.append(str(full_path))
    
    # Print results
    if missing_dirs:
        print(f"ERROR: {len(missing_dirs)} required directories are missing:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
        return False
    else:
        print(f"SUCCESS: All required directories exist in {base_path}")
        return True

def check_example_files(base_dir="LLM"):
    """Check that all training example files exist"""
    base_path = Path(base_dir) / "metadata" / "training_examples"
    
    expected_files = [
        "character_profile_example.jsonl",
        "document_generation_example.jsonl",
        "scenario_continuation_example.jsonl",
        "timeline_integration_example.jsonl",
    ]
    
    # Check each file
    missing_files = []
    for file_name in expected_files:
        file_path = base_path / file_name
        if not file_path.exists() or not file_path.is_file():
            missing_files.append(str(file_path))
    
    # Print results
    if missing_files:
        print(f"ERROR: {len(missing_files)} example files are missing:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print(f"SUCCESS: All training example files exist in {base_path}")
        return True

def main():
    """Main function to run tests"""
    # Allow specifying a different base directory
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "LLM"
    
    print(f"Testing LLM directory structure in {base_dir}...\n")
    
    # Run tests
    dir_result = check_directory_structure(base_dir)
    print()
    file_result = check_example_files(base_dir)
    
    # Summary
    print("\nTest Summary:")
    if dir_result and file_result:
        print("✅ All tests passed! The directory structure is ready for data extraction.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
