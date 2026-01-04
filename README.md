# EOTIR Scenario Extraction System

This system extracts scenarios from the Era of the Imperial Republic RPG forums, organizes them into a structured format, and generates comprehensive reports for easy review and analysis.

## System Overview

The system consists of several Python scripts designed to:

1. Extract scenario data from the EOTIR forums (Red Scenario, Palace Situation Room, and Blue Scenario)
2. Process and organize the data into structured files
3. Generate indices and combined reports
4. Prepare the scenarios for LLM training and further editing

## Directory Structure

After running the extraction, the following structure will be created:

```
Scenarios/
├── Red_Scenario/
│   ├── [Scenario_1]/
│   │   ├── content.md           # Full content of the scenario
│   │   ├── dramatis_personae.md # Identified characters
│   │   ├── timeline.md          # Timeline of events
│   │   ├── plot_development.md  # Suggestions for continuing/completing
│   │   └── metadata.yaml        # Metadata including year, status, etc.
│   ├── [Scenario_2]/
│   └── ...
├── Palace_Situation_Room/
│   └── ...
├── Blue_Scenario/
│   └── ...
└── Indexes/
    ├── Red_Scenario_index.md
    ├── Palace_Situation_Room_index.md
    ├── Blue_Scenario_index.md
    └── combined_index.md

Reports/
├── Red_Scenario/
│   ├── [Scenario_1]_report.md
│   └── ...
├── Palace_Situation_Room/
└── Blue_Scenario/
```

## Scripts and Usage

### 1. Run Full Extraction (`run_full_extraction.py`)

A single script to run the entire extraction process from start to finish.

```
python run_full_extraction.py
```

This runs all the necessary steps to extract scenarios, create indexes, and generate reports.

### 2. Forum Scraper (`forum_scraper.py`)

The main script that extracts scenario data from the EOTIR forums.

```
python forum_scraper.py
```

This will extract all scenarios from all configured forums. The process includes:
- Creating directories for each forum and scenario
- Extracting posts and metadata
- Identifying characters, creating timelines, and suggesting plot developments
- Generating index files

### 3. Test Extraction (`test_extraction.py`)

A helper script to test the extraction on a single forum or scenario.

```
python test_extraction.py
```

### 4. Generate Combined Reports (`generate_combined_report.py`)

Creates comprehensive markdown reports for each scenario by combining all the extracted data.

```
# Generate reports for all scenarios
python generate_combined_report.py

# Generate reports for a specific forum
python generate_combined_report.py --forum Red_Scenario

# Generate a report for a specific scenario
python generate_combined_report.py --scenario scenario_folder_name
```

### 5. Update Scenario Status (`update_scenario_status.py`)

A tool to manage the status of scenarios (New, In Progress, Complete).

```
# List all scenarios with their current status
python update_scenario_status.py --list

# Update the status of a specific scenario
python update_scenario_status.py --forum Red_Scenario --scenario scenario_name --status "In Progress"
```

### 6. Inspect Page (`inspect_page.py`)

A utility to inspect the HTML structure of a forum page. Useful for debugging or adjusting the extraction selectors.

```
python inspect_page.py "https://nexus.eotir.com/topic/URL_TO_INSPECT"
```

## Extracted Data Fields

### Scenario Content (`content.md`)
- Full content of all posts in the scenario
- Includes author information and timestamps
- Formatted in Markdown for easy reading

### Characters (`dramatis_personae.md`)
- Automatically identified character names from the scenario text
- May require manual review and enhancement

### Timeline (`timeline.md`)
- Chronological list of posts with summaries
- Helps track the progression of the scenario

### Plot Development (`plot_development.md`)
- Current state of the scenario
- Suggestions for continuing or completing unfinished storylines
- Place for notes about open questions and potential directions

### Metadata (`metadata.yaml`)
- Title, author, year, and URL of the scenario
- Status indicator (New, In Progress, Complete)
- Post count and extraction timestamp

## Working with the Data

### Reviewing Scenarios
1. Start with the index files in the `Scenarios/Indexes/` directory to get an overview of all scenarios
2. For each scenario, review the combined report in the `Reports/` directory
3. Update the status field in the metadata.yaml file if needed

### Continuing Unfinished Scenarios
1. Review the plot_development.md file for suggestions
2. Refer to the dramatis_personae.md to ensure character consistency
3. Use the timeline.md to understand the chronology of events

### Preparing for LLM Training
The extracted data is already in a format suitable for LLM training:
- Clean, structured text in Markdown format
- Separated metadata and content
- Character and timeline information for context

## Customization

You can modify the extraction process by editing:

1. `forum_scraper.py` - Adjust CSS selectors, regex patterns, or add new extraction logic
2. `generate_combined_report.py` - Change the report format or add new sections

## Requirements

Required Python packages:
- requests
- beautifulsoup4
- pyyaml
- markdownify

Install with: `pip install -r requirements.txt`
