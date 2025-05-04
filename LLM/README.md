# EOTIR LLM Training Dataset

This directory contains scripts and data for preparing the EOTIR RPG and Novel content for training a custom Large Language Model (LLM). The project extracts, processes, and organizes text from various file formats into categorized training data.

## Directory Structure

```
LLM/
├── character_profiles/         # Character descriptions and profiles
├── in_game_documents/
│   ├── laws_policies/          # Legal documents, charters, regulations
│   ├── intelligence/           # Intelligence reports, briefings
│   ├── technical/              # Technical specifications, manuals
│   └── diplomatic/             # Treaties, agreements, diplomatic content
├── narratives/
│   ├── completed_scenarios/    # Finished storylines and scenarios
│   └── unfinished_scenarios/   # Partial or draft narratives
├── ooc_content/
│   ├── rules/                  # Out-of-character rules and guidelines
│   ├── admin/                  # Administrative documents
│   └── templates/              # Forms and templates
├── worldbuilding/              # Setting information, timelines, lore
├── unknown/                    # Files that couldn't be categorized
├── metadata/
│   ├── training_examples/      # JSONL files with prompt-completion pairs
│   └── reports/                # Analysis and statistics
├── extract_llm_data.py         # Script to extract and categorize data
├── dataset_stats.py            # Script to analyze the processed data
├── test_llm_dir.py             # Script to test directory structure
└── requirements.txt            # Python dependencies
```

## Training Examples

The `metadata/training_examples/` directory contains example prompt-completion pairs in JSONL format for various types of content the model should generate:

- **Character Profiles**: Creating detailed character backgrounds and profiles
- **Document Generation**: Generating in-universe documents like reports and technical specifications
- **Scenario Continuation**: Continuing a narrative from a given prompt
- **Timeline Integration**: Creating timeline entries for historical events

These examples serve as templates for fine-tuning the model with specific tasks relevant to the EOTIR universe.

## Data Extraction

The `extract_llm_data.py` script processes files from the EOTIR RPG and Novels directories, extracts their text content, and categorizes them based on filename patterns and content analysis.

### Usage:

```bash
# Process the novels directory
python extract_llm_data.py --novels

# Process the RPG directories
python extract_llm_data.py --rpg

# Process all directories
python extract_llm_data.py --all

# Specify a custom output directory
python extract_llm_data.py --all --output custom_dir
```

The script supports extracting text from various file formats:
- Text files (.txt, .md, .rtf)
- Word documents (.doc, .docx)
- PDF files (.pdf)

## Dataset Statistics

The `dataset_stats.py` script analyzes the processed data and generates visualizations and reports.

### Usage:

```bash
# Generate statistics for the dataset
python dataset_stats.py

# Specify a custom dataset directory
python dataset_stats.py --dir path/to/dataset

# Specify a custom output directory for reports
python dataset_stats.py --output path/to/output
```

The script generates:
- Distribution charts (file counts, word counts, average words per file)
- Word count histogram
- Document type analysis
- Summary report in Markdown format
- JSON statistics for programmatic use

## Directory Testing

The `test_llm_dir.py` script verifies that the LLM directory has the correct structure and contains the necessary example files.

### Usage:

```bash
# Test the directory structure
python test_llm_dir.py
```

## Requirements

To run the scripts, install the required dependencies:

```bash
pip install -r requirements.txt
```

Key dependencies:
- pathlib
- argparse
- matplotlib
- docx2txt or python-docx (for Word documents)
- PyPDF2 (for PDF files)

## Workflow for LLM Training

1. **Extract data**: Run `extract_llm_data.py` to process source files
2. **Analyze dataset**: Use `dataset_stats.py` to understand the dataset composition
3. **Prepare for training**: Determine appropriate training parameters based on the dataset statistics
4. **Train model**: Use the extracted data along with the training examples to fine-tune your LLM

## Notes

- Large files (>10MB) are skipped during extraction
- Some specialized formats may require additional libraries
- For text-only training, further preprocessing may be necessary to normalize formats
