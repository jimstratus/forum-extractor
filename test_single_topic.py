#!/usr/bin/env python3
"""
Test single topic extraction to verify bug fix
"""
import sys
sys.path.insert(0, '.')
from scenario_scraper import extract_single_topic

# Test with a small topic 
# "Red Scenario Rules" - should have only 2 posts
print("Testing single topic extraction...")
print("Topic: Red Scenario Rules (should have ~2 posts)")
print("-" * 60)

success = extract_single_topic(
    "https://nexus.eotir.com/topic/168-red-scenario-rules/",
    None
)

if success:
    print("\n" + "=" * 60)
    print("✓ Test PASSED - Extraction completed successfully")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("✗ Test FAILED - Extraction encountered errors")
    print("=" * 60)
