import os
import pandas as pd
import pickle
import re
from collections import defaultdict
import json
from fix_busted_json import repair_json as fix_busted_repair_json
from json_repair import repair_json
import concurrent.futures
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global configuration
INPUT_FILE_TYPE = 'json'  # Change this to 'pkl' for pickle files

# Get the current working directory and set up paths
cwd = os.getcwd()
input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts'))
output_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts_summary'))

def log_info(message):
    logging.info(message)
    print(message)

def robust_json_parse(json_string):
    """Attempt to parse potentially malformed JSON strings."""
    log_info(f"Attempting to parse JSON string: {json_string[:100]}...")
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        log_info("Initial JSON parsing failed, attempting to repair...")
        try:
            fixed_json = fix_busted_repair_json(json_string)
            return json.loads(fixed_json)
        except:
            log_info("First repair attempt failed, trying alternative method...")
            try:
                fixed_json = repair_json(json_string)
                return json.loads(fixed_json)
            except:
                log_info(f"Warning: Unable to parse JSON string: {json_string[:100]}...")
                return {}

def process_file(file_path):
    """Process a single file and return the data."""
    log_info(f"Processing file: {file_path}")
    if not os.path.exists(file_path):
        log_info(f"Warning: File not found: {file_path}")
        return {}

    if INPUT_FILE_TYPE == 'pkl':
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    elif INPUT_FILE_TYPE == 'json':
        with open(file_path, 'r', encoding='utf-8') as f:
            json_string = f.read()
        return robust_json_parse(json_string)
    else:
        raise ValueError(f"Unsupported file type: {INPUT_FILE_TYPE}")

def process_film_group(group_data):
    reference_film, test_film, group_files, input_root_dir = group_data
    log_info(f"Processing film group: {reference_film} vs {test_film}")
    summary_df = pd.DataFrame()
    
    for file, version in sorted(group_files, key=lambda x: x[1]):
        file_path = os.path.join(input_root_dir, f"scripts_{reference_film}_{test_film}", file)
        data = process_file(file_path)
        
        if not data:
            log_info(f"No data found for file: {file}")
            continue
        
        row = {
            'reference_film': reference_film,
            'test_film': test_film,
            'version_number': version
        }
        
        # Process each feature
        for i in range(1, 5):  # Assuming 4 features
            feature_key = f'feature_{i}'
            if feature_key in data:
                row[f'feature_{i}_value'] = data[feature_key].get('value')
                row[f'feature_{i}_description'] = data[feature_key].get('description')
        
        # Add overall similarity
        row['similarity_overall'] = data.get('similarity_overall')
        
        summary_df = pd.concat([summary_df, pd.DataFrame([row])], ignore_index=True)
    
    log_info(f"Processed {len(summary_df)} files for {reference_film} vs {test_film}")
    return summary_df

def process_files(input_root_dir, output_root_dir):
    log_info(f"Starting to process files in {input_root_dir}")
    
    # Get all subdirectories (film comparisons)
    film_comparisons = [d for d in os.listdir(input_root_dir) if os.path.isdir(os.path.join(input_root_dir, d))]
    log_info(f"Found {len(film_comparisons)} film comparison directories")
    
    # Group files by film combinations
    film_groups = defaultdict(list)
    for comparison in film_comparisons:
        log_info(f"Processing comparison directory: {comparison}")
        match = re.search(r'scripts_(.+)_(.+)', comparison)
        if match:
            reference_film, test_film = match.groups()
            comparison_dir = os.path.join(input_root_dir, comparison)
            for file in os.listdir(comparison_dir):
                if file.startswith('similarity-by-score') and file.endswith(f'.{INPUT_FILE_TYPE}'):
                    version_match = re.search(r'ver(\d+)', file)
                    if version_match:
                        version = int(version_match.group(1))
                        film_groups[(reference_film, test_film)].append((file, version))
            log_info(f"Found {len(film_groups[(reference_film, test_film)])} files for {reference_film} vs {test_film}")
    
    log_info(f"Grouped files for {len(film_groups)} film comparisons")
    
    # Prepare data for parallel processing
    group_data = [(reference_film, test_film, group_files, input_root_dir) 
                  for (reference_film, test_film), group_files in film_groups.items()]
    
    # Process film groups in parallel
    log_info("Starting parallel processing of film groups")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_film_group, group_data))
    
    # Save results
    log_info("Saving results")
    for (reference_film, test_film), summary_df in zip(film_groups.keys(), results):
        if not summary_df.empty:
            output_file = f'summary_diff_scripts_{reference_film}_{test_film}.csv'
            output_path = os.path.join(output_root_dir, output_file)
            summary_df.to_csv(output_path, index=False)
            log_info(f"Saved {output_file}")
        else:
            log_info(f"No data to save for {reference_film} vs {test_film}")

def main():
    log_info("Starting main function")
    log_info(f"Input directory: {input_root_dir}")
    log_info(f"Output directory: {output_root_dir}")
    log_info(f"Input file type: {INPUT_FILE_TYPE}")

    # Ensure output directory exists
    os.makedirs(output_root_dir, exist_ok=True)
    log_info(f"Ensured output directory exists: {output_root_dir}")
    
    process_files(input_root_dir, output_root_dir)
    log_info("Finished processing files")

if __name__ == "__main__":
    main()