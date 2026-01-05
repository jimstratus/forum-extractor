# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-01-05

### Major Release - Full Forum Extraction Complete

#### Added
- Complete extraction of 279 scenarios from all 3 EOTIR forums
- Duplicate post detection using ID and content hash tracking
- Real-time progress visibility with page-by-page updates
- 93 combined scenario reports in `Reports/` directory
- Comprehensive indexes (Excel, JSON, HTML dashboard, timelines)
- Test scripts for validation (`test_forum_scraper.py`, `test_single_topic.py`)

#### Fixed
- **CRITICAL**: Infinite pagination loop bug
  - Forum returns "next page" link even on last page
  - Solution: Duplicate detection stops after 2 consecutive duplicate pages
  - Files: `forum_scraper.py` lines 188-336
- Missing 'topic' attribute in scenario_manager arguments
- Incorrect Palace Situation Room forum URL (changed from /forum/6- to /forum/169-)
- Unicode arrow symbols in console logging (cosmetic fix)

#### Changed
- Enhanced logging to output to both console and file
- Progress indicators show every 10 pages during extraction
- Improved error handling and reporting

#### Data Quality
- All content.md files verified (no broken extractions)
- Supplementary files (dramatis_personae, timeline, plot_development) working as designed
- Metadata files complete for all scenarios

### Commits
- `6857f94` - Fix infinite loop with proper duplicate detection
- `55334b8` - Fix missing topic attribute  
- `0a8bdb4` - Add progress logging and fix Palace URL
- `4e02c28` - Fix argument passing bugs
- `6693f8a` - Add complete forum extraction data and generated reports

## [1.0.0] - Initial Release

### Added
- Basic forum scraping functionality
- Scenario processing and indexing
- Report generation
- LLM data preparation tools
