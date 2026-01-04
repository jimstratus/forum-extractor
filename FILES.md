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
| `forum_scraper.py` | 🔧 | Added fallback CSS selectors for IPS4 compatibility |
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

## Testing

| File | Status | Notes |
|------|--------|-------|
| `test_runner.py` | 🔧 | Fixed test assertions and skipTest handling |

## Removed Files (Additional)

| File | Status | Reason |
|------|--------|--------|
| `demo.py` | ❌ | Redundant - users can run scripts directly |
| `quick_run.py` | ❌ | Redundant - duplicates forum_scraper functionality |
| `test_extraction.py` | ❌ | Redundant - just calls forum_scraper functions |
| `test_llm_dir.py` | ❌ | Redundant - simple check that could be in extract_llm_data.py |

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
- **Files modified**: 16
- **Files removed**: 17 (duplicates/unnecessary)
- **New files created**: 3 (run_manager.bat, run_manager.sh, FILES.md)

## Testing Results

All major components have been tested and verified working:

| Component | Test | Status |
|-----------|------|--------|
| `forum_scraper.py` | Extract 67 topics from Palace Situation Room | ✅ Pass |
| `forum_scraper.py` | Extract posts from topic pages | ✅ Pass |
| `scenario_indexer.py` | Build index of 36 scenarios | ✅ Pass |
| `scenario_indexer.py` | Generate JSON data | ✅ Pass |
| `scenario_indexer.py` | Generate timeline report | ✅ Pass |
| `generate_combined_report.py` | Generate reports for forum | ✅ Pass |
| `update_scenario_status.py` | List scenarios with status | ✅ Pass |
| `scenario_processor.py` | Process scenario and generate files | ✅ Pass |
| `main.py` | Help and argument parsing | ✅ Pass |
| `scenario_manager.py` | Help and argument parsing | ✅ Pass |
| `scenario_scraper.py` | Help and argument parsing | ✅ Pass |
| `extract_llm_data.py` | Help and argument parsing | ✅ Pass |
| `prepare_llm_dataset.py` | Module execution | ✅ Pass |
| `run_full_extraction.py` | Full pipeline execution | ✅ Pass |
| `inspect_page.py` | Page inspection | ✅ Pass |
| `test_runner.py` | Unit tests (12 tests, 1 skipped) | ✅ Pass |
| `generate_combined_report.py` | Generate reports for forum | ✅ Pass |
| `update_scenario_status.py` | List scenarios with status | ✅ Pass |
| `scenario_processor.py` | Process scenario and generate files | ✅ Pass |

Test URLs verified:
- Forum: https://nexus.eotir.com/forum/6-palace-situation-room/ (67 topics)
- Topic: https://nexus.eotir.com/topic/2431-corruption-and-incorruption-36-iry/ (45+ pages)
- Topic: https://nexus.eotir.com/topic/2157-shadows-rising-31-iry/ (44+ pages)
