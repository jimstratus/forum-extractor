#!/bin/bash
# EOTIR Scenario Manager - Shell Script
# This script runs the scenario manager with the provided arguments

echo "EOTIR Scenario Manager"
echo "====================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11 or later"
    exit 1
fi

# Run the scenario manager with all arguments passed to this script
python3 main.py "$@"

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "Scenario manager completed with errors."
else
    echo ""
    echo "Scenario manager completed successfully."
fi

exit $exit_code
