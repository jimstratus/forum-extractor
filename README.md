# EOTIR Forum Extractor

A comprehensive system for extracting, processing, and analyzing scenarios from the Era of the Imperial Republic (EOTIR) RPG forums. The system organizes extracted content into structured formats and can prepare data for LLM training.

## 🎉 Current Status (January 2026)

**✅ Fully Functional & Production Ready**

- **279 scenarios** extracted from 3 EOTIR forums
- **93 combined reports** generated
- **8 index files** created (Excel, JSON, HTML dashboard, timelines)
- **All critical bugs fixed** (infinite loop, duplicate detection working)
- **Comprehensive documentation** included

### Recent Updates
- Fixed infinite pagination loop with proper duplicate detection
- Added real-time progress visibility during extraction
- Fixed Palace Situation Room forum URL
- Generated complete extraction from all forums (97 topics total)
- Created combined reports for all scenarios

### Quick Stats
- **Blue Scenario**: 23 topics, 110 files
- **Red Scenario**: 7 topics, 30 files  
- **Palace Situation Room**: 67 topics, 325 files
- **Total Output**: 377 markdown files, 93 YAML metadata files

## Quick Start

### Windows
```batch
run_manager.bat run-all
```

### Linux/macOS
```bash
./run_manager.sh run-all
```

### Python Direct
```bash
python main.py run-all
```

## System Overview

The system provides a complete pipeline for:

1. **Extraction** - Scrape scenario data from EOTIR forums (Red Scenario, Palace Situation Room, Blue Scenario)
2. **Processing** - Analyze scenarios to extract characters, timelines, and plot information
3. **Indexing** - Generate searchable indexes, reports, and an HTML dashboard
4. **LLM Preparation** - Prepare extracted data for LLM training datasets

## Directory Structure

```
forum-extractor/
├── main.py                    # Main entry point
├── scenario_manager.py        # Pipeline coordinator
├── run_manager.bat/.sh        # Cross-platform runner scripts
│
├── # Core Modules
├── forum_scraper.py           # Forum scraping with rate limiting
├── scenario_scraper.py        # Scenario extraction wrapper
├── scenario_processor.py      # NLP processing and analysis
├── scenario_indexer.py        # Index and report generation
│
├── # Utilities
├── generate_combined_report.py # Combined report generator
├── update_scenario_status.py   # Scenario status management
├── inspect_page.py             # HTML structure inspector
│
├── # LLM Tools
├── extract_llm_data.py         # Extract data for LLM training
├── prepare_llm_dataset.py      # Prepare character datasets
├── test_llm_dir.py             # Verify LLM directory structure
│
├── # Demo & Testing
├── demo.py                     # Demo with sample scenario
├── quick_run.py                # Quick extraction test
├── test_extraction.py          # Extraction tests
├── test_runner.py              # Full test suite
│
├── # Output Directories (generated)
├── Scenarios/                  # Extracted scenario data
│   ├── Red_Scenario/
│   ├── Palace_Situation_Room/
│   ├── Blue_Scenario/
│   └── Indexes/
├── Reports/                    # Generated reports
└── LLM/                        # LLM training data
```

## Commands

### Scenario Manager (`main.py`)

The main entry point supports multiple commands:

```bash
# Run complete pipeline (extract → process → index)
python main.py run-all

# Extract scenarios from forums
python main.py extract
python main.py extract --forum "https://nexus.eotir.com/forum/59-red-scenario/"

# Process extracted scenarios
python main.py process
python main.py process --scenario path/to/scenario.md

# Generate indexes and reports
python main.py index
python main.py index --no-excel --no-dashboard
```

### Individual Scripts

#### Forum Scraper
```bash
python forum_scraper.py
```
Extracts all scenarios from configured forums with:
- Automatic rate limiting
- Retry logic for failed requests
- Post content extraction and markdown conversion

#### Report Generator
```bash
# All scenarios
python generate_combined_report.py

# Specific forum
python generate_combined_report.py --forum Red_Scenario

# Specific scenario
python generate_combined_report.py --scenario scenario_folder_name
```

#### Status Manager
```bash
# List all scenarios with status
python update_scenario_status.py --list

# Update scenario status
python update_scenario_status.py --forum Red_Scenario --scenario scenario_name --status "Complete"
```

#### LLM Data Extraction
```bash
# Extract data for LLM training (prompts for directory)
python extract_llm_data.py

# With command line argument
python extract_llm_data.py --base-dir /path/to/eotir/data
```

#### Demo Mode
```bash
# Run demo with sample scenario
python demo.py

# Run and cleanup after
python demo.py --cleanup
```

## Output Files

### Scenario Files
Each extracted scenario includes:
- `content.md` - Full scenario content in markdown
- `dramatis_personae.md` - Identified characters
- `timeline.md` - Chronological event timeline
- `plot_development.md` - Suggestions for continuation
- `metadata.yaml` - Scenario metadata (title, year, status, URL)

### Index Files
- `scenario_index.xlsx` - Excel spreadsheet of all scenarios
- `dashboard.html` - Interactive HTML dashboard
- `chronological_timeline.md` - Timeline across all scenarios
- `dashboard_data.json` - JSON data for dashboard

## Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- beautifulsoup4 - HTML parsing
- requests - HTTP requests
- pandas - Data manipulation
- pyyaml - YAML processing
- markdownify - HTML to markdown
- openpyxl - Excel file generation
- tqdm - Progress bars
- nltk, spacy - NLP processing (optional)

## Configuration

### Forum URLs
Edit `forum_scraper.py` to modify target forums:
```python
FORUM_URLS = {
    "Red_Scenario": "/forum/59-red-scenario/",
    "Palace_Situation_Room": "/forum/6-palace-situation-room/",
    "Blue_Scenario": "/forum/69-blue-scenario/"
}
```

### Rate Limiting
The scraper includes automatic rate limiting. Adjust in `forum_scraper.py`:
```python
self.requests_per_minute = 30  # Requests per minute limit
```

## Development

### Running Tests
```bash
# All tests
python test_runner.py

# Specific test suites
python test_runner.py --scraper-only
python test_runner.py --processor-only
python test_runner.py --indexer-only
```

### Project Structure
- Uses `pyproject.toml` for package configuration
- Python 3.11+ required
- Cross-platform support (Windows, Linux, macOS)

## License

This project is for personal use with the EOTIR RPG community.
