# Contributing to EOTIR Forum Extractor

Thank you for your interest in contributing to this project. Please follow these guidelines to maintain code quality and consistency.

## Python Code Conventions

### General Style

- Follow PEP 8 style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Add type hints where beneficial

### Dependencies

This project uses these core libraries:

- **beautifulsoup4** (bs4) - HTML/XML parsing
  ```python
  from bs4 import BeautifulSoup
  soup = BeautifulSoup(html_content, 'html.parser')
  ```

- **requests** - HTTP requests
  ```python
  response = requests.get(url, timeout=30)
  response.raise_for_status()
  ```

- **pandas** - Data manipulation
  ```python
  import pandas as pd
  df = pd.DataFrame(data)
  ```

### Code Structure

```
forum-extractor/
├── # Core pipeline modules
├── forum_scraper.py           # HTTP fetching, rate limiting, parsing
├── scenario_scraper.py        # Scenario-specific extraction
├── scenario_processor.py      # NLP analysis, content processing
├── scenario_indexer.py        # Index generation, reporting
├── scenario_manager.py        # Pipeline orchestration
│
├── # Utility scripts
├── generate_combined_report.py
├── update_scenario_status.py
├── inspect_page.py
│
├── # LLM preparation tools
├── extract_llm_data.py
├── prepare_llm_dataset.py
│
└── # Testing
    └── test_runner.py
```

### Function Guidelines

- Keep functions focused and small (ideally < 50 lines)
- Use descriptive function names: `extract_posts()`, `build_scenario_index()`
- Add docstrings for public functions
- Handle exceptions gracefully with specific error messages

### HTML Parsing Conventions

When using BeautifulSoup:

```python
# Preferred: use specific CSS selectors
content = soup.select('div.post-content')[0].get_text(strip=True)

# Avoid: overly broad selectors
content = soup.find('div').get_text()  # Too broad
```

## Commit Message Format

Use conventional commits with scopes:

```
<type>(<scope>): <description>

[optional body]
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

### Scopes

Use these scopes based on the component being modified:

| Scope | Description | Example Components |
|-------|-------------|---------------------|
| `scraper` | Forum/topic scraping | `forum_scraper.py`, `scenario_scraper.py` |
| `processor` | Content processing/NLP | `scenario_processor.py` |
| `indexer` | Index/report generation | `scenario_indexer.py`, `generate_combined_report.py` |
| `llm` | LLM training data tools | `extract_llm_data.py`, `prepare_llm_dataset.py` |
| `manager` | Pipeline coordination | `scenario_manager.py`, `main.py` |
| `utils` | Utility scripts | `update_scenario_status.py`, `inspect_page.py` |
| `docs` | Documentation only | README, CONTRIBUTING, etc. |

### Examples

```
feat(scraper): add retry logic for failed requests
fix(processor): handle missing timeline data gracefully
docs(readme): add quick start section
refactor(indexer): improve Excel generation performance
test(llm): add dataset validation tests
chore: update requirements versions
```

## Pull Request Guidelines

1. Create a feature branch from `main`
2. Test changes before submitting
3. Update documentation if needed
4. Keep commits atomic and focused

## Testing

Run the test suite before submitting:

```bash
python test_runner.py
```

Run specific test suites:

```bash
python test_runner.py --scraper-only
python test_runner.py --processor-only
python test_runner.py --indexer-only
```
