# Documentation Index

Categorized documentation for the EOTIR Forum Extractor project.

## Getting Started

- [README.md](../README.md) - Project overview and quick start
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Setup instructions and development guide
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines and code conventions

## Project Documentation

| Document | Description |
|----------|-------------|
| [FILES.md](../FILES.md) | File inventory and review status |
| [CHANGELOG.md](../CHANGELOG.md) | Version history and release notes |

## Core Modules

| Module | Purpose |
|--------|---------|
| `forum_scraper.py` | HTTP fetching, rate limiting, forum parsing |
| `scenario_scraper.py` | Scenario-specific extraction wrapper |
| `scenario_processor.py` | NLP processing and content analysis |
| `scenario_indexer.py` | Index generation and reporting |

## Utilities

| Script | Purpose |
|--------|---------|
| `generate_combined_report.py` | Generate combined scenario reports |
| `update_scenario_status.py` | Manage scenario status |
| `inspect_page.py` | Debug HTML page structure |

## LLM Tools

| Script | Purpose |
|--------|---------|
| `extract_llm_data.py` | Extract data for LLM training |
| `prepare_llm_dataset.py` | Prepare character datasets |

## Testing

| Script | Purpose |
|--------|---------|
| `test_runner.py` | Full test suite |
| `test_forum_scraper.py` | Scraper-specific tests |
| `test_single_topic.py` | Single topic extraction tests |

## Categories

### User Guides
- Quick start: See [README.md](../README.md#quick-start)
- Configuration: See [README.md](../README.md#configuration)
- Commands: See [README.md](../README.md#commands)

### Developer Guides
- Setup: See [DEVELOPMENT.md](./DEVELOPMENT.md#initial-setup)
- Testing: See [DEVELOPMENT.md](./DEVELOPMENT.md#testing)
- Code style: See [CONTRIBUTING.md](./CONTRIBUTING.md#python-code-conventions)

### Reference
- Requirements: See [requirements.txt](../requirements.txt)
- Project structure: See [FILES.md](../FILES.md)
- Changelog: See [CHANGELOG.md](../CHANGELOG.md)
