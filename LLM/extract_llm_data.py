import os
import re
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("extraction_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Categories and their target directories
CATEGORIES = {
    "character_profiles": os.path.join("LLM", "character_profiles"),
    "in_game_documents/laws_policies": os.path.join("LLM", "in_game_documents", "laws_policies"),
    "in_game_documents/intelligence": os.path.join("LLM", "in_game_documents", "intelligence"),
    "in_game_documents/technical": os.path.join("LLM", "in_game_documents", "technical"),
    "in_game_documents/diplomatic": os.path.join("LLM", "in_game_documents", "diplomatic"),
    "narratives/completed_scenarios": os.path.join("LLM", "narratives", "completed_scenarios"),
    "narratives/unfinished_scenarios": os.path.join("LLM", "narratives", "unfinished_scenarios"),
    "worldbuilding": os.path.join("LLM", "worldbuilding"),
    "ooc_content/rules": os.path.join("LLM", "ooc_content", "rules"),
    "ooc_content/admin": os.path.join("LLM", "ooc_content", "admin"),
    "ooc_content/templates": os.path.join("LLM", "ooc_content", "templates"),
    "unknown": os.path.join("LLM", "unknown")
}

# File patterns for categorization
CATEGORIZATION_PATTERNS = {
    # Character profiles
    r"(?i)(char\s*prof|character|personnel\s*file|profile)": "character_profiles",
    r"(?i)\.docx?$.*people": "character_profiles",
    
    # In-game documents - laws and policies
    r"(?i)(charter|declaration|act|law|policy|resolution|statute)": "in_game_documents/laws_policies",
    r"(?i)(governance|regulation|rule\s*set)": "in_game_documents/laws_policies",
    
    # In-game documents - intelligence
    r"(?i)(intelligence|briefing|report|security|surveillance)": "in_game_documents/intelligence",
    r"(?i)(classified|confidential|secret|top\s*secret)": "in_game_documents/intelligence",
    r"(?i)(IRSB|COMPNOR)": "in_game_documents/intelligence",
    
    # In-game documents - technical
    r"(?i)(technical|specification|manual|schematic|blueprint)": "in_game_documents/technical",
    r"(?i)(ship|vessel|starfighter|cruiser|destroyer)": "in_game_documents/technical",
    r"(?i)(engineering|system|design|prototype)": "in_game_documents/technical",
    
    # In-game documents - diplomatic
    r"(?i)(treaty|diplomatic|agreement|accord|memorandum)": "in_game_documents/diplomatic",
    r"(?i)(negotiation|delegation|ambassador|envoy|peace)": "in_game_documents/diplomatic",
    r"(?i)(alliance|faction|foreign|relation)": "in_game_documents/diplomatic",
    
    # Narratives - completed scenarios
    r"(?i)(scenario|mission\s*log|after\s*action|completed)": "narratives/completed_scenarios",
    r"(?i)(story|tale|chronicle|saga|narrative)": "narratives/completed_scenarios",
    
    # Narratives - unfinished scenarios
    r"(?i)(draft|outline|concept|idea|unfinished|partial)": "narratives/unfinished_scenarios",
    r"(?i)(wip|work\s*in\s*progress|notes|brainstorm)": "narratives/unfinished_scenarios",
    
    # Worldbuilding
    r"(?i)(world\s*building|lore|history|timeline|universe)": "worldbuilding",
    r"(?i)(planet|system|sector|region|map|galaxy)": "worldbuilding",
    r"(?i)(culture|species|race|civilization|society)": "worldbuilding",
    r"(?i)(technology|artifact|relic|ancient)": "worldbuilding",
    
    # OOC - Rules
    r"(?i)(rules|guideline|instruction|procedure|protocol)": "ooc_content/rules",
    r"(?i)(handbook|manual|guide|reference|how\s*to)": "ooc_content/rules",
    
    # OOC - Admin
    r"(?i)(admin|staff|moderator|leadership|management)": "ooc_content/admin",
    r"(?i)(meeting|minutes|discussion|planning|strategy)": "ooc_content/admin",
    r"(?i)(announcement|update|bulletin|newsletter)": "ooc_content/admin",
    
    # OOC - Templates
    r"(?i)(template|form|application|questionnaire)": "ooc_content/templates",
    r"(?i)(standard|format|boilerplate|starter)": "ooc_content/templates",
}

def extract_text_from_file(file_path):
    """Extract text from various file formats"""
    file_ext = file_path.suffix.lower()
    
    # Text files
    if file_ext in ['.txt', '.md', '.rtf']:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None
    
    # Word documents
    elif file_ext in ['.doc', '.docx']:
        try:
            # Try to use docx2txt if available
            try:
                import docx2txt
                return docx2txt.process(file_path)
            except ImportError:
                # Fallback to python-docx
                try:
                    import docx
                    doc = docx.Document(file_path)
                    return "\n".join([para.text for para in doc.paragraphs])
                except ImportError:
                    logger.warning("Neither docx2txt nor python-docx is installed. Skipping Word document.")
                    return None
        except Exception as e:
            logger.error(f"Error processing Word document {file_path}: {e}")
            return None
    
    # PDF files
    elif file_ext == '.pdf':
        try:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(file_path)
                text = ""
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text() + "\n"
                return text
            except ImportError:
                logger.warning("PyPDF2 is not installed. Skipping PDF file.")
                return None
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return None
    
    # Unsupported format
    else:
        logger.info(f"Unsupported file format: {file_ext}")
        return None

def categorize_content(file_path, content):
    """Categorize content based on filename, path, and content patterns"""
    
    # Convert to string for pattern matching
    path_str = str(file_path)
    
    # Character profiles directory takes precedence
    if "character" in path_str.lower() or "profiles" in path_str.lower():
        return "character_profiles"
    
    # Check filename and path against patterns
    for pattern, category in CATEGORIZATION_PATTERNS.items():
        if re.search(pattern, path_str, re.IGNORECASE):
            return category
    
    # If content is available, check content patterns
    if content:
        content_sample = content[:1000]  # Check first 1000 chars to determine type
        
        # Look for character profile indicators
        if re.search(r"(?i)(name|age|gender|species|rank|homeworld)", content_sample):
            if re.search(r"(?i)(personality|background|history|appearance)", content_sample):
                return "character_profiles"
        
        # Look for technical document indicators
        if re.search(r"(?i)(specifications|dimensions|armament|propulsion|crew complement)", content_sample):
            return "in_game_documents/technical"
        
        # Look for intelligence document indicators
        if re.search(r"(?i)(classified|security clearance|intelligence report|threat assessment)", content_sample):
            return "in_game_documents/intelligence"
    
    # Default to unknown if no patterns match
    return "unknown"

def process_file(file_path, root_dir, dataset_dir):
    """Process a single file and save to appropriate category"""
    
    # Skip if the file is too large (> 10MB)
    if os.path.getsize(file_path) > 10 * 1024 * 1024:
        logger.warning(f"Skipping large file: {file_path}")
        return None
    
    # Extract text from file
    content = extract_text_from_file(file_path)
    if not content:
        logger.warning(f"Failed to extract content from {file_path}")
        return None
    
    # Categorize content
    category = categorize_content(file_path, content)
    
    # Create a clean filename
    rel_path = os.path.relpath(file_path, root_dir)
    clean_name = re.sub(r'[^\w\s-]', '_', rel_path)
    clean_name = re.sub(r'\s+', '_', clean_name)
    output_filename = f"{clean_name}.txt"
    
    # Create output directory
    output_dir = os.path.join(dataset_dir, category)
    os.makedirs(output_dir, exist_ok=True)
    
    # Save content to file
    output_path = os.path.join(output_dir, output_filename)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved to {output_path}")
        
        # Return metadata
        return {
            "original_path": str(file_path),
            "processed_path": output_path,
            "category": category,
            "size_bytes": len(content),
            "word_count": len(content.split())
        }
    except Exception as e:
        logger.error(f"Error saving to {output_path}: {e}")
        return None

def extract_zip_files(source_dir):
    """Extract zip files in the source directory"""
    for item in os.listdir(source_dir):
        if item.endswith('.zip'):
            zip_path = os.path.join(source_dir, item)
            extract_dir = os.path.splitext(zip_path)[0]
            
            # Skip if already extracted
            if os.path.exists(extract_dir):
                logger.info(f"Skipping extraction, directory already exists: {extract_dir}")
                continue
                
            logger.info(f"Extracting {zip_path} to {extract_dir}")
            try:
                os.makedirs(extract_dir, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            except Exception as e:
                logger.error(f"Error extracting {zip_path}: {e}")

def process_directory(source_dir, output_dir, recursive=True):
    """Process all files in a directory"""
    results = {
        "total_files": 0,
        "processed_files": 0,
        "skipped_files": 0,
        "error_files": 0,
        "categories": {},
        "files": []
    }
    
    # Extract zip files first if needed
    extract_zip_files(source_dir)
    
    # Create metadata directory
    metadata_dir = os.path.join(output_dir, "metadata")
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Walk through directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(('.txt', '.md', '.rtf', '.doc', '.docx', '.pdf')):
                results["total_files"] += 1
                file_path = os.path.join(root, file)
                
                try:
                    # Process file
                    file_result = process_file(Path(file_path), Path(source_dir), output_dir)
                    
                    if file_result:
                        results["processed_files"] += 1
                        results["files"].append(file_result)
                        
                        # Update category stats
                        category = file_result["category"]
                        if category not in results["categories"]:
                            results["categories"][category] = 0
                        results["categories"][category] += 1
                    else:
                        results["skipped_files"] += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results["error_files"] += 1
                    
        # Exit if not recursive
        if not recursive:
            break
    
    # Save processing summary
    summary_path = os.path.join(metadata_dir, "processing_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate human-readable report
    report_path = os.path.join(metadata_dir, "processing_report.md")
    with open(report_path, 'w') as f:
        f.write("# EOTIR LLM Dataset Processing Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Processing Summary\n\n")
        f.write(f"- Total files discovered: {results['total_files']}\n")
        f.write(f"- Files successfully processed: {results['processed_files']}\n")
        f.write(f"- Files skipped: {results['skipped_files']}\n")
        f.write(f"- Processing errors: {results['error_files']}\n\n")
        
        f.write("## Category Distribution\n\n")
        for category, count in sorted(results["categories"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / results['processed_files']) * 100 if results['processed_files'] > 0 else 0
            f.write(f"- {category}: {count} files ({percentage:.1f}%)\n")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Extract and process text from EOTIR files for LLM training.")
    parser.add_argument("--novels", action="store_true", help="Process the EOTIR Novels directory")
    parser.add_argument("--rpg", action="store_true", help="Process the EOTIR RPG directory")
    parser.add_argument("--all", action="store_true", help="Process all directories")
    parser.add_argument("--output", default="LLM", help="Output directory for processed data")
    
    args = parser.parse_args()
    
    # Set up source directories
    source_dirs = []
    if args.novels or args.all:
        source_dirs.append("EOTIR Novels")
    if args.rpg or args.all:
        source_dirs.append("EOTIR RPG")
        source_dirs.append("EOTIR RPG MOVE")
        source_dirs.append("EOTIR RPG Throne")
    
    # If no specific directories selected, prompt user
    if not source_dirs:
        print("Please select at least one source directory to process.")
        print("Use --novels for EOTIR Novels, --rpg for EOTIR RPG, or --all for both.")
        return
    
    # Process each source directory
    all_results = {
        "total_files": 0,
        "processed_files": 0,
        "skipped_files": 0,
        "error_files": 0,
        "categories": {},
        "source_dirs": source_dirs
    }
    
    for source_dir in source_dirs:
        logger.info(f"Processing directory: {source_dir}")
        results = process_directory(source_dir, args.output)
        
        # Aggregate results
        all_results["total_files"] += results["total_files"]
        all_results["processed_files"] += results["processed_files"]
        all_results["skipped_files"] += results["skipped_files"]
        all_results["error_files"] += results["error_files"]
        
        # Aggregate category counts
        for category, count in results["categories"].items():
            if category not in all_results["categories"]:
                all_results["categories"][category] = 0
            all_results["categories"][category] += count
    
    logger.info(f"Processing complete. Processed {all_results['processed_files']} files.")
    logger.info(f"Results saved to {args.output}/metadata/")

if __name__ == "__main__":
    main()
