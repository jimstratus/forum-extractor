#!/usr/bin/env python3
"""
EOTIR Forum Extractor - Main Entry Point

This module provides the main entry point for the EOTIR Forum Extractor system.
It delegates to the scenario_manager module for coordinating the extraction,
processing, and indexing workflow.
"""

import sys
from scenario_manager import main as run_manager


def main():
    """Main entry point for the EOTIR Forum Extractor."""
    return run_manager()


if __name__ == "__main__":
    sys.exit(main())
