import os
import json
import pandas as pd
import re
from collections import defaultdict
from fix_busted_json import repair_json as fix_busted_repair_json
from json_repair import repair_json
import logging

# Global configuration
MAX_SCRIPT_CT = 5
INPUT_FILE_TYPE = 'json'
OVERWRITE_FLAG = False

# Get the current working directory and set up paths
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts_summary'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def robust_json_parse(json_string):
    """Attempt to parse potentially malformed JSON strings."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        logging.warning("Initial JSON parsing failed. Attempting to repair...")
        try:
            fixed_json = fix_busted_repair_json(json_string)
            return json.loads(fixed_json)
        except:
            logging.warning("First repair attempt failed. Trying alternative method...")
            try:
                fixed_json = repair_json(json_string)
                return json.loads(fixed_json)
            except:
                logging.error(f"Unable to parse JSON string: {json_string[:100]}...")
                return {}

def process_file(file_path):
    """Process a single JSON file and return the data."""
    logging.info(f"Processing file: {file_path}")
    encodings = ['utf-8', 'latin-1', 'utf-16']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return robust_json_parse(f.read())
        except UnicodeDecodeError:
            logging.warning(f"Failed to decode with {encoding}, trying next...")
    logging.error(f"Failed to decode {file_path} with all attempted encodings")
    return {}

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
            logging.info(f"Processing subdirectory: {subdir}")
            
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
                logging.info(f"Processing element type: {element_type}")
                
                # Sort files by version and take the first MAX_SCRIPT_CT
                sorted_files = sorted(files, key=lambda x: x[1])[:MAX_SCRIPT_CT]
                
                for file, version in sorted_files:
                    file_path = os.path.join(subdir_path, file)
                    
                    # Check if output already exists
                    output_file = f'summary_diff_elements_{ref_film}_{test_film}.csv'
                    output_path = os.path.join(output_root_dir, output_file)
                    
                    if os.path.exists(output_path) and not OVERWRITE_FLAG:
                        existing_df = pd.read_csv(output_path)
                        if ((existing_df['reference_film'] == ref_film) & 
                            (existing_df['test_film'] == test_film) & 
                            (existing_df['version_number'] == version) & 
                            (existing_df['element_type'] == element_type)).any():
                            logging.info(f"Skipping already processed file: {file}")
                            continue
                    
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
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                if os.path.exists(output_path):
                    existing_df = pd.read_csv(output_path)
                    summary_df = pd.concat([existing_df, summary_df]).drop_duplicates().reset_index(drop=True)
                summary_df.to_csv(output_path, index=False)
                logging.info(f"Saved {output_file}")
            else:
                logging.info(f"No new data to save for {ref_film}_{test_film}")

def main():
    logging.info("Starting utility10_merge_score_diff_scripts.py")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)
    
    process_files(INPUT_ROOT_DIR, OUTPUT_ROOT_DIR)
    
    logging.info("Finished processing all files")

if __name__ == "__main__":
    main()