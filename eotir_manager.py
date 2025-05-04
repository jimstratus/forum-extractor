#!/usr/bin/env python3
"""
EOTIR Manager
This script serves as a central management tool for all EOTIR processing components.
It can run individual components or a full processing pipeline.
"""

import os
import sys
import logging
import argparse
import subprocess
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("eotir_manager_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Available components
COMPONENTS = {
    "scenarios": "scenario_processor.py",
    "scraper": "scenario_scraper.py", 
    "indexer": "scenario_indexer.py",
    "llm": "extract_llm_data.py",
    "report": "generate_combined_report.py"
}

def run_component(component, args=None):
    """Run a specific EOTIR component"""
    if component not in COMPONENTS:
        logger.error(f"Unknown component: {component}")
        return False
    
    script_path = COMPONENTS[component]
    if not os.path.exists(script_path):
        logger.error(f"Component script not found: {script_path}")
        return False
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    logger.info(f"Running component: {component} ({script_path})")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Component {component} failed with return code {process.returncode}")
            logger.error(f"Error output: {stderr}")
            return False
        
        logger.info(f"Component {component} completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error running component {component}: {e}")
        return False

def run_all_components(args):
    """Run all EOTIR components in the correct order"""
    logger.info("Starting full EOTIR processing pipeline")
    
    # Define component order and their arguments
    pipeline = [
        ("scraper", None),  # None means no arguments for this component
        ("scenarios", None),
        ("indexer", None),
        ("llm", None),
        ("report", None)
    ]
    
    successful_components = []
    failed_components = []
    
    for component, component_args in pipeline:
        if run_component(component, component_args):
            successful_components.append(component)
        else:
            failed_components.append(component)
            if not args.continue_on_error:
                logger.error(f"Stopping pipeline due to failure in component: {component}")
                break
    
    # Log summary
    logger.info("EOTIR processing pipeline complete")
    logger.info(f"Successful components: {len(successful_components)}")
    logger.info(f"Failed components: {len(failed_components)}")
    
    if failed_components:
        logger.warning(f"Failed components: {', '.join(failed_components)}")
    
    return len(failed_components) == 0

def list_available_components():
    """List all available EOTIR components"""
    print("\nAvailable EOTIR components:")
    print("---------------------------")
    for name, script in COMPONENTS.items():
        exists = "✓" if os.path.exists(script) else "✗"
        print(f"{name:10} -> {script:25} [{exists}]")
    print("\n")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EOTIR Manager - Central management for EOTIR processing")
    
    # Component selection
    component_group = parser.add_argument_group("Component Selection")
    component_group.add_argument("--all", action="store_true", help="Run all components in order")
    component_group.add_argument("--component", help="Run a specific component", choices=COMPONENTS.keys())
    component_group.add_argument("--list", action="store_true", help="List available components")
    
    # Pipeline options
    pipeline_group = parser.add_argument_group("Pipeline Options")
    pipeline_group.add_argument("--continue-on-error", action="store_true", 
                        help="Continue the pipeline even if a component fails")
    
    # Component-specific arguments
    component_args_group = parser.add_argument_group("Component Arguments")
    component_args_group.add_argument("--args", nargs=argparse.REMAINDER, 
                               help="Arguments to pass to the component")
    
    args = parser.parse_args()
    
    # List components if requested
    if args.list:
        list_available_components()
        return 0
    
    # Validate arguments
    if not (args.all or args.component):
        parser.print_help()
        print("\nError: You must specify either --all or --component")
        return 1
    
    # Run the requested component or all components
    success = False
    if args.component:
        success = run_component(args.component, args.args)
    elif args.all:
        success = run_all_components(args)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
