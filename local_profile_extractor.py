import os
import sys
import json
import logging
import docx2txt
import PyPDF2
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("local_extraction_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Output directory
OUTPUT_DIR = os.path.join("LLM", "character_profiles")

# Character profile directories
CHARACTER_DIRS = [
    os.path.join("EOTIR RPG", "Character Profiles"),
    os.path.join("EOTIR Novels", "Chronicles"),
    os.path.join("EOTIR Novels", "People")
]

def extract_character_name(filename):
    """Extract character name from filename"""
    # Remove file extension
    name = os.path.splitext(os.path.basename(filename))[0]
    
    # Remove prefixes like "Char Profile - " or "CharProf-"
    prefixes = ["Char Profile - ", "CharProf-", "Character Profile - "]
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    # Clean up the name
    name = name.replace("_", " ").strip()
    
    return name

def extract_docx_content(file_path):
    """Extract text content from docx file"""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        logger.error(f"Error extracting content from {file_path}: {e}")
        return None

def extract_pdf_content(file_path):
    """Extract text content from pdf file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting content from {file_path}: {e}")
        return None

def extract_txt_content(file_path):
    """Extract text content from txt file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error extracting content from {file_path}: {e}")
        return None

def save_character_profile(name, content, source_path):
    """Save character profile to file"""
    if not content:
        return None
        
    try:
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Create a safe filename from character name
        safe_name = name.replace(" ", "_").replace(".", "_")
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
        
        # Add source directory to filename to avoid conflicts
        source_dir = os.path.basename(os.path.dirname(source_path))
        source_dir = source_dir.replace(" ", "_").lower()
        
        filename = f"{safe_name}_local_{source_dir}.txt"
        
        # Add metadata to the content
        metadata = f"# Character Profile: {name}\n\n"
        metadata += f"**Source File:** {source_path}\n"
        metadata += f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        full_content = metadata + content
        
        # Save content to file
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Don't overwrite if file exists, create a new version
        if os.path.exists(output_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_local_{source_dir}_{timestamp}.txt"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(full_content)
            
        logger.info(f"Saved character profile to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error saving character profile for {name}: {e}")
        return None

def process_character_file(file_path):
    """Process a single character profile file"""
    logger.info(f"Processing file: {file_path}")
    
    # Extract character name from filename
    character_name = extract_character_name(file_path)
    
    # Extract content based on file extension
    content = None
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.docx':
        content = extract_docx_content(file_path)
    elif file_ext == '.pdf':
        content = extract_pdf_content(file_path)
    elif file_ext == '.txt':
        content = extract_txt_content(file_path)
    else:
        logger.warning(f"Unsupported file format: {file_ext}")
        return None
    
    if content:
        # Save character profile
        output_path = save_character_profile(character_name, content, file_path)
        return {
            "character_name": character_name,
            "source_file": file_path,
            "output_path": output_path
        }
    else:
        logger.warning(f"Failed to extract content from {file_path}")
        return None

def scan_directory(directory_path):
    """Scan directory for character profile files"""
    logger.info(f"Scanning directory: {directory_path}")
    
    if not os.path.exists(directory_path):
        logger.warning(f"Directory does not exist: {directory_path}")
        return []
    
    profiles = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Check if file is a potential character profile
            if any(keyword in file.lower() for keyword in ["char", "profile", "bio"]) and file_ext in ['.docx', '.pdf', '.txt']:
                result = process_character_file(file_path)
                if result:
                    profiles.append(result)
    
    logger.info(f"Found {len(profiles)} character profiles in {directory_path}")
    return profiles

def main():
    all_profiles = []
    
    # Process each directory
    for directory in CHARACTER_DIRS:
        profiles = scan_directory(directory)
        all_profiles.extend(profiles)
    
    # Generate summary
    summary = {
        "total_directories": len(CHARACTER_DIRS),
        "total_profiles": len(all_profiles),
        "directories": CHARACTER_DIRS,
        "profiles": all_profiles
    }
    
    # Save summary
    metadata_dir = os.path.join("LLM", "metadata")
    os.makedirs(metadata_dir, exist_ok=True)
    
    summary_path = os.path.join(metadata_dir, "local_extraction_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as file:
        json.dump(summary, file, indent=2)
    
    # Generate human-readable report
    report_path = os.path.join(metadata_dir, "local_extraction_report.md")
    with open(report_path, 'w', encoding='utf-8') as file:
        file.write("# EOTIR Local Character Profiles Extraction Report\n\n")
        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        file.write("## Processing Summary\n\n")
        file.write(f"- Directories scanned: {len(CHARACTER_DIRS)}\n")
        file.write(f"- Character profiles extracted: {len(all_profiles)}\n\n")
        
        file.write("## Directory Details\n\n")
        for directory in CHARACTER_DIRS:
            dir_profiles = [p for p in all_profiles if directory in p["source_file"]]
            file.write(f"### {directory}\n\n")
            file.write(f"- Profiles found: {len(dir_profiles)}\n")
            if dir_profiles:
                file.write("- Characters extracted:\n")
                for profile in dir_profiles:
                    file.write(f"  - {profile['character_name']} ({os.path.basename(profile['source_file'])})\n")
            file.write("\n")
    
    logger.info(f"Extraction complete. Extracted {len(all_profiles)} character profiles from {len(CHARACTER_DIRS)} directories.")
    logger.info(f"Results saved to {OUTPUT_DIR}")
    logger.info(f"Summary report saved to {report_path}")

if __name__ == "__main__":
    main()
