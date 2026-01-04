#!/usr/bin/env python3
"""
EOTIR Scenario Indexer
This script generates indexes and reports for the processed scenarios.
"""

import os
import sys
import re
import logging
import argparse
import yaml
import json
from datetime import datetime
import glob
import pandas as pd
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scenario_indexing_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base directories
SCENARIOS_DIR = os.path.join("Scenarios")
INDEXES_DIR = os.path.join(SCENARIOS_DIR, "Indexes")

def read_frontmatter(file_path):
    """Read YAML frontmatter from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            try:
                frontmatter = yaml.safe_load(frontmatter_text)
                return frontmatter
            except Exception as e:
                logger.error(f"Error parsing frontmatter in {file_path}: {e}")
        else:
            logger.warning(f"No frontmatter found in {file_path}")
        
        return {}
    
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return {}

def extract_numeric_year(year_str):
    """Extract numeric year value from year string (e.g., '34 IRY' -> 34)"""
    if not year_str:
        return None
    
    match = re.search(r'(\d+)\s*(?:IRY|UFY)', year_str, re.IGNORECASE)
    if match:
        value = int(match.group(1))
        # UFY years are negative (count backwards)
        if 'UFY' in year_str.upper():
            value = -value
        return value
    
    return None

def suggest_year(title, content):
    """Suggest a year from title or content if not explicitly given"""
    # First check the title
    title_match = re.search(r'\[(\d+)\s*(?:IRY|UFY)\]', title, re.IGNORECASE)
    if title_match:
        year_type = "IRY" if "IRY" in title_match.group(0).upper() else "UFY"
        return f"{title_match.group(1)} {year_type}"
    
    # Then check the content
    content_match = re.search(r'\b(\d+)\s*(?:IRY|UFY)\b', content, re.IGNORECASE)
    if content_match:
        year_type = "IRY" if "IRY" in content_match.group(0).upper() else "UFY"
        return f"{content_match.group(1)} {year_type}"
    
    return ""

def get_file_content(file_path):
    """Get file content without frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
        if frontmatter_match:
            # Return content after frontmatter
            return content[frontmatter_match.end():]
        
        return content
    
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def count_entities(file_path, entity_type):
    """Count entities (characters or timeline events) from a file"""
    if not os.path.isfile(file_path):
        return 0
    
    frontmatter = read_frontmatter(file_path)
    
    if entity_type == "character":
        return frontmatter.get("character_count", 0)
    elif entity_type == "event":
        return frontmatter.get("event_count", 0)
    
    return 0

def build_scenario_index(scenarios_dir):
    """Build a comprehensive index of all scenario files"""
    logger.info("Building scenario index...")
    
    # Find all scenario files (not including supplementary files)
    search_pattern = os.path.join(scenarios_dir, "**", "*.md")
    all_files = glob.glob(search_pattern, recursive=True)
    scenario_files = [f for f in all_files if not any(f.endswith(suffix) for suffix in 
                      ["_characters.md", "_timeline.md", "_analysis.md", "_development.md"])]
    
    # Exclude files in the Indexes directory
    scenario_files = [f for f in scenario_files if "Indexes" not in f]
    
    logger.info(f"Found {len(scenario_files)} scenario files to index")
    
    # Collect data for each scenario
    scenarios_data = []
    
    for file_path in scenario_files:
        try:
            # Read frontmatter
            frontmatter = read_frontmatter(file_path)
            
            # Get title
            title = frontmatter.get("title", os.path.basename(file_path).replace(".md", ""))
            
            # Get forum type
            forum = frontmatter.get("forum", "Unknown")
            
            # Get year
            year = frontmatter.get("year", "")
            
            # If year not specified, try to extract from title or content
            year_suggestion = ""
            if not year:
                content = get_file_content(file_path)
                year_suggestion = suggest_year(title, content)
            
            # Get numeric year value
            numeric_year = extract_numeric_year(year or year_suggestion)
            
            # Get status
            status = frontmatter.get("status", "Unknown")
            
            # Get extraction date
            extraction_date = frontmatter.get("extraction_date", "")
            
            # Get URL
            url = frontmatter.get("url", "")
            
            # Check for supplementary files
            base_path = os.path.splitext(file_path)[0]
            characters_path = f"{base_path}_characters.md"
            timeline_path = f"{base_path}_timeline.md"
            analysis_path = f"{base_path}_analysis.md"
            development_path = f"{base_path}_development.md"
            
            has_characters = os.path.isfile(characters_path)
            has_timeline = os.path.isfile(timeline_path)
            has_analysis = os.path.isfile(analysis_path)
            has_development = os.path.isfile(development_path)
            
            # Get character count
            character_count = count_entities(characters_path, "character")
            
            # Get timeline event count
            timeline_event_count = count_entities(timeline_path, "event")
            
            # Get completion status from analysis
            completion_status = "Unknown"
            if has_analysis:
                analysis_frontmatter = read_frontmatter(analysis_path)
                completion_status = analysis_frontmatter.get("completion_status", "Unknown")
            
            # Add to list
            scenarios_data.append({
                "title": title,
                "forum": forum,
                "year": year,
                "year_suggestion": year_suggestion,
                "numeric_year": numeric_year,
                "status": status,
                "completion_status": completion_status,
                "character_count": character_count,
                "timeline_event_count": timeline_event_count,
                "extraction_date": extraction_date,
                "url": url,
                "path": file_path,
                "has_characters": has_characters,
                "has_timeline": has_timeline,
                "has_analysis": has_analysis,
                "has_development": has_development,
                "characters_path": characters_path if has_characters else "",
                "timeline_path": timeline_path if has_timeline else "",
                "analysis_path": analysis_path if has_analysis else "",
                "development_path": development_path if has_development else ""
            })
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(scenarios_data)
    
    # Sort by forum and title
    if not df.empty:
        df = df.sort_values(by=["forum", "title"])
    
    logger.info(f"Built index with {len(df)} scenarios")
    return df

def generate_excel_index(df):
    """Generate Excel index from the DataFrame"""
    logger.info("Generating Excel index...")
    
    # Create output directory if it doesn't exist
    os.makedirs(INDEXES_DIR, exist_ok=True)
    
    excel_path = os.path.join(INDEXES_DIR, "scenario_index.xlsx")
    
    # Create Excel writer
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Write main sheet
            df.to_excel(writer, sheet_name="All Scenarios", index=False)
            
            # Create forum-specific sheets
            forums = df['forum'].unique()
            for forum in forums:
                if forum != "Unknown":
                    forum_df = df[df['forum'] == forum]
                    forum_df.to_excel(writer, sheet_name=forum, index=False)
            
            # Create completion status sheet
            status_df = df.sort_values(by=["completion_status", "forum", "title"])
            status_df.to_excel(writer, sheet_name="By Completion Status", index=False)
            
            # Create year sheet
            if 'numeric_year' in df.columns and not df['numeric_year'].isna().all():
                year_df = df.sort_values(by=["numeric_year", "forum", "title"])
                year_df.to_excel(writer, sheet_name="By Year", index=False)
        
        logger.info(f"Excel index saved to {excel_path}")
        return excel_path
    
    except Exception as e:
        logger.error(f"Error generating Excel index: {e}")
        return None

def generate_json_data(df):
    """Generate JSON data file for the dashboard"""
    logger.info("Generating JSON data for dashboard...")
    
    # Create output directory if it doesn't exist
    os.makedirs(INDEXES_DIR, exist_ok=True)
    
    json_path = os.path.join(INDEXES_DIR, "dashboard_data.json")
    
    try:
        # Create data structure for JSON
        data = {
            "generated_date": datetime.now().isoformat(),
            "total_scenarios": len(df),
            "scenarios_by_forum": df.groupby('forum').size().to_dict(),
            "scenarios_by_status": df.groupby('completion_status').size().to_dict(),
            "forums": {},
            "years": {},
            "scenarios": df.to_dict('records')
        }
        
        # Group by forum
        for forum in df['forum'].unique():
            forum_df = df[df['forum'] == forum]
            data["forums"][forum] = forum_df.to_dict('records')
        
        # Group by year
        for year in df['year'].unique():
            if year:  # Skip empty years
                year_df = df[df['year'] == year]
                data["years"][year] = year_df.to_dict('records')
        
        # Write JSON file with custom encoder for dates
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"JSON data saved to {json_path}")
        return json_path
    
    except Exception as e:
        logger.error(f"Error generating JSON data: {e}")
        return None

def generate_timeline_report(df):
    """Generate a markdown report of scenarios in chronological order"""
    logger.info("Generating chronological timeline report...")
    
    # Create output directory if it doesn't exist
    os.makedirs(INDEXES_DIR, exist_ok=True)
    
    timeline_path = os.path.join(INDEXES_DIR, "chronological_timeline.md")
    
    try:
        # Create a filtered DataFrame with valid years
        year_df = df[df['year'].notna() & (df['year'] != "")]
        
        # If we have no years, try using year suggestions
        if len(year_df) == 0 and not df['year_suggestion'].isna().all():
            year_df = df[df['year_suggestion'].notna() & (df['year_suggestion'] != "")]
            year_df = year_df.copy()
            year_df['year'] = year_df['year_suggestion']
        
        # If still empty, just use the original DataFrame
        if len(year_df) == 0:
            year_df = df
        
        # Sort by numeric year, then title
        if 'numeric_year' in year_df.columns and not year_df['numeric_year'].isna().all():
            year_df = year_df.sort_values(by=['numeric_year', 'title'])
        
        # Group by year
        year_groups = {}
        for _, row in year_df.iterrows():
            year = row.get('year', 'Unknown Year')
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(row)
        
        # Write the timeline report
        with open(timeline_path, 'w', encoding='utf-8') as f:
            f.write("# EOTIR Chronological Timeline\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Split into IRY and UFY
            iry_years = [y for y in year_groups.keys() if 'IRY' in y.upper()]
            ufy_years = [y for y in year_groups.keys() if 'UFY' in y.upper()]
            other_years = [y for y in year_groups.keys() if 'IRY' not in y.upper() and 'UFY' not in y.upper()]
            
            # Sort years
            iry_years.sort(key=lambda y: extract_numeric_year(y) or 0)
            ufy_years.sort(key=lambda y: extract_numeric_year(y) or 0, reverse=True)  # UFY counts backwards
            
            # Write UFY section (earlier in timeline)
            if ufy_years:
                f.write("## United Factions Years (UFY)\n\n")
                for year in ufy_years:
                    f.write(f"### {year}\n\n")
                    for row in year_groups[year]:
                        forum = row.get('forum', 'Unknown')
                        title = row.get('title', 'Untitled')
                        completion = row.get('completion_status', 'Unknown')
                        url = row.get('url', '')
                        path = row.get('path', '')
                        chars = row.get('character_count', 0)
                        events = row.get('timeline_event_count', 0)
                        
                        f.write(f"- **{title}** ({forum}) - {completion}\n")
                        if url:
                            f.write(f"  - URL: {url}\n")
                        f.write(f"  - Characters: {chars}, Timeline Events: {events}\n")
                        f.write(f"  - Path: {path}\n")
                        f.write("\n")
            
            # Write IRY section
            if iry_years:
                f.write("## Imperial Republic Years (IRY)\n\n")
                for year in iry_years:
                    f.write(f"### {year}\n\n")
                    for row in year_groups[year]:
                        forum = row.get('forum', 'Unknown')
                        title = row.get('title', 'Untitled')
                        completion = row.get('completion_status', 'Unknown')
                        url = row.get('url', '')
                        path = row.get('path', '')
                        chars = row.get('character_count', 0)
                        events = row.get('timeline_event_count', 0)
                        
                        f.write(f"- **{title}** ({forum}) - {completion}\n")
                        if url:
                            f.write(f"  - URL: {url}\n")
                        f.write(f"  - Characters: {chars}, Timeline Events: {events}\n")
                        f.write(f"  - Path: {path}\n")
                        f.write("\n")
            
            # Write Other section for unknown years
            if other_years:
                f.write("## Undated Scenarios\n\n")
                for year in other_years:
                    if year != "Unknown Year":
                        f.write(f"### {year}\n\n")
                    for row in year_groups[year]:
                        forum = row.get('forum', 'Unknown')
                        title = row.get('title', 'Untitled')
                        completion = row.get('completion_status', 'Unknown')
                        url = row.get('url', '')
                        path = row.get('path', '')
                        
                        f.write(f"- **{title}** ({forum}) - {completion}\n")
                        if url:
                            f.write(f"  - URL: {url}\n")
                        f.write(f"  - Path: {path}\n")
                        f.write("\n")
        
        logger.info(f"Timeline report saved to {timeline_path}")
        return timeline_path
    
    except Exception as e:
        logger.error(f"Error generating timeline report: {e}")
        return None

def generate_html_dashboard():
    """Generate HTML dashboard to view scenarios"""
    logger.info("Generating HTML dashboard...")
    
    # Create output directory if it doesn't exist
    os.makedirs(INDEXES_DIR, exist_ok=True)
    
    dashboard_path = os.path.join(INDEXES_DIR, "dashboard.html")
    json_path = os.path.join(INDEXES_DIR, "dashboard_data.json")
    
    if not os.path.isfile(json_path):
        logger.error(f"JSON data file not found: {json_path}")
        return None
    
    # Create the dashboard HTML (use raw string to avoid escape sequence warnings)
    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EOTIR Scenario Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #1a1a2e;
            color: white;
            padding: 10px 20px;
            text-align: center;
        }
        h1, h2, h3 {
            margin-top: 20px;
        }
        .filters {
            background-color: #fff;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .scenario-list {
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .scenario-card {
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            background-color: #fafafa;
        }
        .scenario-title {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        .scenario-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .tag {
            display: inline-block;
            background-color: #e0e0e0;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        .tag.complete {
            background-color: #c8e6c9;
            color: #388e3c;
        }
        .tag.partial {
            background-color: #fff9c4;
            color: #ffa000;
        }
        .tag.incomplete {
            background-color: #ffcdd2;
            color: #d32f2f;
        }
        .tag.red {
            background-color: #ffcdd2;
            color: #d32f2f;
        }
        .tag.palace {
            background-color: #bbdefb;
            color: #1976d2;
        }
        .tag.blue {
            background-color: #c8e6c9;
            color: #388e3c;
        }
        .scenario-links {
            margin-top: 10px;
        }
        .scenario-links a {
            display: inline-block;
            margin-right: 10px;
            text-decoration: none;
            color: #1976d2;
        }
        .scenario-links a:hover {
            text-decoration: underline;
        }
        .statistics {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            flex: 1;
            background-color: #fff;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            min-width: 200px;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        select, input {
            padding: 8px;
            margin-right: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            padding: 8px 15px;
            background-color: #1a1a2e;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #16213e;
        }
        .hidden {
            display: none;
        }
        .pagination {
            margin-top: 20px;
            text-align: center;
        }
        .pagination button {
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <header>
        <h1>EOTIR Scenario Dashboard</h1>
    </header>
    
    <div class="container">
        <div class="statistics" id="stats-container">
            <!-- Statistics will be inserted here -->
        </div>
        
        <div class="filters">
            <h2>Filters</h2>
            <div style="margin-bottom: 10px;">
                <select id="forum-filter">
                    <option value="all">All Forums</option>
                    <!-- Forum options will be inserted here -->
                </select>
                
                <select id="year-filter">
                    <option value="all">All Years</option>
                    <!-- Year options will be inserted here -->
                </select>
                
                <select id="status-filter">
                    <option value="all">All Statuses</option>
                    <!-- Status options will be inserted here -->
                </select>
            </div>
            
            <div>
                <input type="text" id="search-input" placeholder="Search by title or content...">
                <button id="search-button">Search</button>
                <button id="reset-filters">Reset Filters</button>
            </div>
        </div>
        
        <div class="scenario-list" id="scenario-container">
            <!-- Scenarios will be inserted here -->
        </div>
        
        <div class="pagination" id="pagination">
            <!-- Pagination controls will be inserted here -->
        </div>
    </div>
    
    <script>
        // Global variables
        let scenarioData;
        let filteredScenarios = [];
        const scenariosPerPage = 10;
        let currentPage = 1;
        
        // Fetch the JSON data
        fetch('dashboard_data.json')
            .then(response => response.json())
            .then(data => {
                scenarioData = data;
                initializeDashboard();
            })
            .catch(error => {
                console.error('Error loading dashboard data:', error);
                document.getElementById('scenario-container').innerHTML = 
                    '<p>Error loading data. Please check that dashboard_data.json exists in the same directory.</p>';
            });
        
        function initializeDashboard() {
            // Initialize all scenarios
            filteredScenarios = [...scenarioData.scenarios];
            
            // Populate statistics
            updateStatistics();
            
            // Populate forum filter
            const forumFilter = document.getElementById('forum-filter');
            const forums = Object.keys(scenarioData.forums);
            forums.forEach(forum => {
                const option = document.createElement('option');
                option.value = forum;
                option.textContent = forum.replace('_', ' ');
                forumFilter.appendChild(option);
            });
            
            // Populate year filter
            const yearFilter = document.getElementById('year-filter');
            const years = Object.keys(scenarioData.years);
            years.sort((a, b) => {
                // Custom sort for IRY and UFY years
                const aMatch = a.match(/(\d+)\s*(IRY|UFY)/i);
                const bMatch = b.match(/(\d+)\s*(IRY|UFY)/i);
                
                if (aMatch && bMatch) {
                    const aType = aMatch[2].toUpperCase();
                    const bType = bMatch[2].toUpperCase();
                    
                    if (aType === bType) {
                        const aYear = parseInt(aMatch[1]);
                        const bYear = parseInt(bMatch[1]);
                        return aType === 'UFY' ? bYear - aYear : aYear - bYear;
                    }
                    
                    return aType === 'UFY' ? -1 : 1; // UFY before IRY
                }
                
                return a.localeCompare(b);
            });
            
            years.forEach(year => {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                yearFilter.appendChild(option);
            });
            
            // Populate status filter
            const statusFilter = document.getElementById('status-filter');
            const statuses = [...new Set(scenarioData.scenarios.map(s => s.completion_status))];
            statuses.forEach(status => {
                if (status) {
                    const option = document.createElement('option');
                    option.value = status;
                    option.textContent = status;
                    statusFilter.appendChild(option);
                }
            });
            
            // Set up event listeners
            document.getElementById('forum-filter').addEventListener('change', applyFilters);
            document.getElementById('year-filter').addEventListener('change', applyFilters);
            document.getElementById('status-filter').addEventListener('change', applyFilters);
            document.getElementById('search-button').addEventListener('click', applyFilters);
            document.getElementById('search-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    applyFilters();
                }
            });
            document.getElementById('reset-filters').addEventListener('click', resetFilters);
            
            // Initial display
            displayScenarios();
        }
        
        function updateStatistics() {
            const statsContainer = document.getElementById('stats-container');
            
            // Total scenarios
            const totalStat = document.createElement('div');
            totalStat.className = 'stat-card';
            totalStat.innerHTML = `
                <h3>Total Scenarios</h3>
                <div class="stat-number">${scenarioData.total_scenarios}</div>
            `;
            
            // Scenarios by forum
            const forumStats = document.createElement('div');
            forumStats.className = 'stat-card';
            forumStats.innerHTML = `<h3>By Forum</h3>`;
            
            Object.entries(scenarioData.scenarios_by_forum).forEach(([forum, count]) => {
                forumStats.innerHTML += `<div>${forum.replace('_', ' ')}: ${count}</div>`;
            });
            
            // Scenarios by status
            const statusStats = document.createElement('div');
            statusStats.className = 'stat-card';
            statusStats.innerHTML = `<h3>By Status</h3>`;
            
            Object.entries(scenarioData.scenarios_by_status).forEach(([status, count]) => {
                statusStats.innerHTML += `<div>${status}: ${count}</div>`;
            });
            
            // Filtered count
            const filteredStat = document.createElement('div');
            filteredStat.className = 'stat-card';
            filteredStat.id = 'filtered-count';
            filteredStat.innerHTML = `
                <h3>Filtered Results</h3>
                <div class="stat-number">${filteredScenarios.length}</div>
            `;
            
            statsContainer.innerHTML = '';
            statsContainer.appendChild(totalStat);
            statsContainer.appendChild(forumStats);
            statsContainer.appendChild(statusStats);
            statsContainer.appendChild(filteredStat);
        }
        
        function applyFilters() {
            const forumValue = document.getElementById('forum-filter').value;
            const yearValue = document.getElementById('year-filter').value;
            const statusValue = document.getElementById('status-filter').value;
            const searchValue = document.getElementById('search-input').value.toLowerCase();
            
            filteredScenarios = scenarioData.scenarios.filter(scenario => {
                // Apply forum filter
                if (forumValue !== 'all' && scenario.forum !== forumValue) {
                    return false;
                }
                
                // Apply year filter
                if (yearValue !== 'all' && scenario.year !== yearValue) {
                    return false;
                }
                
                // Apply status filter
                if (statusValue !== 'all' && scenario.completion_status !== statusValue) {
                    return false;
                }
                
                // Apply search filter
                if (searchValue && !scenario.title.toLowerCase().includes(searchValue)) {
                    return false;
                }
                
                return true;
            });
            
            currentPage = 1;
            displayScenarios();
            updateStatistics();
        }
        
        function resetFilters() {
            document.getElementById('forum-filter').value = 'all';
            document.getElementById('year-filter').value = 'all';
            document.getElementById('status-filter').value = 'all';
            document.getElementById('search-input').value = '';
            
            filteredScenarios = [...scenarioData.scenarios];
            currentPage = 1;
            displayScenarios();
            updateStatistics();
        }
        
        function displayScenarios() {
            const container = document.getElementById('scenario-container');
            container.innerHTML = '';
            
            if (filteredScenarios.length === 0) {
                container.innerHTML = '<p>No scenarios match the current filters.</p>';
                document.getElementById('pagination').innerHTML = '';
                return;
            }
            
            // Calculate pagination
            const totalPages = Math.ceil(filteredScenarios.length / scenariosPerPage);
            const startIndex = (currentPage - 1) * scenariosPerPage;
            const endIndex = Math.min(startIndex + scenariosPerPage, filteredScenarios.length);
            
            // Display scenarios for current page
            for (let i = startIndex; i < endIndex; i++) {
                const scenario = filteredScenarios[i];
                const card = createScenarioCard(scenario);
                container.appendChild(card);
            }
            
            // Update pagination controls
            updatePagination(totalPages);
        }
        
        function createScenarioCard(scenario) {
            const card = document.createElement('div');
            card.className = 'scenario-card';
            
            // Create status tag class
            let statusClass = 'incomplete';
            if (scenario.completion_status === 'Complete') {
                statusClass = 'complete';
            } else if (scenario.completion_status === 'Partially Complete') {
                statusClass = 'partial';
            }
            
            // Create forum tag class
            let forumClass = '';
            if (scenario.forum === 'Red_Scenario') {
                forumClass = 'red';
            } else if (scenario.forum === 'Palace_Situation_Room') {
                forumClass = 'palace';
            } else if (scenario.forum === 'Blue_Scenario') {
                forumClass = 'blue';
            }
            
            card.innerHTML = `
                <div class="scenario-title">${scenario.title}</div>
                <div class="scenario-meta">
                    <span class="tag ${forumClass}">${scenario.forum.replace('_', ' ')}</span>
                    <span class="tag ${statusClass}">${scenario.completion_status}</span>
                    ${scenario.year ? `<span class="tag">${scenario.year}</span>` : ''}
                    ${scenario.character_count ? `<span class="tag">Characters: ${scenario.character_count}</span>` : ''}
                    ${scenario.timeline_event_count ? `<span class="tag">Events: ${scenario.timeline_event_count}</span>` : ''}
                </div>
                <div class="scenario-meta">
                    <span>Source: ${scenario.url ? `<a href="${scenario.url}" target="_blank">Forum Link</a>` : 'Not available'}</span>
                </div>
                <div class="scenario-links">
                    <a href="${scenario.path}" target="_blank">View Scenario</a>
                    ${scenario.characters_path ? `<a href="${scenario.characters_path}" target="_blank">Characters</a>` : ''}
                    ${scenario.timeline_path ? `<a href="${scenario.timeline_path}" target="_blank">Timeline</a>` : ''}
                    ${scenario.analysis_path ? `<a href="${scenario.analysis_path}" target="_blank">Analysis</a>` : ''}
                    ${scenario.development_path ? `<a href="${scenario.development_path}" target="_blank">Development</a>` : ''}
                </div>
            `;
            
            return card;
        }
        
        function updatePagination(totalPages) {
            const pagination = document.getElementById('pagination');
            pagination.innerHTML = '';
            
            if (totalPages <= 1) {
                return;
            }
            
            // Previous button
            const prevButton = document.createElement('button');
            prevButton.textContent = 'Previous';
            prevButton.disabled = currentPage === 1;
            prevButton.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    displayScenarios();
                }
            });
            pagination.appendChild(prevButton);
            
            // Page numbers
            const pageInfo = document.createElement('span');
            pageInfo.textContent = ` Page ${currentPage} of ${totalPages} `;
            pagination.appendChild(pageInfo);
            
            // Next button
            const nextButton = document.createElement('button');
            nextButton.textContent = 'Next';
            nextButton.disabled = currentPage === totalPages;
            nextButton.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    currentPage++;
                    displayScenarios();
                }
            });
            pagination.appendChild(nextButton);
        }
    </script>
</body>
</html>"""
    
    try:
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"HTML dashboard saved to {dashboard_path}")
        return dashboard_path
    
    except Exception as e:
        logger.error(f"Error generating HTML dashboard: {e}")
        return None

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EOTIR Scenario Indexer - Generate indexes and reports for scenarios")
    parser.add_argument("--no-excel", action="store_true", help="Skip generating Excel index")
    parser.add_argument("--no-dashboard", action="store_true", help="Skip generating HTML dashboard")
    parser.add_argument("--no-timeline", action="store_true", help="Skip generating timeline report")
    args = parser.parse_args()
    
    # Build the scenario index
    df = build_scenario_index(SCENARIOS_DIR)
    
    if df is None or len(df) == 0:
        logger.error("No scenarios found to index")
        return
    
    # Generate JSON data
    json_path = generate_json_data(df)
    
    # Generate Excel index
    if not args.no_excel:
        excel_path = generate_excel_index(df)
    
    # Generate timeline report
    if not args.no_timeline:
        timeline_path = generate_timeline_report(df)
    
    # Generate HTML dashboard
    if not args.no_dashboard:
        dashboard_path = generate_html_dashboard()
    
    logger.info("Indexing complete")

if __name__ == "__main__":
    main()
