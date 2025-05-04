#!/usr/bin/env python3
"""
Dataset statistics script for the EOTIR LLM training dataset.
This script analyzes the processed data files and generates reports on distribution,
sizes, and other relevant metrics.
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def count_words(file_path):
    """Count the number of words in a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            return len(text.split())
    except Exception as e:
        print(f"Error counting words in {file_path}: {e}")
        return 0

def get_category_stats(base_dir="LLM"):
    """Collect statistics for each category directory"""
    base_path = Path(base_dir)
    categories = defaultdict(lambda: {"file_count": 0, "total_words": 0, "avg_words_per_file": 0, "files": []})
    
    # Skip metadata directory
    skip_dirs = ["metadata"]
    
    for root, dirs, files in os.walk(base_path):
        rel_path = os.path.relpath(root, base_path)
        
        # Skip the metadata directory
        if any(skip_dir in rel_path for skip_dir in skip_dirs):
            continue
            
        # If we're in a category directory
        if rel_path != "." and files:
            category = rel_path.replace("\\", "/")
            
            # Count files and words
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    word_count = count_words(file_path)
                    
                    categories[category]["file_count"] += 1
                    categories[category]["total_words"] += word_count
                    categories[category]["files"].append({"name": file, "word_count": word_count})
    
    # Calculate averages
    for category, stats in categories.items():
        if stats["file_count"] > 0:
            stats["avg_words_per_file"] = stats["total_words"] / stats["file_count"]
    
    return categories

def generate_category_charts(categories, output_dir="LLM/metadata"):
    """Generate charts displaying the distribution of files and words by category"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Prepare data for charts
    categories_sorted = sorted(categories.items(), key=lambda x: x[1]["file_count"], reverse=True)
    cat_names = [cat for cat, _ in categories_sorted]
    file_counts = [stats["file_count"] for _, stats in categories_sorted]
    word_counts = [stats["total_words"] for _, stats in categories_sorted]
    
    # Shorten category names for display
    short_names = [cat.split('/')[-1] if '/' in cat else cat for cat in cat_names]
    
    # Figure for file counts
    plt.figure(figsize=(12, 8))
    plt.bar(short_names, file_counts, color='skyblue')
    plt.title('Number of Files by Category')
    plt.ylabel('Number of Files')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path / 'file_distribution.png')
    plt.close()
    
    # Figure for word counts
    plt.figure(figsize=(12, 8))
    plt.bar(short_names, word_counts, color='lightgreen')
    plt.title('Total Words by Category')
    plt.ylabel('Word Count')
    plt.xticks(rotation=45, ha='right')
    
    # Format y-axis with comma separators for thousands
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    plt.tight_layout()
    plt.savefig(output_path / 'word_distribution.png')
    plt.close()
    
    # Figure for average words per file
    avg_words = [stats["avg_words_per_file"] for _, stats in categories_sorted]
    plt.figure(figsize=(12, 8))
    plt.bar(short_names, avg_words, color='salmon')
    plt.title('Average Words per File by Category')
    plt.ylabel('Average Word Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path / 'avg_words_distribution.png')
    plt.close()
    
    return output_path / 'file_distribution.png', output_path / 'word_distribution.png', output_path / 'avg_words_distribution.png'

def generate_word_count_histogram(categories, output_dir="LLM/metadata"):
    """Generate a histogram of file sizes (in words)"""
    output_path = Path(output_dir)
    
    # Collect all file word counts
    all_word_counts = []
    for category, stats in categories.items():
        for file_info in stats["files"]:
            all_word_counts.append(file_info["word_count"])
    
    # Create histogram
    plt.figure(figsize=(12, 8))
    plt.hist(all_word_counts, bins=50, color='lightblue', edgecolor='black')
    plt.title('Distribution of File Sizes (Word Count)')
    plt.xlabel('Word Count')
    plt.ylabel('Number of Files')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add vertical line for average
    avg_word_count = sum(all_word_counts) / len(all_word_counts) if all_word_counts else 0
    plt.axvline(x=avg_word_count, color='red', linestyle='--', 
                label=f'Average: {avg_word_count:.0f} words')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path / 'word_count_histogram.png')
    plt.close()
    
    return output_path / 'word_count_histogram.png'

def generate_document_analysis(categories, output_dir="LLM/metadata"):
    """Generate document type analysis"""
    output_path = Path(output_dir)
    
    # Detect document types (reports, technical docs, etc.)
    document_types = Counter()
    
    # Document type patterns
    doc_type_patterns = {
        "Character Profile": r"(?i)(character|profile|personnel|biography|background)",
        "Technical Document": r"(?i)(specifications|technical|manual|schematic|ship|vessel|starfighter)",
        "Intelligence Report": r"(?i)(intelligence|report|briefing|classified|security|surveillance)",
        "Legal Document": r"(?i)(law|regulation|act|charter|statute|legal|court)",
        "Narrative": r"(?i)(story|scenario|mission|campaign|narrative|chapter)",
        "Administrative": r"(?i)(admin|procedure|protocol|guideline|instruction)",
        "Correspondence": r"(?i)(letter|message|communique|correspondence)"
    }
    
    # Count file types
    for category, stats in categories.items():
        for file_info in stats["files"]:
            file_name = file_info["name"]
            
            # Check each pattern
            matched = False
            for doc_type, pattern in doc_type_patterns.items():
                if re.search(pattern, file_name):
                    document_types[doc_type] += 1
                    matched = True
                    break
            
            # If no match, count as "Other"
            if not matched:
                document_types["Other"] += 1
    
    # Generate pie chart
    plt.figure(figsize=(12, 8))
    labels = list(document_types.keys())
    sizes = list(document_types.values())
    
    # Sort by size
    sorted_data = sorted(zip(labels, sizes), key=lambda x: x[1], reverse=True)
    labels = [x[0] for x in sorted_data]
    sizes = [x[1] for x in sorted_data]
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
            shadow=True, wedgeprops={'edgecolor': 'white'})
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Distribution of Document Types')
    plt.tight_layout()
    plt.savefig(output_path / 'document_types.png')
    plt.close()
    
    return output_path / 'document_types.png'

def generate_summary_report(categories, chart_paths, output_dir="LLM/metadata"):
    """Generate a summary report with statistics and charts"""
    output_path = Path(output_dir)
    
    # Prepare overall statistics
    total_files = sum(stats["file_count"] for stats in categories.values())
    total_words = sum(stats["total_words"] for stats in categories.values())
    avg_words_per_file = total_words / total_files if total_files > 0 else 0
    
    # Sort categories by file count
    sorted_categories = sorted(categories.items(), key=lambda x: x[1]["file_count"], reverse=True)
    
    # Generate markdown report
    with open(output_path / 'dataset_report.md', 'w') as f:
        f.write("# EOTIR LLM Dataset Statistics\n\n")
        
        # Overall statistics
        f.write("## Overall Statistics\n\n")
        f.write(f"- **Total Files**: {total_files:,}\n")
        f.write(f"- **Total Words**: {total_words:,}\n")
        f.write(f"- **Average Words per File**: {avg_words_per_file:.1f}\n\n")
        
        # Category statistics
        f.write("## Category Statistics\n\n")
        f.write("| Category | Files | Total Words | Avg Words/File |\n")
        f.write("|----------|-------|-------------|----------------|\n")
        
        for category, stats in sorted_categories:
            f.write(f"| {category} | {stats['file_count']:,} | {stats['total_words']:,} | {stats['avg_words_per_file']:.1f} |\n")
        
        # Charts
        f.write("\n## Data Distribution\n\n")
        
        # Embed images using relative paths
        for chart_path in chart_paths:
            rel_path = os.path.relpath(chart_path, output_path)
            f.write(f"![{os.path.basename(chart_path)}]({rel_path})\n\n")
        
        # Word count distribution
        f.write("\n## File Size Distribution\n\n")
        f.write("The dataset includes files of various sizes, from small documents with fewer than 100 words to large documents with several thousand words.\n\n")
        
        # Top largest files
        all_files = []
        for category, stats in categories.items():
            for file_info in stats["files"]:
                all_files.append((category, file_info["name"], file_info["word_count"]))
        
        largest_files = sorted(all_files, key=lambda x: x[2], reverse=True)[:20]
        
        f.write("### Largest Files\n\n")
        f.write("| Category | File | Word Count |\n")
        f.write("|----------|------|------------|\n")
        
        for category, file_name, word_count in largest_files:
            f.write(f"| {category} | {file_name} | {word_count:,} |\n")
        
        # Recommendations
        f.write("\n## Recommendations for Training\n\n")
        f.write("Based on the analysis of the dataset, here are some recommendations for LLM training:\n\n")
        f.write("1. **Balance Categories**: Consider balancing categories in your training process to ensure the model doesn't over-index on any particular content type.\n")
        f.write("2. **File Size Consideration**: Be aware of the distribution of file sizes. Consider chunking larger files to create more consistent training examples.\n")
        f.write("3. **Domain-Specific Terms**: Create a custom tokenizer or vocabulary expansion to handle EOTIR-specific terminology.\n")
        f.write("4. **Content Diversity**: The dataset has a good mix of content types (narratives, technical documents, character profiles, etc.) which will help the model learn different writing styles and formats.\n")
        
    # Also save the statistics as JSON for programmatic use
    stats_data = {
        "overall": {
            "total_files": total_files,
            "total_words": total_words,
            "avg_words_per_file": avg_words_per_file
        },
        "categories": {cat: {"file_count": stats["file_count"], "total_words": stats["total_words"], 
                            "avg_words_per_file": stats["avg_words_per_file"]}
                    for cat, stats in categories.items()}
    }
    
    with open(output_path / 'dataset_stats.json', 'w') as f:
        json.dump(stats_data, f, indent=2)
    
    return output_path / 'dataset_report.md'

def main():
    parser = argparse.ArgumentParser(description="Generate statistics for the EOTIR LLM dataset")
    parser.add_argument("--dir", default="LLM", help="Base directory for the dataset")
    parser.add_argument("--output", default="LLM/metadata", help="Output directory for reports and charts")
    
    args = parser.parse_args()
    
    print("Analyzing dataset...")
    categories = get_category_stats(args.dir)
    
    print("Generating charts...")
    chart_paths = list(generate_category_charts(categories, args.output))
    
    print("Generating word count histogram...")
    word_hist_path = generate_word_count_histogram(categories, args.output)
    chart_paths.append(word_hist_path)
    
    print("Analyzing document types...")
    doc_type_path = generate_document_analysis(categories, args.output)
    chart_paths.append(doc_type_path)
    
    print("Generating summary report...")
    report_path = generate_summary_report(categories, chart_paths, args.output)
    
    print(f"Analysis complete! Report saved to {report_path}")

if __name__ == "__main__":
    main()
