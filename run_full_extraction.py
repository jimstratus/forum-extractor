#!/usr/bin/env python3
"""
EOTIR Full Extraction Script
Runs the complete extraction pipeline: extract → process → index → report
"""

import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run the full extraction pipeline."""
    try:
        # Import the scenario manager
        from scenario_manager import import_modules, extract_scenarios, process_scenarios, index_scenarios
        import argparse
        
        logger.info("Starting full extraction pipeline...")
        
        # Create a namespace with default arguments
        args = argparse.Namespace(
            forum=None,
            login=False,
            output=None,
            scenario=None,
            year=None,
            no_excel=False,
            no_dashboard=False,
            no_timeline=False
        )
        
        # Import required modules
        modules = import_modules()
        
        # Step 1: Extract scenarios from forums
        logger.info("Step 1: Extracting scenarios from forums...")
        extract_scenarios(args, modules)
        
        # Step 2: Process extracted scenarios
        logger.info("Step 2: Processing scenarios...")
        process_scenarios(args, modules)
        
        # Step 3: Generate indexes and reports
        logger.info("Step 3: Generating indexes and reports...")
        index_scenarios(args, modules)
        
        # Step 4: Generate combined reports
        logger.info("Step 4: Generating combined reports...")
        try:
            import subprocess
            subprocess.run([sys.executable, "generate_combined_report.py"], check=False)
        except Exception as e:
            logger.warning(f"Could not generate combined reports: {e}")
        
        logger.info("Full extraction pipeline completed successfully")
        return 0
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())