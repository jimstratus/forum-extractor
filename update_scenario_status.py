import os
import yaml
import argparse
from datetime import datetime

def list_scenarios():
    """List all available scenarios with their current status"""
    scenarios_dir = "Scenarios"
    print("\nAvailable Scenarios:")
    print("-" * 80)
    print(f"{'Forum':<25} {'Scenario':<40} {'Status':<15}")
    print("-" * 80)
    
    for forum in os.listdir(scenarios_dir):
        forum_dir = os.path.join(scenarios_dir, forum)
        if not os.path.isdir(forum_dir) or forum == "Indexes":
            continue
        
        for scenario in os.listdir(forum_dir):
            scenario_dir = os.path.join(forum_dir, scenario)
            if not os.path.isdir(scenario_dir):
                continue
            
            metadata_file = os.path.join(scenario_dir, "metadata.yaml")
            if not os.path.exists(metadata_file):
                continue
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)
                    status = metadata.get('status', 'Unknown')
                    print(f"{forum:<25} {scenario[:40]:<40} {status:<15}")
            except Exception as e:
                print(f"{forum:<25} {scenario[:40]:<40} Error: {str(e)}")

def update_status(forum, scenario, status):
    """Update the status of a specific scenario"""
    if status not in ["New", "In Progress", "Complete"]:
        print(f"Error: Invalid status '{status}'. Must be 'New', 'In Progress', or 'Complete'.")
        return False
    
    scenario_dir = os.path.join("Scenarios", forum, scenario)
    if not os.path.isdir(scenario_dir):
        print(f"Error: Scenario directory '{scenario_dir}' not found.")
        return False
    
    metadata_file = os.path.join(scenario_dir, "metadata.yaml")
    if not os.path.exists(metadata_file):
        print(f"Error: Metadata file '{metadata_file}' not found.")
        return False
    
    try:
        # Load existing metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = yaml.safe_load(f)
        
        # Update status and add last updated timestamp
        old_status = metadata.get('status', 'Unknown')
        metadata['status'] = status
        metadata['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save updated metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False)
        
        print(f"Updated status for {forum}/{scenario} from '{old_status}' to '{status}'")
        
        # Also update the report if it exists
        report_file = os.path.join("Reports", f"{forum}_{scenario}_report.md")
        if os.path.exists(report_file):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace status in the report
                content = content.replace(f"- **Status**: {old_status}", f"- **Status**: {status}")
                
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Updated status in report file: {report_file}")
            except Exception as e:
                print(f"Warning: Could not update report file: {str(e)}")
        
        return True
    
    except Exception as e:
        print(f"Error updating metadata: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update scenario status')
    parser.add_argument('--list', action='store_true', help='List all scenarios with their current status')
    parser.add_argument('--forum', help='Forum name (e.g., Red_Scenario)')
    parser.add_argument('--scenario', help='Scenario folder name')
    parser.add_argument('--status', choices=['New', 'In Progress', 'Complete'], help='New status to set')
    
    args = parser.parse_args()
    
    if args.list:
        list_scenarios()
        return
    
    if args.forum and args.scenario and args.status:
        update_status(args.forum, args.scenario, args.status)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
