import os
import yaml
import argparse
from datetime import datetime

# Configuration
SCENARIOS_DIR = "Scenarios"
REPORTS_DIR = "Reports"

def load_metadata(metadata_file):
    """Load metadata from YAML file"""
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading metadata from {metadata_file}: {str(e)}")
        return {}

def load_content(content_file):
    """Load content from markdown file"""
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading content from {content_file}: {str(e)}")
        return ""

def generate_combined_report(scenario_dir, report_file):
    """Generate combined report for a scenario"""
    print(f"Generating report for {os.path.basename(scenario_dir)}")
    
    # Load files
    metadata_file = os.path.join(scenario_dir, "metadata.yaml")
    content_file = os.path.join(scenario_dir, "content.md")
    dramatis_file = os.path.join(scenario_dir, "dramatis_personae.md")
    timeline_file = os.path.join(scenario_dir, "timeline.md")
    plot_file = os.path.join(scenario_dir, "plot_development.md")
    
    # Load metadata
    metadata = load_metadata(metadata_file)
    
    # Create the combined report
    with open(report_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# {metadata.get('title', 'Unknown Scenario')}\n\n")
        f.write(f"## Scenario Metadata\n\n")
        f.write(f"- **Year**: {metadata.get('year', 'Unknown')}\n")
        f.write(f"- **Forum**: {metadata.get('forum', 'Unknown')}\n")
        f.write(f"- **Author**: {metadata.get('author', 'Unknown')}\n")
        f.write(f"- **Status**: {metadata.get('status', 'New')}\n")
        f.write(f"- **URL**: [{metadata.get('url', '#')}]({metadata.get('url', '#')})\n")
        f.write(f"- **Post Count**: {metadata.get('post_count', 0)}\n")
        f.write(f"- **Extracted**: {metadata.get('extracted_date', 'Unknown')}\n")
        f.write(f"- **Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Add dramatis personae
        if os.path.exists(dramatis_file):
            dp_content = load_content(dramatis_file)
            # Remove the title as we'll add our own
            dp_content = dp_content.split('\n', 1)[1] if '\n' in dp_content else dp_content
            f.write(f"## Dramatis Personae\n{dp_content}\n\n")
        
        # Add timeline
        if os.path.exists(timeline_file):
            timeline_content = load_content(timeline_file)
            # Remove the title as we'll add our own
            timeline_content = timeline_content.split('\n', 1)[1] if '\n' in timeline_content else timeline_content
            f.write(f"## Timeline of Events\n{timeline_content}\n\n")
        
        # Add plot development suggestions
        if os.path.exists(plot_file):
            plot_content = load_content(plot_file)
            # Remove the title as we'll add our own
            plot_content = plot_content.split('\n', 1)[1] if '\n' in plot_content else plot_content
            f.write(f"## Plot Development Suggestions\n{plot_content}\n\n")
        
        # Add full content
        if os.path.exists(content_file):
            content = load_content(content_file)
            # Remove the title and metadata as we've already added it
            if '\n\n' in content:
                # Skip the title and metadata
                parts = content.split('\n\n', 3)
                if len(parts) >= 4:
                    content = parts[3]
            f.write(f"## Full Content\n\n{content}\n")
    
    print(f"Report saved to {report_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate combined reports for scenarios')
    parser.add_argument('--forum', help='Forum name to process (e.g., Red_Scenario)')
    parser.add_argument('--scenario', help='Specific scenario folder name to process')
    args = parser.parse_args()
    
    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    if args.scenario:
        # Find the scenario folder
        scenario_found = False
        for forum in os.listdir(SCENARIOS_DIR):
            forum_dir = os.path.join(SCENARIOS_DIR, forum)
            if not os.path.isdir(forum_dir):
                continue
            
            for scenario in os.listdir(forum_dir):
                if scenario == args.scenario:
                    scenario_dir = os.path.join(forum_dir, scenario)
                    report_file = os.path.join(REPORTS_DIR, f"{forum}_{scenario}_report.md")
                    generate_combined_report(scenario_dir, report_file)
                    scenario_found = True
                    break
            
            if scenario_found:
                break
        
        if not scenario_found:
            print(f"Scenario '{args.scenario}' not found in any forum")
    
    elif args.forum:
        # Process specific forum
        forum_dir = os.path.join(SCENARIOS_DIR, args.forum)
        if not os.path.isdir(forum_dir):
            print(f"Forum directory '{args.forum}' not found")
            return
        
        forum_reports_dir = os.path.join(REPORTS_DIR, args.forum)
        os.makedirs(forum_reports_dir, exist_ok=True)
        
        for scenario in os.listdir(forum_dir):
            scenario_dir = os.path.join(forum_dir, scenario)
            if os.path.isdir(scenario_dir):
                report_file = os.path.join(forum_reports_dir, f"{scenario}_report.md")
                generate_combined_report(scenario_dir, report_file)
    
    else:
        # Process all forums
        for forum in os.listdir(SCENARIOS_DIR):
            forum_dir = os.path.join(SCENARIOS_DIR, forum)
            if not os.path.isdir(forum_dir):
                continue
            
            forum_reports_dir = os.path.join(REPORTS_DIR, forum)
            os.makedirs(forum_reports_dir, exist_ok=True)
            
            for scenario in os.listdir(forum_dir):
                scenario_dir = os.path.join(forum_dir, scenario)
                if os.path.isdir(scenario_dir):
                    report_file = os.path.join(forum_reports_dir, f"{scenario}_report.md")
                    generate_combined_report(scenario_dir, report_file)

if __name__ == "__main__":
    main()
