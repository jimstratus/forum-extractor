# Development Guide

This guide covers setting up a local development environment and running the project.

## Prerequisites

- **Python 3.11+** (required)
- **pip** (Python package manager)
- **git** (version control)

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd forum-extractor
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- beautifulsoup4 - HTML parsing
- requests - HTTP requests
- pandas - Data manipulation
- pyyaml - YAML processing
- openpyxl - Excel file generation
- tqdm - Progress bars
- nltk, spacy - NLP processing
- markdownify - HTML to markdown conversion
- python-dateutil - Date handling
- docx2txt - Document text extraction

## Environment Variables

The project uses environment variables for configuration. Create a `.env` file if needed:

```bash
# Optional: Override default settings
FORUM_BASE_URL=https://nexus.eotir.com
RATE_LIMIT_REQUESTS_PER_MINUTE=30
LOG_LEVEL=INFO
```

| Variable | Default | Description |
|----------|---------|-------------|
| `FORUM_BASE_URL` | `https://nexus.eotir.com` | Base URL for EOTIR forums |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `30` | Rate limit for scraping |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Running the Project

### Using the Runner Script (Recommended)

**Linux/macOS:**
```bash
./run_manager.sh run-all
```

**Windows:**
```batch
run_manager.bat run-all
```

### Using Python Directly

```bash
# Run the complete pipeline
python main.py run-all

# Run specific commands
python main.py --help
```

### Individual Scraper Scripts

```bash
# Forum scraper (extracts from all configured forums)
python forum_scraper.py

# Scenario scraper (scenario-specific extraction)
python scenario_scraper.py

# Generate combined reports
python generate_combined_report.py

# Generate combined reports for a specific forum
python generate_combined_report.py --forum Red_Scenario

# Update scenario status
python update_scenario_status.py --list

# Extract data for LLM training
python extract_llm_data.py --base-dir /path/to/data

# Inspect page HTML structure
python inspect_page.py
```

## Testing

### Run Full Test Suite

```bash
python test_runner.py
```

### Run Specific Test Suites

```bash
# Scraping tests only
python test_runner.py --scraper-only

# Processing tests only
python test_runner.py --processor-only

# Indexer tests only
python test_runner.py --indexer-only
```

### Individual Test Scripts

```bash
# Test forum scraper functionality
python test_forum_scraper.py

# Test single topic extraction
python test_single_topic.py
```

## Project Structure

```
forum-extractor/
├── main.py                    # Main entry point
├── scenario_manager.py        # Pipeline coordinator
│
├── # Core Modules
├── forum_scraper.py           # Forum scraping with rate limiting
├── scenario_scraper.py        # Scenario extraction wrapper
├── scenario_processor.py      # NLP processing and analysis
├── scenario_indexer.py        # Index and report generation
│
├── # Utilities
├── generate_combined_report.py
├── update_scenario_status.py
├── inspect_page.py
│
├── # LLM Tools
├── extract_llm_data.py
├── prepare_llm_dataset.py
│
├── # Testing
├── test_runner.py             # Full test suite
├── test_forum_scraper.py
├── test_single_topic.py
│
├── # Scripts
├── run_manager.sh             # Linux/macOS runner
├── run_manager.bat            # Windows runner
│
├── # Generated Output
├── Scenarios/                 # Extracted scenario data
├── Reports/                   # Generated reports
└── LLM/                       # LLM training data
```

## Code Style

When contributing code:

- Follow PEP 8 style guidelines
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Add type hints where beneficial
- Add docstrings for public functions

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed conventions.

## Debugging

### Inspecting Page Structure

Use the inspect_page.py script to examine HTML structure:

```bash
python inspect_page.py
```

### Logging

The project logs to both console and file. Log files are written to the project root.

### Rate Limiting

The scraper includes automatic rate limiting (30 requests/minute by default). To adjust:

```python
# In forum_scraper.py
self.requests_per_minute = 30  # Modify as needed
```
