#!/usr/bin/env python3
"""
EOTIR Scenario Manager Demo
This script creates a sample scenario and runs it through the processing pipeline.
"""

import os
import sys
import logging
import argparse
import yaml
import json
import glob
import importlib
from datetime import datetime
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("demo_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base directories
SCENARIOS_DIR = os.path.join("Scenarios")
DEMO_SCENARIO_DIR = os.path.join(SCENARIOS_DIR, "Red_Scenario", "34_IRY")

# Sample scenario content
SAMPLE_SCENARIO = """---
title: Like Unto the Romans
forum: Red_Scenario
year: 34 IRY
status: In Progress
extraction_date: 2025-05-03
url: https://nexus.eotir.com/topic/2362-like-unto-the-romans-34-iry/
---

# Like Unto the Romans [34 IRY]

*Posted by Supreme_Ruler - May 15, 2024*

The situation in the Western Reaches has become increasingly concerning. Reports of unrest and growing anti-Imperial sentiment have reached the attention of the Supreme Ruler's Office. The Senate has been debating appropriate responses for weeks, but little concrete action has been taken.

As dawn broke over the Imperial Palace on Coruscant, Emperor Joseph Stratus stood on his private balcony, observing the endless cityscape. This was no longer the Republic of old - this was his Empire, his Imperial Republic. For thirty-four years he had guided it, sometimes with a gentle hand, other times with the necessary firmness that leadership required.

"They're growing bolder in the Western Reaches," he said without turning, aware that his loyal aide had quietly entered the chamber behind him.

"Yes, Your Excellency," replied Colonel Marcus. "Intelligence reports suggest organized resistance in at least three systems. They're calling themselves 'The Liberty Front'."

The Emperor's expression remained unchanged, but his eyes narrowed slightly. "Liberty," he mused. "Always a dangerous word in the wrong mouths."

"Shall I arrange a meeting with the Security Council, sir?"

"No," the Emperor replied after a moment. "Send for General Octavius. This requires a more... Roman solution."

---

*Posted by General_Octavius - May 16, 2024*

General Octavius arrived at the Imperial Palace precisely at the appointed hour. The summons from the Emperor himself had been unexpected, but not unwelcome. As the commander of the elite 7th Legion, Octavius had earned a reputation for solving problems that others couldn't - or wouldn't.

After being escorted through security, Octavius was led to the Emperor's private study rather than the formal throne room. This would be a conversation, not a command performance.

"Your Excellency," Octavius said, bowing deeply as he entered.

Emperor Stratus gestured to a chair. "Sit, General. We have matters of state to discuss."

As Octavius took his seat, the Emperor activated a holographic display showing the Western Reaches. Several systems glowed red, indicating areas of unrest.

"The situation is deteriorating," the Emperor said matter-of-factly. "The Senate debates while rebellion spreads. I require someone who understands that fire must sometimes be fought with fire."

Octavius studied the map carefully. "The 7th Legion stands ready, Your Excellency. What are your orders?"

"When the old Roman Empire faced rebellion, they didn't merely suppress it - they made examples that would discourage others for generations to come." The Emperor's voice was calm, but carried the weight of absolute authority. "I need you to remind these systems why the Pax Imperium is preferable to the chaos of resistance."

Octavius nodded slowly. "As the Romans did. I understand, Your Excellency."

"You have full operational discretion, General. But understand this - I need order restored quickly and permanently. The Galaxy is watching."

"It will be done, Your Excellency." Octavius stood and bowed again. "The 7th Legion departs within 24 hours."

---

*Posted by Senator_Valerian - May 18, 2024*

The Senate chamber was in an uproar. Senator Livia Valerian of Alderaan stood at her podium, her voice rising above the tumult.

"Colleagues, I have just received word that the 7th Legion has been deployed to the Western Reaches with full operational discretion. This action was taken without Senate approval or oversight!"

Shouts and murmurs filled the vast chamber. The Imperial Senate, while maintaining the appearance of the old Republic's democratic traditions, had seen its power gradually diminished over three decades of Emperor Stratus's rule.

"Point of order!" called out Senator Drusus Vex of Kuat, a known Imperial loyalist. "The Emperor has constitutional authority to deploy military assets in response to insurrection without prior Senate approval."

"That authority," Valerian countered, "was meant for immediate threats to Imperial security. The unrest in the Western Reaches, while concerning, hardly qualifies as—"

"The definition of 'immediate threat' is not for you to decide, Senator," interrupted Grand Moff Tiberius, who had entered the chamber unannounced. As the Emperor's direct representative to the Senate, his presence immediately quieted the room.

"The Emperor has determined that swift action is necessary," Tiberius continued smoothly. "The Senate will be kept informed of developments as appropriate. In the meantime, perhaps this body could focus its energies on the agricultural relief bill for the Outer Rim, which has been stalled for weeks?"

Valerian's face flushed with anger, but she recognized the political maneuvering for what it was - a clear message that the deployment was not up for debate.

"This isn't over," she said quietly, taking her seat.

In the shadows of the observation gallery, a hooded figure watched the proceedings with interest before slipping away unnoticed.
"""

def setup_demo_environment():
    """Set up the demo environment with a sample scenario"""
    logger.info("Setting up demo environment...")
    
    # Create directories
    os.makedirs(DEMO_SCENARIO_DIR, exist_ok=True)
    
    # Create sample scenario file
    scenario_path = os.path.join(DEMO_SCENARIO_DIR, "Like_Unto_the_Romans.md")
    with open(scenario_path, 'w', encoding='utf-8') as f:
        f.write(SAMPLE_SCENARIO)
    
    logger.info(f"Created sample scenario at {scenario_path}")
    return scenario_path

def cleanup_demo_environment(full_cleanup=False):
    """Clean up the demo environment"""
    if full_cleanup:
        logger.info("Cleaning up demo environment (full cleanup)...")
        if os.path.exists(SCENARIOS_DIR):
            shutil.rmtree(SCENARIOS_DIR)
    else:
        logger.info("Cleaning up demo environment (partial cleanup)...")
        # Only remove analysis files
        for suffix in ["_characters.md", "_timeline.md", "_analysis.md", "_development.md"]:
            pattern = os.path.join(DEMO_SCENARIO_DIR, f"*{suffix}")
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    logger.info(f"Removed {file_path}")
                except:
                    pass

def run_process_demo(scenario_path, modules):
    """Run the processing demo"""
    logger.info("Running scenario processing demo...")
    
    # Import the processor module
    try:
        processor_module = importlib.import_module('scenario_processor')
    except ImportError as e:
        logger.error(f"Failed to import scenario_processor: {e}")
        return False
    
    try:
        # Get the directory containing the scenario file
        scenario_dir = os.path.dirname(scenario_path)
        
        # Create a content.md file for the ScenarioProcessor (it expects this structure)
        content_file = os.path.join(scenario_dir, "content.md")
        if not os.path.exists(content_file):
            # Copy scenario content to content.md
            with open(scenario_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Use the ScenarioProcessor class
        processor = processor_module.ScenarioProcessor(scenario_dir)
        result = processor.process_scenario()
        
        if result:
            logger.info("Sample scenario processed successfully")
            if isinstance(result, dict):
                for key, value in result.items():
                    if value and isinstance(value, str) and os.path.exists(value):
                        logger.info(f"  - {key}: {value}")
        else:
            logger.warning("Scenario processing returned no result")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during demo processing: {e}")
        return False

def run_index_demo(modules):
    """Run the indexing demo"""
    logger.info("Running scenario indexing demo...")
    
    # Import the indexer module
    try:
        indexer = importlib.import_module('scenario_indexer')
    except ImportError as e:
        logger.error(f"Failed to import scenario_indexer: {e}")
        return False
    
    try:
        # Build the index
        df = indexer.build_scenario_index(SCENARIOS_DIR)
        
        # Generate JSON data
        json_path = indexer.generate_json_data(df)
        
        # Generate Excel index
        excel_path = indexer.generate_excel_index(df)
        
        # Generate timeline report
        timeline_path = indexer.generate_timeline_report(df)
        
        # Generate HTML dashboard
        dashboard_path = indexer.generate_html_dashboard()
        
        logger.info("Demo indexing complete:")
        for path in [json_path, excel_path, timeline_path, dashboard_path]:
            if path and os.path.exists(path):
                logger.info(f"  - Created: {path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error during demo indexing: {e}")
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EOTIR Scenario Manager Demo")
    parser.add_argument("--cleanup", action="store_true", help="Clean up demo files after running")
    parser.add_argument("--full-cleanup", action="store_true", help="Remove all scenario files")
    args = parser.parse_args()
    
    try:
        import importlib
        
        # Set up demo environment
        scenario_path = setup_demo_environment()
        
        # Run processing demo
        run_process_demo(scenario_path, None)
        
        # Run indexing demo
        run_index_demo(None)
        
        # Open dashboard if available
        dashboard_path = os.path.join(SCENARIOS_DIR, "Indexes", "dashboard.html")
        if os.path.exists(dashboard_path):
            logger.info(f"Dashboard available at: {os.path.abspath(dashboard_path)}")
            
            # Try to open in browser
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(dashboard_path)}")
                logger.info("Opened dashboard in browser")
            except Exception as e:
                logger.warning(f"Could not open dashboard in browser: {e}")
        
        # Clean up if requested
        if args.full_cleanup:
            cleanup_demo_environment(full_cleanup=True)
        elif args.cleanup:
            cleanup_demo_environment()
        
        logger.info("Demo completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Error running demo: {e}")
        return 1

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Starting EOTIR Scenario Manager Demo at {start_time}")
    
    exit_code = main()
    
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    logger.info(f"Demo completed at {end_time}")
    logger.info(f"Total execution time: {elapsed_time}")
    
    sys.exit(exit_code)
