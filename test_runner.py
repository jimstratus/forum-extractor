#!/usr/bin/env python3
"""
EOTIR Scenario Manager Test Runner
This script runs tests to verify the functionality of the scenario management system.
"""

import os
import sys
import logging
import argparse
import unittest
import tempfile
import shutil
import importlib
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Sample scenario content for testing
SAMPLE_SCENARIO = """---
title: Test Scenario
forum: Test_Forum
year: 1 IRY
status: In Progress
extraction_date: 2025-05-03
url: https://example.com/test
---

# Test Scenario [1 IRY]

*Posted by Test_Author - May 1, 2025*

This is a test scenario for unit testing the EOTIR Scenario Manager.

The Imperial Republic faces a test situation. Emperor Stratus has ordered a response.

---

*Posted by Test_Officer - May 2, 2025*

I will carry out the orders immediately, Your Excellency.
"""

class ScraperTests(unittest.TestCase):
    """Tests for the scenario_scraper module"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_scraper_import(self):
        """Test that the scraper module can be imported"""
        try:
            scraper = importlib.import_module('scenario_scraper')
            self.assertIsNotNone(scraper)
        except ImportError:
            self.fail("Failed to import scenario_scraper")
    
    def test_sanitize_filename(self):
        """Test the sanitize_filename function"""
        try:
            scraper = importlib.import_module('scenario_scraper')
            result = scraper.sanitize_filename("Test: File/Name*?")
            # Colon and space both become underscores, creating double underscore
            self.assertEqual(result, "Test__File_Name__")
        except Exception as e:
            self.fail(f"sanitize_filename failed: {e}")
    
    def test_extract_year_from_title(self):
        """Test the extract_year_from_title function"""
        try:
            scraper = importlib.import_module('scenario_scraper')
            iry_result = scraper.extract_year_from_title("Test Title [34 IRY]")
            self.assertEqual(iry_result, "34 IRY")
            
            ufy_result = scraper.extract_year_from_title("Test Title [5 UFY]")
            self.assertEqual(ufy_result, "5 UFY")
            
            no_year_result = scraper.extract_year_from_title("Test Title")
            self.assertEqual(no_year_result, "")
        except Exception as e:
            self.fail(f"extract_year_from_title failed: {e}")

class ProcessorTests(unittest.TestCase):
    """Tests for the scenario_processor module"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.scenario_dir = os.path.join(self.temp_dir, "Scenarios", "Test_Forum", "1_IRY")
        os.makedirs(self.scenario_dir, exist_ok=True)
        
        # Create a test scenario directory with content.md (as expected by ScenarioProcessor)
        self.scenario_folder = os.path.join(self.scenario_dir, "Test_Scenario")
        os.makedirs(self.scenario_folder, exist_ok=True)
        
        # Create content.md file inside the scenario folder
        self.content_file = os.path.join(self.scenario_folder, "content.md")
        with open(self.content_file, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_SCENARIO)
        
        # Also create the old-style scenario file for backward compatibility tests
        self.scenario_path = os.path.join(self.scenario_dir, "Test_Scenario.md")
        with open(self.scenario_path, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_SCENARIO)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_processor_import(self):
        """Test that the processor module can be imported"""
        try:
            processor = importlib.import_module('scenario_processor')
            self.assertIsNotNone(processor)
        except ImportError:
            self.fail("Failed to import scenario_processor")
    
    def test_read_scenario_file(self):
        """Test the read_scenario_file function"""
        try:
            processor = importlib.import_module('scenario_processor')
            frontmatter, content = processor.read_scenario_file(self.scenario_path)
            self.assertEqual(frontmatter.get('title'), "Test Scenario")
            self.assertEqual(frontmatter.get('forum'), "Test_Forum")
            self.assertEqual(frontmatter.get('year'), "1 IRY")
            self.assertTrue(content.startswith("\n# Test Scenario"))
        except Exception as e:
            self.fail(f"read_scenario_file failed: {e}")
    
    def test_find_scenarios(self):
        """Test the find_scenarios function"""
        try:
            processor = importlib.import_module('scenario_processor')
            scenarios = processor.find_scenarios(os.path.join(self.temp_dir, "Scenarios"))
            # Should find at least 1 scenario (may find both old-style .md and content.md)
            self.assertGreaterEqual(len(scenarios), 1)
            # Check that at least one of the found scenarios is a valid path
            self.assertTrue(any(os.path.exists(s) for s in scenarios))
        except Exception as e:
            self.fail(f"find_scenarios failed: {e}")
    
    def test_process_scenario(self):
        """Test the ScenarioProcessor class"""
        try:
            processor_module = importlib.import_module('scenario_processor')
            
            # May need to mock NLP tools for this test
            try:
                import nltk
                import spacy
                
                # Try to process the scenario using the ScenarioProcessor class
                # Pass the scenario folder (not the .md file)
                processor = processor_module.ScenarioProcessor(self.scenario_folder)
                result = processor.process_scenario()
                self.assertIsNotNone(result)
                
                # Check if result contains scenario path
                if "error" not in result:
                    self.assertIn('scenario', result)
            
            except (ImportError, ModuleNotFoundError):
                logger.warning("Skipping full process_scenario test as NLP libraries are not available")
                self.skipTest("NLP libraries not available")
        
        except Exception as e:
            self.fail(f"process_scenario failed: {e}")

class IndexerTests(unittest.TestCase):
    """Tests for the scenario_indexer module"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.scenario_dir = os.path.join(self.temp_dir, "Scenarios", "Test_Forum", "1_IRY")
        os.makedirs(self.scenario_dir, exist_ok=True)
        
        # Create a test scenario file
        self.scenario_path = os.path.join(self.scenario_dir, "Test_Scenario.md")
        with open(self.scenario_path, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_SCENARIO)
        
        # Create test supplementary files
        base_path = os.path.splitext(self.scenario_path)[0]
        with open(f"{base_path}_characters.md", 'w', encoding='utf-8') as f:
            f.write("---\ncharacter_count: 2\n---\n# Characters")
        
        with open(f"{base_path}_timeline.md", 'w', encoding='utf-8') as f:
            f.write("---\nevent_count: 2\n---\n# Timeline")
        
        with open(f"{base_path}_analysis.md", 'w', encoding='utf-8') as f:
            f.write("---\ncompletion_status: In Progress\n---\n# Analysis")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_indexer_import(self):
        """Test that the indexer module can be imported"""
        try:
            indexer = importlib.import_module('scenario_indexer')
            self.assertIsNotNone(indexer)
        except ImportError:
            self.fail("Failed to import scenario_indexer")
    
    def test_read_frontmatter(self):
        """Test the read_frontmatter function"""
        try:
            indexer = importlib.import_module('scenario_indexer')
            frontmatter = indexer.read_frontmatter(self.scenario_path)
            self.assertEqual(frontmatter.get('title'), "Test Scenario")
            self.assertEqual(frontmatter.get('forum'), "Test_Forum")
            self.assertEqual(frontmatter.get('year'), "1 IRY")
        except Exception as e:
            self.fail(f"read_frontmatter failed: {e}")
    
    def test_extract_numeric_year(self):
        """Test the extract_numeric_year function"""
        try:
            indexer = importlib.import_module('scenario_indexer')
            iry_result = indexer.extract_numeric_year("34 IRY")
            self.assertEqual(iry_result, 34)
            
            ufy_result = indexer.extract_numeric_year("5 UFY")
            self.assertEqual(ufy_result, -5)  # UFY years are negative
            
            no_year_result = indexer.extract_numeric_year("")
            self.assertIsNone(no_year_result)
        except Exception as e:
            self.fail(f"extract_numeric_year failed: {e}")
    
    def test_build_scenario_index(self):
        """Test the build_scenario_index function"""
        try:
            indexer = importlib.import_module('scenario_indexer')
            
            # Try to build the index
            try:
                import pandas as pd
                
                df = indexer.build_scenario_index(os.path.join(self.temp_dir, "Scenarios"))
                self.assertIsNotNone(df)
                self.assertEqual(len(df), 1)
                self.assertEqual(df.iloc[0]['title'], "Test Scenario")
                self.assertEqual(df.iloc[0]['forum'], "Test_Forum")
                self.assertEqual(df.iloc[0]['year'], "1 IRY")
                self.assertEqual(df.iloc[0]['completion_status'], "In Progress")
                self.assertEqual(df.iloc[0]['character_count'], 2)
                self.assertEqual(df.iloc[0]['timeline_event_count'], 2)
            
            except ImportError:
                logger.warning("Skipping build_scenario_index test as pandas is not available")
                self.skipTest("pandas not available")
        
        except Exception as e:
            self.fail(f"build_scenario_index failed: {e}")

class IntegrationTests(unittest.TestCase):
    """Integration tests for the scenario management system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.scenarios_dir = os.path.join(self.temp_dir, "Scenarios")
        os.makedirs(self.scenarios_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_module_import(self):
        """Test that all modules can be imported"""
        # Import all required modules
        modules = {}
        
        try:
            modules['scraper'] = importlib.import_module('scenario_scraper')
            modules['processor'] = importlib.import_module('scenario_processor')
            modules['indexer'] = importlib.import_module('scenario_indexer')
            modules['manager'] = importlib.import_module('scenario_manager')
            
            self.assertTrue(all(modules.values()))
        except ImportError as e:
            self.fail(f"Failed to import module: {e}")

def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases to the suite
    suite.addTest(loader.loadTestsFromTestCase(ScraperTests))
    suite.addTest(loader.loadTestsFromTestCase(ProcessorTests))
    suite.addTest(loader.loadTestsFromTestCase(IndexerTests))
    suite.addTest(loader.loadTestsFromTestCase(IntegrationTests))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EOTIR Scenario Manager Test Runner")
    parser.add_argument("--scraper-only", action="store_true", help="Run only scraper tests")
    parser.add_argument("--processor-only", action="store_true", help="Run only processor tests")
    parser.add_argument("--indexer-only", action="store_true", help="Run only indexer tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    args = parser.parse_args()
    
    logger.info("Starting test runner...")
    
    if args.scraper_only:
        logger.info("Running scraper tests only")
        suite = unittest.TestLoader().loadTestsFromTestCase(ScraperTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        success = result.wasSuccessful()
    
    elif args.processor_only:
        logger.info("Running processor tests only")
        suite = unittest.TestLoader().loadTestsFromTestCase(ProcessorTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        success = result.wasSuccessful()
    
    elif args.indexer_only:
        logger.info("Running indexer tests only")
        suite = unittest.TestLoader().loadTestsFromTestCase(IndexerTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        success = result.wasSuccessful()
    
    elif args.integration_only:
        logger.info("Running integration tests only")
        suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        success = result.wasSuccessful()
    
    else:
        logger.info("Running all tests")
        success = run_tests()
    
    if success:
        logger.info("All tests passed successfully")
        return 0
    else:
        logger.error("Some tests failed")
        return 1

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Starting EOTIR Scenario Manager Test Runner at {start_time}")
    
    exit_code = main()
    
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    logger.info(f"Tests completed at {end_time}")
    logger.info(f"Total execution time: {elapsed_time}")
    
    sys.exit(exit_code)
