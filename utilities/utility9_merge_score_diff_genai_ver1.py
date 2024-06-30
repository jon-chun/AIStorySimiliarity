import os
import pandas as pd
import pickle
import re
from collections import defaultdict
import concurrent.futures
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

cwd = os.getcwd()
input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai'))
output_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))

def log_info(message):
    logging.info(message)
    print(message)

def process_file(file_path):
    log_info(f"Processing file: {file_path}")
    if not os.path.exists(file_path):
        log_info(f"Warning: File not found: {file_path}")
        return {}

    with open(file_path, 'rb') as f:
        try:
            return pickle.load(f)
        except Exception as e:
            log_info(f"Error processing file {file_path}: {str(e)}")
            return {}

def extract_features(data):
    features = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                if 'similarity_overall' in value:
                    features[f'{key}_similarity_overall'] = value['similarity_overall']
                if 'similarity_by_features' in value:
                    for sub_key, sub_value in value['similarity_by_features'].items():
                        if isinstance(sub_value, dict):
                            for sub_sub_key, sub_sub_value in sub_value.items():
                                features[f'{key}_{sub_key}_{sub_sub_key}'] = sub_sub_value
                        else:
                            features[f'{key}_{sub_key}'] = sub_value
    return features

def process_film_group(group_data):
    reference_film, test_film, group_files = group_data
    log_info(f"Processing film group: {reference_film} vs {test_film}")
    summary_df = pd.DataFrame()
    
    for file in group_files:
        file_path = os.path.join(input_root_dir, file)
        data = process_file(file_path)
        
        if not data:
            log_info(f"No data found for file: {file}")
            continue
        
        features = extract_features(data)
        
        timestamp = re.search(r'(\d{8}-\d{6})', file)
        timestamp = timestamp.group(1) if timestamp else 'unknown'
        
        row = {
            'reference_film': reference_film,
            'test_film': test_film,
            'timestamp': timestamp,
            **features
        }
        
        summary_df = pd.concat([summary_df, pd.DataFrame([row])], ignore_index=True)
    
    log_info(f"Processed {len(summary_df)} files for {reference_film} vs {test_film}")
    return summary_df

def process_files(input_root_dir, output_root_dir):
    log_info(f"Starting to process files in {input_root_dir}")
    
    all_files = [f for f in os.listdir(input_root_dir) if f.endswith('.pkl')]
    log_info(f"Found {len(all_files)} pkl files")
    
    film_groups = defaultdict(list)
    for file in all_files:
        match = re.search(r'genai_(.+)_(.+)_\d{8}-\d{6}', file)
        if match:
            reference_film, test_film = match.groups()
            film_groups[(reference_film, test_film)].append(file)
    
    log_info(f"Grouped files for {len(film_groups)} film comparisons")
    
    group_data = [(reference_film, test_film, group_files) 
                  for (reference_film, test_film), group_files in film_groups.items()]
    
    log_info("Starting parallel processing of film groups")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_film_group, group_data))
    
    log_info("Saving results")
    for (reference_film, test_film), summary_df in zip(film_groups.keys(), results):
        if not summary_df.empty:
            output_file = f'summary_diff_genai_{reference_film}_{test_film}.csv'
            output_path = os.path.join(output_root_dir, output_file)
            summary_df.to_csv(output_path, index=False)
            log_info(f"Saved {output_file}")
        else:
            log_info(f"No data to save for {reference_film} vs {test_film}")

def main():
    log_info("Starting main function")
    log_info(f"Input directory: {input_root_dir}")
    log_info(f"Output directory: {output_root_dir}")

    os.makedirs(output_root_dir, exist_ok=True)
    log_info(f"Ensured output directory exists: {output_root_dir}")
    
    process_files(input_root_dir, output_root_dir)
    log_info("Finished processing files")

if __name__ == "__main__":
    main()