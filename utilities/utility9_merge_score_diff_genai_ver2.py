import os
import pandas as pd
import pickle
import re
import json
import logging
from fix_busted_json import repair_json as fix_busted_repair_json
from json_repair import repair_json
from collections import defaultdict  # Missing import added

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global configuration
INPUT_FILE_TYPE = 'pkl'  # We will focus on processing the .pkl files as per the new requirements

# Get the current working directory and set up paths
cwd = os.getcwd()
input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai'))
output_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))

def robust_json_parse(json_string):
    """Attempt to parse potentially malformed JSON strings."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        try:
            fixed_json = fix_busted_repair_json(json_string)
            return json.loads(fixed_json)
        except:
            try:
                fixed_json = repair_json(json_string)
                return json.loads(fixed_json)
            except:
                logging.warning(f"Unable to parse JSON string: {json_string[:100]}...")
                return {}

def process_file(file_path):
    """Process a single file and return the data."""
    logging.info(f"Processing file: {file_path}")
    if INPUT_FILE_TYPE == 'pkl':
        with open(file_path, 'rb') as f:
            try:
                return pickle.load(f)
            except:
                logging.warning(f"Failed to load PKL file normally, trying as text: {file_path}")
                with open(file_path, 'r', errors='ignore') as text_f:
                    text_content = text_f.read()
                    return robust_json_parse(text_content)
    elif INPUT_FILE_TYPE == 'csv':
        df = pd.read_csv(file_path)
        data = {'data': [[{}]]}
        for col in df.columns:
            if col != 'overall':
                data['data'][0][0][col] = robust_json_parse(df[col].iloc[0])
        return data
    else:
        raise ValueError(f"Unsupported file type: {INPUT_FILE_TYPE}")

def process_files(input_root_dir, output_root_dir):
    logging.info(f"Processing files in directory: {input_root_dir}")
    
    # Get all .pkl files and sort them
    files = sorted([f for f in os.listdir(input_root_dir) if f.endswith('.pkl')])
    logging.info(f"Found {len(files)} .pkl files")

    # Group files by film combinations
    film_groups = defaultdict(list)
    for file in files:
        match = re.search(r'similarity-by-score_genaigenai_raiders-of-the-lost-ark_script_(.+)_ver(\d+)\.csv\.pkl', file)
        if match:
            film_name, version = match.groups()
            film_groups[film_name].append((file, int(version)))
        else:
            logging.warning(f"File name did not match expected pattern: {file}")
    
    logging.info(f"Grouped into {len(film_groups)} film combinations")

    for film_name, group_files in film_groups.items():
        logging.info(f"Processing group: {film_name}")
        summary_df = pd.DataFrame()
        short_summary_df = pd.DataFrame()
        
        for file, version in sorted(group_files, key=lambda x: x[1]):
            data = process_file(os.path.join(input_root_dir, file))
            logging.info(f"Data loaded from {file}: {data.keys() if isinstance(data, dict) else type(data)}")
            logging.info(f"Full data content: {data}")
            
            row = {
                'film_name': film_name,
                'version_number': version
            }

            # Adjusted to inspect the data structure and extract values correctly
            if 'characters' in data:
                col_data = data['characters']
                for feature in col_data.get('similarity_by_features', {}):
                    row[f'characters-{feature}'] = col_data['similarity_by_features'][feature]
            
            if 'plot' in data:
                col_data = data['plot']
                for feature in col_data.get('similarity_by_features', {}):
                    row[f'plot-{feature}'] = col_data['similarity_by_features'][feature]
            
            if 'setting' in data:
                col_data = data['setting']
                for feature in col_data.get('similarity_by_features', {}):
                    row[f'setting-{feature}'] = col_data['similarity_by_features'][feature]
            
            if 'themes' in data:
                col_data = data['themes']
                for feature in col_data.get('similarity_by_features', {}):
                    row[f'themes-{feature}'] = col_data['similarity_by_features'][feature]

            # Add the row to the summary DataFrame
            summary_df = pd.concat([summary_df, pd.DataFrame([row])], ignore_index=True)

            # Create a shorter summary with only key features
            short_row = {k: row[k] for k in ['film_name', 'version_number']}
            for k in row:
                if 'overall' in k:
                    short_row[k] = row[k]
            short_summary_df = pd.concat([short_summary_df, pd.DataFrame([short_row])], ignore_index=True)
        
        # Save the summary DataFrame to CSV
        output_file = f'summary_diff_genai_{film_name}.csv'
        short_output_file = f'summary_diff_genai_short_{film_name}.csv'
        output_path = os.path.join(output_root_dir, output_file)
        short_output_path = os.path.join(output_root_dir, short_output_file)
        summary_df.to_csv(output_path, index=False)
        short_summary_df.to_csv(short_output_path, index=False)
        logging.info(f"Saved {output_file} to {output_path}")
        logging.info(f"Saved {short_output_file} to {short_output_path}")

def main():
    logging.info("Starting the processing script")
    # Ensure output directory exists
    os.makedirs(output_root_dir, exist_ok=True)
    
    process_files(input_root_dir, output_root_dir)
    logging.info("Finished processing all files")

if __name__ == "__main__":
    main()
