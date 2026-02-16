#!/usr/bin/env python3
"""Generate curation template from metadata."""

import sys
import csv

def generate_template(metadata_path, output_path):
    """Create curation template with all stems."""
    with open(metadata_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Add curation columns
    fieldnames = ['song', 'stem', 'tempo', 'key', 'duration_seconds', 
                  'include', 'split', 'genre', 'mood', 'era', 'notes']
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, row in enumerate(rows):
            # Default: include 80% in train, 20% in valid
            split = 'train' if i % 5 != 0 else 'valid'
            
            writer.writerow({
                'song': row['song'],
                'stem': row['stem'],
                'tempo': row['tempo'],
                'key': row['key'],
                'duration_seconds': row['duration_seconds'],
                'include': '',  # User fills: yes/no
                'split': split,  # User can override
                'genre': '',  # User fills: rock, jazz, etc
                'mood': '',  # User fills: upbeat, dark, etc
                'era': '',  # User fills: early, mid, late
                'notes': ''  # User notes
            })
    
    print(f"Created curation template with {len(rows)} stems")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_curation.py <metadata.csv> <output.csv>")
        sys.exit(1)
    
    generate_template(sys.argv[1], sys.argv[2])
