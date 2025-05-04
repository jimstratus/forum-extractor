#!/usr/bin/env python3
"""
EOTIR Scenario Manager
This script coordinates the entire workflow for scenario extraction, processing and indexing.
"""

import os
import sys
import logging
import argparse
import importlib
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scenario_manager_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def import_modules():
    """Import the required modules using importlib"""
    logger.info("Importing modules...")
    modules = {}
    
    try:
        modules['scraper'] = importlib.import_module('scenario_scraper')
        logger.info("Successfully imported scenario_scraper")
    except ImportError as e:
        logger.error(f"Failed to import scenario_scraper: {e}")
        modules['scraper'] = None
    
    try:
        modules['processor'] = importlib.import_module('scenario_processor')
        logger.info("Successfully imported scenario_processor")
    except ImportError as e:
        logger.error(f"Failed to import scenario_processor: {e}")
        modules['processor'] = None
    
    try:
        modules['indexer'] = importlib.import_module('scenario_indexer')
        logger.info("Successfully imported scenario_indexer")
    except ImportError as e:
        logger.error(f"Failed to import scenario_indexer: {e}")
        modules['indexer'] = None
    
    return modules

def extract_scenarios(args, modules):
    """Extract scenarios from forums"""
    logger.info("Starting scenario extraction...")
    
    if not modules['scraper']:
        logger.error("Scraper module not available. Cannot extract scenarios.")
        return False
    
    try:
        # Prepare arguments for the scraper
        scraper_args = argparse.Namespace()
        scraper_args.forum = args.forum if hasattr(args, 'forum') else None
        scraper_args.login = args.login if hasattr(args, 'login') else False
        scraper_args.output = args.output if hasattr(args, 'output') else None
        
        # Call the scraper's main function
        logger.info(f"Calling scraper with args: {scraper_args}")
        modules['scraper'].main(scraper_args)
        logger.info("Scenario extraction completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during scenario extraction: {e}")
        return False

def process_scenarios(args, modules):
    """Process scenarios to generate supplementary files"""
    logger.info("Starting scenario processing...")
    
    if not modules['processor']:
        logger.error("Processor module not available. Cannot process scenarios.")
        return False
    
    try:
        # Prepare arguments for the processor
        processor_args = argparse.Namespace()
        processor_args.scenario = args.scenario if hasattr(args, 'scenario') else None
        processor_args.forum = args.forum if hasattr(args, 'forum') else None
        processor_args.year = args.year if hasattr(args, 'year') else None
        
        # Call the processor's main function
        logger.info(f"Calling processor with args: {processor_args}")
        modules['processor'].main(processor_args)
        logger.info("Scenario processing completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during scenario processing: {e}")
        return False

def index_scenarios(args, modules):
    """Generate indexes and reports for scenarios"""
    logger.info("Starting scenario indexing...")
    
    if not modules['indexer']:
        logger.error("Indexer module not available. Cannot index scenarios.")
        return False
    
    try:
        # Prepare arguments for the indexer
        indexer_args = argparse.Namespace()
        indexer_args.no_excel = args.no_excel if hasattr(args, 'no_excel') else False
        indexer_args.no_dashboard = args.no_dashboard if hasattr(args, 'no_dashboard') else False
        indexer_args.no_timeline = args.no_timeline if hasattr(args, 'no_timeline') else False
        
        # Call the indexer's main function
        logger.info(f"Calling indexer with args: {indexer_args}")
        modules['indexer'].main(indexer_args)
        logger.info("Scenario indexing completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during scenario indexing: {e}")
        return False

def run_all(args, modules):
    """Run the full extraction → processing → indexing pipeline"""
    logger.info("Starting full scenario management pipeline...")
    
    # Extract scenarios
    if not extract_scenarios(args, modules):
        logger.error("Extraction phase failed. Continuing with processing and indexing...")
    
    # Process scenarios
    if not process_scenarios(args, modules):
        logger.error("Processing phase failed. Continuing with indexing...")
    
    # Index scenarios
    if not index_scenarios(args, modules):
        logger.error("Indexing phase failed.")
        return False
    
    logger.info("Full scenario management pipeline completed")
    return True

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="EOTIR Scenario Manager - Coordinate scenario extraction, processing, and indexing")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run-all command
    run_all_parser = subparsers.add_parser('run-all', help='Run the full pipeline (extract, process, index)')
    run_all_parser.add_argument('--login', action='store_true', help='Login to the forum for extraction')
    run_all_parser.add_argument('--forum', help='Specify a particular forum URL')
    run_all_parser.add_argument('--output', help='Output directory for scenarios')
    run_all_parser.add_argument('--scenario', help='Process a specific scenario file')
    run_all_parser.add_argument('--year', help='Process scenarios from a specific year')
    run_all_parser.add_argument('--no-excel', action='store_true', help='Skip generating Excel index')
    run_all_parser.add_argument('--no-dashboard', action='store_true', help='Skip generating HTML dashboard')
    run_all_parser.add_argument('--no-timeline', action='store_true', help='Skip generating timeline report')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract scenarios from forums')
    extract_parser.add_argument('--login', action='store_true', help='Login to the forum')
    extract_parser.add_argument('--forum', help='URL of the forum to scrape')
    extract_parser.add_argument('--output', help='Output directory for scenarios')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process scenarios')
    process_parser.add_argument('--scenario', help='Process a specific scenario file')
    process_parser.add_argument('--forum', help='Process scenarios from a specific forum')
    process_parser.add_argument('--year', help='Process scenarios from a specific year')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Generate indexes and reports')
    index_parser.add_argument('--no-excel', action='store_true', help='Skip generating Excel index')
    index_parser.add_argument('--no-dashboard', action='store_true', help='Skip generating HTML dashboard')
    index_parser.add_argument('--no-timeline', action='store_true', help='Skip generating timeline report')
    
    return parser.parse_args()

def main():
    """Main execution function"""
    # Parse command-line arguments
    args = parse_args()
    
    # Import required modules
    modules = import_modules()
    
    # Check if all required modules are available
    if not all(modules.values()):
        logger.error("Not all required modules are available. Please check your installation.")
        return 1
    
    # Execute the requested command
    if args.command == 'run-all':
        success = run_all(args, modules)
    elif args.command == 'extract':
        success = extract_scenarios(args, modules)
    elif args.command == 'process':
        success = process_scenarios(args, modules)
    elif args.command == 'index':
        success = index_scenarios(args, modules)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1
    
    # Return status code based on success
    return 0 if success else 1

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Starting EOTIR Scenario Manager at {start_time}")
    
    exit_code = main()
    
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    logger.info(f"EOTIR Scenario Manager completed at {end_time}")
    logger.info(f"Total execution time: {elapsed_time}")
    
    sys.exit(exit_code)
