#!/bin/bash

echo "EOTIR Manager Runner"
echo "==================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.6 or higher"
    echo
    read -p "Press Enter to continue..."
    exit 1
fi

# List components if no arguments are provided
if [ $# -eq 0 ]; then
    echo "Available options:"
    echo "  list        - List all available components"
    echo "  all         - Run all components in sequence"
    echo "  scenarios   - Process scenarios only"
    echo "  scraper     - Run scenario scraper only" 
    echo "  indexer     - Run scenario indexer only"
    echo "  llm         - Run LLM data extraction only"
    echo "  report      - Generate combined report only"
    echo
    echo "Example: $(basename "$0") scenarios"
    echo
    python3 eotir_manager.py --list
    read -p "Press Enter to continue..."
    exit 0
fi

# Run the selected component
if [ "$1" = "list" ]; then
    python3 eotir_manager.py --list
elif [ "$1" = "all" ]; then
    echo "Running all components in sequence..."
    python3 eotir_manager.py --all "${@:2}"
else
    echo "Running $1 component..."
    python3 eotir_manager.py --component "$1" --args "${@:2}"
fi

echo
if [ $? -ne 0 ]; then
    echo "Component execution failed. See logs for details."
else
    echo "Component executed successfully!"
fi

read -p "Press Enter to continue..."
