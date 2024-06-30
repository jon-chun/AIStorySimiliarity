import os
import json
import pandas as pd
import re
from collections import defaultdict

# Global configuration
MAX_SCRIPT_CT = 5
INPUT_FILE_TYPE = 'json'

# Get the current working directory and set up paths
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts_summary'))

def robust_json_parse(json_string):
    """Attempt to parse potentially malformed JSON strings."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        print(f"Warning: Unable to parse JSON string: {json_string[:100]}...")
        return {}

def process_file(file_path):
    """Process a single JSON file and return the data."""
    with open(file_path, 'r') as f:
        return robust_json_parse(f.read())

def extract_film_info(filename):
    """Extract reference film, test film, element type, and version from filename."""
    match = re.search(r'scripts_(.+)_(.+)_elements-(.+)_ver(\d+)\.json', filename)
    if match:
        return match.groups()
    return None, None, None, None


def process_files(input_root_dir, output_root_dir):
    for subdir in os.listdir(input_root_dir):
        subdir_path = os.path.join(input_root_dir, subdir)
        if os.path.isdir(subdir_path):
            # Group files by element type
            element_groups = defaultdict(list)
            for file in os.listdir(subdir_path):
                if file.endswith('.json'):
                    ref_film, test_film, element_type, version = extract_film_info(file)
                    if all((ref_film, test_film, element_type, version)):
                        element_groups[element_type].append((file, int(version)))

            # Process each element type
            summary_data = []
            for element_type, files in element_groups.items():
                # Sort files by version and take the first MAX_SCRIPT_CT
                sorted_files = sorted(files, key=lambda x: x[1])[:MAX_SCRIPT_CT]
                
                for file, version in sorted_files:
                    file_path = os.path.join(subdir_path, file)
                    data = process_file(file_path)
                    
                    row = {
                        'reference_film': ref_film,
                        'test_film': test_film,
                        'version_number': version,
                        'element_type': element_type
                    }
                    
                    # Process each feature in the element type
                    for feature, feature_data in data.items():
                        if isinstance(feature_data, dict) and 'similarity' in feature_data:
                            row[f'{element_type}-{feature}'] = feature_data['similarity']
                    
                    summary_data.append(row)

            # Create and save the summary DataFrame
            summary_df = pd.DataFrame(summary_data)
            output_file = f'summary_diff_elements_{ref_film}_{test_film}.csv'
            output_path = os.path.join(output_root_dir, output_file)
            summary_df.to_csv(output_path, index=False)
            print(f"Saved {output_file}")


def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)
    
    process_files(INPUT_ROOT_DIR, OUTPUT_ROOT_DIR)

if __name__ == "__main__":
    main()