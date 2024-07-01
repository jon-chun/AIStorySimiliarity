import os
import glob
import pandas as pd
import pickle
import re


# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))

FILE_PATTERN = r'similarity-by-score_genaigenai_(.+?)_(.+?)_(\d{4})_ver(\d+)\.pkl'

def extract_similarity_values(data):
    result = {}
    
    # Characters
    characters = data['characters']['similarity_by_features']
    characters['similarity_overall'] = data['characters']['similarity_overall']
    for key, value in characters.items():
        result[f'characters_{key}'] = value
    
    # Plot
    plot = data['plot']['similarity_by_features']
    plot['similarity_overall'] = data['plot']['similarity_overall']
    for key, value in plot.items():
        result[f'plot_{key}'] = value
    
    # Setting
    setting = data['setting']['similarity_by_features']['features']
    setting['similarity_overall'] = data['setting']['similarity_overall']
    for key, value in setting.items():
        result[f'setting_{key}'] = value
    
    # Themes
    themes = data['themes']['similarity_by_features']['features']
    themes['similarity_overall'] = data['themes']['similarity_overall']
    for key, value in themes.items():
        result[f'themes_{key}'] = value
    
    return result

def process_files():
    file_pattern = os.path.join(INPUT_ROOT_DIR, 'similarity-by-score_genaigenai_*_*_*_ver*.pkl')
    all_files = glob.glob(file_pattern)
    
    # Group files by reference_film and test_film
    file_groups = {}
    for file in all_files:
        match = re.search(FILE_PATTERN, os.path.basename(file))
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                reference_film, test_film = groups[:2]
                key = f"{reference_film}_{test_film}"
                if key not in file_groups:
                    file_groups[key] = []
                file_groups[key].append(file)
            else:
                print(f"Warning: Unexpected filename format for {file}")
    
    # Process each group
    for key, files in file_groups.items():
        data_list = []
        for file in files:
            with open(file, 'rb') as f:
                data = pickle.load(f)
            
            # Assuming the structure is always the same, we take the first item
            first_key = list(data.keys())[0]
            extracted_data = extract_similarity_values(data[first_key])
            extracted_data['filename'] = os.path.basename(file)
            data_list.append(extracted_data)
        
        # Create DataFrame
        df = pd.DataFrame(data_list)
        
        # Save to CSV
        output_file = os.path.join(OUTPUT_ROOT_DIR, f"summary_genai_{key}.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved {output_file}")

if __name__ == "__main__":
    process_files()