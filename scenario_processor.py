#!/usr/bin/env python3
"""
EOTIR Scenario Processor
This script processes scenario files to extract characters, create timelines, 
analyze completion status, and suggest plot developments.
PLACEHOLDER FILE - This would contain the actual implementation for NLP processing.
"""

import os
import sys
import logging
import argparse
import re
import yaml
import glob
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("processor_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Base directories
SCENARIOS_DIR = os.path.join("Scenarios")

def read_scenario_file(file_path):
    """Read a scenario file and extract frontmatter and content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    frontmatter_match = re.match(r'---\n(.*?)\n---\n', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        try:
            frontmatter = {}
            for line in frontmatter_text.split('\n'):
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    frontmatter[key.strip()] = value.strip()
            
            # Return content after frontmatter
            remainder = content[frontmatter_match.end():]
            return frontmatter, remainder
        except Exception as e:
            logger.error(f"Error parsing frontmatter in {file_path}: {e}")
    
    # If no frontmatter, return empty dict and full content
    return {}, content

def find_scenarios(scenarios_dir, scenario_file=None, forum=None, year=None):
    """Find scenario files based on criteria"""
    # If specific scenario file is provided, only process that one
    if scenario_file and os.path.isfile(scenario_file):
        return [scenario_file]
    
    # Search pattern base
    pattern_base = os.path.join(scenarios_dir, "**", "*.md")
    
    # Filter by forum
    if forum:
        pattern_base = os.path.join(scenarios_dir, forum, "**", "*.md")
    
    # Filter by year
    if year:
        year_dir = year.replace(" ", "_")
        pattern_base = os.path.join(scenarios_dir, "*", year_dir, "*.md")
    
    # Combine forum and year filters
    if forum and year:
        year_dir = year.replace(" ", "_")
        pattern_base = os.path.join(scenarios_dir, forum, year_dir, "*.md")
    
    # Find all scenario files
    all_files = glob.glob(pattern_base, recursive=True)
    
    # Exclude supplementary files
    scenario_files = [f for f in all_files if not any(f.endswith(suffix) for suffix in 
                     ["_characters.md", "_timeline.md", "_analysis.md", "_development.md"])]
    
    return scenario_files

def extract_characters(scenario_content):
    """
    Extract characters from scenario content

    NOTE: This is a placeholder. The actual implementation would:
    1. Use NLP to identify named entities (PERSON)
    2. Track character mentions and interactions
    3. Extract character descriptions and roles
    4. Organize characters by importance
    """
    # Simple regex-based extraction for the placeholder
    # This would be replaced with actual NLP processing
    character_matches = re.finditer(r'\*(Posted by ([^-]+))', scenario_content)
    characters = []
    
    for match in character_matches:
        character_name = match.group(2).strip()
        if character_name not in characters:
            characters.append(character_name)
    
    # Add some placeholder characters based on common titles/roles in text
    for title in ["Emperor", "General", "Senator", "Colonel", "Grand Moff"]:
        if title in scenario_content:
            name_match = re.search(f"{title} ([A-Z][a-z]+)", scenario_content)
            if name_match and f"{title} {name_match.group(1)}" not in characters:
                characters.append(f"{title} {name_match.group(1)}")
    
    return characters

def extract_timeline(scenario_content):
    """
    Extract a timeline of events from scenario content

    NOTE: This is a placeholder. The actual implementation would:
    1. Use NLP to identify temporal expressions
    2. Extract events and associate them with dates/times
    3. Order events chronologically
    4. Identify causal relationships between events
    """
    # Simple post-based timeline for the placeholder
    # This would be replaced with actual NLP processing
    posts = re.split(r'\n---\n', scenario_content)
    events = []
    
    for i, post in enumerate(posts):
        post = post.strip()
        if not post:
            continue
        
        # Extract date from post header
        date_match = re.search(r'\*Posted by [^-]+ - ([^*]+)\*', post)
        date = date_match.group(1).strip() if date_match else f"Post {i+1}"
        
        # Extract first paragraph as summary
        lines = post.split('\n')
        content_lines = [line for line in lines if not line.startswith('*Posted by')]
        summary = content_lines[0] if content_lines else "Empty post"
        if len(summary) > 100:
            summary = summary[:97] + "..."
        
        events.append({
            "date": date,
            "summary": summary,
            "post_index": i
        })
    
    return events

def analyze_completion(scenario_content, timeline):
    """
    Analyze the completion status of a scenario

    NOTE: This is a placeholder. The actual implementation would:
    1. Use NLP to identify narrative arcs and plotlines
    2. Detect unresolved conflicts and open questions
    3. Evaluate character arcs for completion
    4. Assess overall narrative closure
    """
    # Simple heuristic for the placeholder
    # This would be replaced with actual NLP processing
    
    # Count posts as a simple metric
    post_count = len(timeline)
    
    # Look for conclusion indicators
    conclusion_indicators = [
        "conclude", "concluded", "conclusion", 
        "end", "ended", "finale",
        "resolve", "resolved", "resolution"
    ]
    
    has_conclusion = False
    for indicator in conclusion_indicators:
        if indicator in scenario_content.lower():
            has_conclusion = True
            break
    
    # Determine completion status
    if post_count >= 10 and has_conclusion:
        completion_status = "Complete"
    elif post_count >= 5:
        completion_status = "Partially Complete"
    elif post_count >= 3:
        completion_status = "In Progress"
    else:
        completion_status = "Incomplete"
    
    # Identify unfinished plotlines (placeholder)
    unfinished_plotlines = []
    if "rebellion" in scenario_content.lower() and "quell" not in scenario_content.lower():
        unfinished_plotlines.append("Rebellion plotline")
    
    if "senate" in scenario_content.lower() and "vote" not in scenario_content.lower():
        unfinished_plotlines.append("Senate deliberation plotline")
    
    if "mission" in scenario_content.lower() and "complete" not in scenario_content.lower():
        unfinished_plotlines.append("Mission plotline")
    
    return {
        "completion_status": completion_status,
        "post_count": post_count,
        "has_conclusion": has_conclusion,
        "unfinished_plotlines": unfinished_plotlines
    }

def suggest_development(scenario_content, characters, timeline, analysis):
    """
    Suggest plot developments for continuing the scenario

    NOTE: This is a placeholder. The actual implementation would:
    1. Use NLP to identify narrative patterns and arcs
    2. Generate suggestions based on genre conventions
    3. Offer character development opportunities
    4. Provide options for resolving open plotlines
    """
    # Simple suggestions for the placeholder
    # This would be replaced with actual NLP and potentially LLM processing
    
    suggestions = []
    
    # Based on completion status
    if analysis["completion_status"] == "Complete":
        suggestions.append({
            "type": "continuation",
            "title": "Sequel Potential",
            "description": "While this scenario appears complete, consider a sequel that explores the aftermath of these events."
        })
    elif analysis["completion_status"] == "Partially Complete":
        suggestions.append({
            "type": "completion",
            "title": "Narrative Closure",
            "description": "The scenario has developed significantly but lacks definitive resolution. Consider adding 1-3 more posts that provide closure for the main story threads."
        })
    elif analysis["completion_status"] == "In Progress":
        suggestions.append({
            "type": "development",
            "title": "Midpoint Escalation",
            "description": "The scenario is developing well. Consider introducing a complication or twist that raises the stakes and drives the narrative forward."
        })
    else:  # Incomplete
        suggestions.append({
            "type": "revival",
            "title": "Revival Strategy",
            "description": "This scenario has potential but was abandoned early. Consider a time skip or new perspective to reinvigorate interest."
        })
    
    # Based on unfinished plotlines
    for plotline in analysis["unfinished_plotlines"]:
        suggestions.append({
            "type": "plotline",
            "title": f"Resolve: {plotline}",
            "description": f"Develop a resolution for the {plotline.lower()} that satisfies the narrative setup."
        })
    
    # Character-based suggestions
    if characters:
        suggestion_character = characters[0]  # Use first character as example
        suggestions.append({
            "type": "character",
            "title": f"Character Development: {suggestion_character}",
            "description": f"Deepen {suggestion_character}'s involvement by exploring their motivations or introducing a personal challenge."
        })
    
    # Generic suggestions
    if "conflict" not in scenario_content.lower():
        suggestions.append({
            "type": "conflict",
            "title": "Enhance Conflict",
            "description": "Introduce or escalate a central conflict to drive the narrative forward and increase reader engagement."
        })
    
    if "imperial" in scenario_content.lower() and "rebel" in scenario_content.lower():
        suggestions.append({
            "type": "faction",
            "title": "Faction Intrigue",
            "description": "Develop the Imperial-Rebel dynamic with political intrigue, spies, or unexpected alliances."
        })
    
    return suggestions

def generate_characters_file(scenario_path, characters):
    """Generate a characters file for a scenario"""
    base_path = os.path.splitext(scenario_path)[0]
    characters_path = f"{base_path}_characters.md"
    
    with open(characters_path, 'w', encoding='utf-8') as f:
        # Add frontmatter
        f.write("---\n")
        f.write(f"character_count: {len(characters)}\n")
        f.write(f"generated_date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("---\n\n")
        
        # Add title
        scenario_name = os.path.basename(base_path)
        f.write(f"# Characters in {scenario_name}\n\n")
        
        # Add character list
        for i, character in enumerate(characters, 1):
            f.write(f"## {i}. {character}\n\n")
            f.write(f"*Character analysis would go here in the actual implementation*\n\n")
            f.write("- **Role**: Unknown\n")
            f.write("- **Affiliation**: Unknown\n")
            f.write("- **Motivation**: Unknown\n")
            f.write("- **Character Arc**: Not analyzed\n\n")
    
    logger.info(f"Generated characters file: {characters_path}")
    return characters_path

def generate_timeline_file(scenario_path, timeline):
    """Generate a timeline file for a scenario"""
    base_path = os.path.splitext(scenario_path)[0]
    timeline_path = f"{base_path}_timeline.md"
    
    with open(timeline_path, 'w', encoding='utf-8') as f:
        # Add frontmatter
        f.write("---\n")
        f.write(f"event_count: {len(timeline)}\n")
        f.write(f"generated_date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("---\n\n")
        
        # Add title
        scenario_name = os.path.basename(base_path)
        f.write(f"# Timeline for {scenario_name}\n\n")
        
        # Add timeline
        for i, event in enumerate(timeline, 1):
            f.write(f"## {i}. {event['date']}\n\n")
            f.write(f"{event['summary']}\n\n")
    
    logger.info(f"Generated timeline file: {timeline_path}")
    return timeline_path

def generate_analysis_file(scenario_path, analysis):
    """Generate an analysis file for a scenario"""
    base_path = os.path.splitext(scenario_path)[0]
    analysis_path = f"{base_path}_analysis.md"
    
    with open(analysis_path, 'w', encoding='utf-8') as f:
        # Add frontmatter
        f.write("---\n")
        f.write(f"completion_status: {analysis['completion_status']}\n")
        f.write(f"post_count: {analysis['post_count']}\n")
        f.write(f"generated_date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("---\n\n")
        
        # Add title
        scenario_name = os.path.basename(base_path)
        f.write(f"# Analysis of {scenario_name}\n\n")
        
        # Overall status
        f.write("## Overall Status\n\n")
        f.write(f"**Completion Status**: {analysis['completion_status']}\n\n")
        f.write(f"**Post Count**: {analysis['post_count']}\n\n")
        f.write(f"**Has Conclusion**: {'Yes' if analysis['has_conclusion'] else 'No'}\n\n")
        
        # Unfinished plotlines
        f.write("## Unfinished Plotlines\n\n")
        if analysis['unfinished_plotlines']:
            for plotline in analysis['unfinished_plotlines']:
                f.write(f"- {plotline}\n")
        else:
            f.write("*No unfinished plotlines detected*\n")
    
    logger.info(f"Generated analysis file: {analysis_path}")
    return analysis_path

def generate_development_file(scenario_path, suggestions):
    """Generate a development suggestions file for a scenario"""
    base_path = os.path.splitext(scenario_path)[0]
    development_path = f"{base_path}_development.md"
    
    with open(development_path, 'w', encoding='utf-8') as f:
        # Add frontmatter
        f.write("---\n")
        f.write(f"suggestion_count: {len(suggestions)}\n")
        f.write(f"generated_date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("---\n\n")
        
        # Add title
        scenario_name = os.path.basename(base_path)
        f.write(f"# Development Suggestions for {scenario_name}\n\n")
        
        # Add suggestions
        for i, suggestion in enumerate(suggestions, 1):
            f.write(f"## Suggestion {i}: {suggestion['title']}\n\n")
            f.write(f"**Type**: {suggestion['type']}\n\n")
            f.write(f"{suggestion['description']}\n\n")
    
    logger.info(f"Generated development file: {development_path}")
    return development_path

import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class ScenarioProcessor:
    def __init__(self, scenario_path):
        self.scenario_path = Path(scenario_path)

    def validate_content(self, content):
        if not content or len(content.strip()) == 0:
            return False
        return True

    def process_scenario(self):
        try:
            content_file = self.scenario_path / "content.md"
            if not content_file.exists():
                logger.error(f"Content file missing for {self.scenario_path}")
                return False

            content = content_file.read_text(encoding='utf-8')
            if not self.validate_content(content):
                logger.error(f"Invalid content in {content_file}")
                return False

            # Process the valid content
            # Extract characters
            characters = extract_characters(content)
            logger.info(f"Extracted {len(characters)} characters")

            # Extract timeline
            timeline = extract_timeline(content)
            logger.info(f"Extracted {len(timeline)} timeline events")

            # Analyze completion
            analysis = analyze_completion(content, timeline)
            logger.info(f"Completion status: {analysis['completion_status']}")

            # Suggest development
            suggestions = suggest_development(content, characters, timeline, analysis)
            logger.info(f"Generated {len(suggestions)} development suggestions")

            # Generate supplementary files
            characters_path = generate_characters_file(self.scenario_path, characters)
            timeline_path = generate_timeline_file(self.scenario_path, timeline)
            analysis_path = generate_analysis_file(self.scenario_path, analysis)
            development_path = generate_development_file(self.scenario_path, suggestions)

            return {
                "scenario": self.scenario_path,
                "characters": characters_path,
                "timeline": timeline_path,
                "analysis": analysis_path,
                "development": development_path
            }

        except Exception as e:
            logger.error(f"Error processing scenario {self.scenario_path}: {e}")
            return {"scenario": self.scenario_path, "error": str(e)}


def main(args=None):
    """Main execution function"""
    if args is None:
        parser = argparse.ArgumentParser(description="EOTIR Scenario Processor - Process scenarios to generate supplementary files")
        parser.add_argument("--scenario", help="Path to a specific scenario file to process")
        parser.add_argument("--forum", help="Process scenarios from a specific forum")
        parser.add_argument("--year", help="Process scenarios from a specific year")
        args = parser.parse_args()
    
    # Find scenarios to process
    scenarios = find_scenarios(SCENARIOS_DIR, args.scenario, args.forum, args.year)
    logger.info(f"Found {len(scenarios)} scenarios to process")
    
    # Process each scenario
    results = []
    for scenario_path in scenarios:
        processor = ScenarioProcessor(scenario_path)
        result = processor.process_scenario()
        results.append(result)
    
    # Print summary
    logger.info(f"Processed {len(results)} scenarios")
    success_count = sum(1 for r in results if "error" not in r)
    logger.info(f"Successful: {success_count}, Failed: {len(results) - success_count}")
    
    return results

if __name__ == "__main__":
    main()