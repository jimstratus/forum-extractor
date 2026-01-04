# File Index and Review Status

This document tracks all files in the repository and their review/cleanup status.

## Legend
- ✅ Reviewed and cleaned up
- 🔧 Reviewed and modified
- 📝 Reviewed, no changes needed
- ❌ Removed (duplicate/unnecessary)

---

## Root Configuration Files

| File | Status | Notes |
|------|--------|-------|
| `.gitignore` | 🔧 | Added log files, generated files, replit files |
| `pyproject.toml` | 🔧 | Fixed project name, added dependencies |
| `requirements.txt` | 📝 | Complete, no changes needed |
| `README.md` | 🔧 | Complete rewrite with comprehensive documentation |

## Removed Files

| File | Status | Reason |
|------|--------|--------|
| `.replit` | ❌ | Replit-specific, not needed |
| `generated-icon.png` | ❌ | Replit-generated icon |
| `uv.lock` | ❌ | Had wrong project name, can be regenerated |
| `eotir_manager.py` | ❌ | Duplicate of scenario_manager.py |
| `run_eotir_manager.bat` | ❌ | Replaced with run_manager.bat |
| `run_eotir_manager.sh` | ❌ | Replaced with run_manager.sh |
| `forum_extraction.py` | ❌ | Duplicate of forum_scraper.py |
| `local_profile_extractor.py` | ❌ | Duplicate of extract_llm_data.py |
| `extraction_requirements.txt` | ❌ | Consolidated into requirements.txt |
| `README_QUICK_RUN.md` | ❌ | Generated placeholder file |
| `page_sample.html` | ❌ | Generated debug output |
| `scenario_index.csv` | ❌ | Generated output file |
| `*_log.txt` files | ❌ | Log files should not be committed |

## Main Entry Points

| File | Status | Notes |
|------|--------|-------|
| `main.py` | 🔧 | Was empty, now delegates to scenario_manager |
| `run_manager.bat` | ✅ | New Windows runner script |
| `run_manager.sh` | ✅ | New Linux/macOS runner script |
| `run_full_extraction.py` | 🔧 | Removed placeholders, now uses actual modules |

## Core Modules

| File | Status | Notes |
|------|--------|-------|
| `scenario_manager.py` | 📝 | Pipeline coordinator, no changes needed |
| `forum_scraper.py` | 📝 | Main scraper with ForumScraper class |
| `scenario_scraper.py` | 🔧 | Updated to integrate with forum_scraper |
| `scenario_processor.py` | 🔧 | Removed duplicate imports |
| `scenario_indexer.py` | 🔧 | Fixed syntax warning (raw string for HTML) |

## Utility Scripts

| File | Status | Notes |
|------|--------|-------|
| `generate_combined_report.py` | 📝 | No changes needed |
| `update_scenario_status.py` | 📝 | No changes needed |
| `inspect_page.py` | 🔧 | Fixed to write sample to temp directory |

## LLM Tools

| File | Status | Notes |
|------|--------|-------|
| `extract_llm_data.py` | 🔧 | Added directory prompt (--base-dir) |
| `prepare_llm_dataset.py` | 📝 | Character dataset preparation |
| `test_llm_dir.py` | 🔧 | Added directory prompt (--base-dir) |

## Demo & Testing

| File | Status | Notes |
|------|--------|-------|
| `demo.py` | 🔧 | Fixed to use ScenarioProcessor class |
| `quick_run.py` | 📝 | Quick extraction test (embedded script ok) |
| `test_extraction.py` | 📝 | Forum scraper test |
| `test_runner.py` | 🔧 | Fixed test setup for ScenarioProcessor |

## Generated Data Directories

These directories contain extracted/generated data:

| Directory | Contents |
|-----------|----------|
| `Scenarios/` | Extracted scenario data organized by forum |
| `Scenarios/Indexes/` | Index files, dashboard, timeline |
| `Reports/` | Generated combined reports |

---

## Summary

- **Total files reviewed**: 22 source files
- **Files modified**: 14
- **Files removed**: 13 (duplicates/unnecessary)
- **New files created**: 2 (run_manager.bat, run_manager.sh)
