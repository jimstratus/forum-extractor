import os
import re
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
SOURCE_DIR = os.path.join("LLM", "character_profiles")
TARGET_DIR = os.path.join("LLM", "character_profiles_processed")
METADATA_DIR = os.path.join("LLM", "metadata")
DATASET_SUMMARY_PATH = os.path.join(METADATA_DIR, "character_dataset_summary.json")
DATASET_REPORT_PATH = os.path.join(METADATA_DIR, "character_dataset_report.md")

# Character name normalization patterns
PREFIXES_TO_REMOVE = [
    r'^Char(acter)?\s*Profile\s*[-:]?\s*',
    r'^CharProf\s*[-:]?\s*'
]

def normalize_character_name(name):
    """Normalize character name for consistent matching"""
    if not name:
        return ""
    
    # Remove common prefixes
    for pattern in PREFIXES_TO_REMOVE:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Remove special characters and normalize spaces
    name = re.sub(r'[^\w\s\'-]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def extract_character_name_from_file(file_path):
    """Extract character name from file content or filename"""
    try:
        # First try to extract from content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)  # Read first 2000 chars for efficiency
            
            # Look for character name in headers or metadata
            name_patterns = [
                r'# Character Profile: ([^\n]+)',
                r'Character(?:\s+Profile)?(?:\s*:+\s*|\s+of\s+|\s+for\s+)([^|\n]+)',
                r'(?:Name|CHARACTER NAME)[^\w\n]*:?\s*([^,.\n]+)',
                r'\*\*(?:Name|Full Name)\*\*:?\s*([^,.\n]+)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return normalize_character_name(match.group(1))
        
        # If no name found in content, extract from filename
        filename = os.path.basename(file_path)
        name = os.path.splitext(filename)[0]
        
        # Remove source indicators and extensions
        name = re.sub(r'_(?:profiles|characters|archives|local_\w+)(?:_\d+)?$', '', name)
        
        # Remove potential duplicated name sections if they exist
        if '__' in name:
            name = name.split('__')[0]
            
        return normalize_character_name(name)
                
    except Exception as e:
        logger.error(f"Error extracting name from {file_path}: {e}")
        return os.path.splitext(os.path.basename(file_path))[0]

def group_character_files():
    """Group files by character name"""
    if not os.path.exists(SOURCE_DIR):
        logger.error(f"Source directory not found: {SOURCE_DIR}")
        return None
    
    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.txt')]
    
    if not files:
        logger.error("No character profile files found")
        return None
    
    # Group files by normalized character name
    character_groups = defaultdict(list)
    unidentified_files = []
    
    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        character_name = extract_character_name_from_file(file_path)
        
        if character_name and len(character_name) > 2 and not character_name.startswith('s') and character_name.lower() not in ['of', 'character', 'with', 'that', 'for', 'nts']:
            character_groups[character_name].append(filename)
        else:
            unidentified_files.append(filename)
    
    return {
        "character_groups": dict(character_groups),
        "unidentified_files": unidentified_files
    }

def prepare_character_dataset(groups_data):
    """Prepare character dataset from grouped files"""
    if not groups_data:
        return None
    
    character_groups = groups_data["character_groups"]
    unidentified_files = groups_data["unidentified_files"]
    
    # Create target directory
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    processed_characters = []
    
    # Process each character group
    for character_name, files in character_groups.items():
        logger.info(f"Processing character: {character_name}")
        
        safe_name = re.sub(r'[^\w\s]', '_', character_name).strip()
        safe_name = re.sub(r'\s+', '_', safe_name)
        
        # Create output file path
        output_path = os.path.join(TARGET_DIR, f"{safe_name}.txt")
        
        # Combine content from all files
        combined_content = f"# Character Profile: {character_name}\n\n"
        combined_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        combined_content += f"**Source Files:** {len(files)}\n\n"
        
        file_sources = []
        forum_sources = []
        local_sources = []
        
        for filename in files:
            file_path = os.path.join(SOURCE_DIR, filename)
            
            # Determine source type
            if '_profiles.txt' in filename or '_characters.txt' in filename or '_archives.txt' in filename:
                source_type = "Web Forum"
                forum_sources.append(filename)
            elif '_local_' in filename:
                source_type = "Local File"
                local_sources.append(filename)
            else:
                source_type = "Unknown"
            
            file_sources.append({"filename": filename, "type": source_type})
            
            # Extract content (skip the header)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Skip the header if it exists
                    content_parts = content.split("\n\n", 3)
                    if len(content_parts) >= 3:
                        content = content_parts[2]
                    
                    # Add section for this source
                    combined_content += f"\n## Source: {filename}\n\n"
                    combined_content += content.strip() + "\n\n"
                    combined_content += "-" * 50 + "\n\n"
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
        
        # Write combined content
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            logger.info(f"Created unified profile at {output_path}")
            
            # Add to processed list
            processed_characters.append({
                "character_name": character_name,
                "output_file": os.path.basename(output_path),
                "source_count": len(files),
                "forum_sources": len(forum_sources),
                "local_sources": len(local_sources),
                "sources": file_sources
            })
        except Exception as e:
            logger.error(f"Error writing combined profile for {character_name}: {e}")
    
    # Copy unidentified files
    unidentified_dir = os.path.join(TARGET_DIR, "_unidentified")
    os.makedirs(unidentified_dir, exist_ok=True)
    
    for filename in unidentified_files:
        source_path = os.path.join(SOURCE_DIR, filename)
        target_path = os.path.join(unidentified_dir, filename)
        
        try:
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied unidentified file to {target_path}")
        except Exception as e:
            logger.error(f"Error copying file {filename}: {e}")
    
    return {
        "processed_characters": len(processed_characters),
        "unidentified_files": len(unidentified_files),
        "characters": processed_characters
    }

def generate_dataset_report(dataset_data):
    """Generate dataset report"""
    if not dataset_data:
        return False
    
    # Save JSON summary
    with open(DATASET_SUMMARY_PATH, 'w', encoding='utf-8') as f:
        json.dump(dataset_data, f, indent=2)
    
    # Create markdown report
    with open(DATASET_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("# EOTIR Character Profiles - Dataset Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- Total characters processed: {dataset_data['processed_characters']}\n")
        f.write(f"- Unidentified files: {dataset_data['unidentified_files']}\n\n")
        
        f.write("## Characters\n\n")
        
        # Sort characters by name
        characters = sorted(dataset_data['characters'], key=lambda x: x['character_name'])
        
        for char in characters:
            f.write(f"### {char['character_name']}\n\n")
            f.write(f"- Output file: {char['output_file']}\n")
            f.write(f"- Source count: {char['source_count']}\n")
            f.write(f"- Forum sources: {char['forum_sources']}\n")
            f.write(f"- Local sources: {char['local_sources']}\n\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. Review processed character profiles for accuracy\n")
        f.write("2. Run manual checks on characters with multiple source files\n")
        f.write("3. Check the unidentified files folder for any important profiles that were not properly categorized\n")
        f.write("4. Incorporate these profiles into your LLM training dataset\n")
    
    logger.info(f"Dataset report saved to {DATASET_REPORT_PATH}")
    logger.info(f"Dataset summary saved to {DATASET_SUMMARY_PATH}")
    
    return True

def main():
    logger.info("Starting character profile dataset preparation")
    
    # Group files by character
    groups_data = group_character_files()
    
    if not groups_data:
        logger.error("Failed to group character files")
        return
    
    # Prepare dataset
    dataset_data = prepare_character_dataset(groups_data)
    
    if not dataset_data:
        logger.error("Failed to prepare character dataset")
        return
    
    # Generate report
    if generate_dataset_report(dataset_data):
        logger.info("Character profile dataset preparation completed successfully")
    else:
        logger.error("Failed to generate dataset report")

if __name__ == "__main__":
    main()
