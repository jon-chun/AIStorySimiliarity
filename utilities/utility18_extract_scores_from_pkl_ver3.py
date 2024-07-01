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
    
    for element in ['characters', 'plot', 'setting', 'themes']:
        if element in data:
            features = data[element].get('similarity_by_features', {})
            if element == 'setting' and 'features' in features:
                features = features['features']
            elif element == 'themes' and 'features' in features:
                features = features['features']
            
            for key, value in features.items():
                result[f'{element}_{key}'] = value
            
            result[f'{element}_similarity_overall'] = data[element].get('similarity_overall', '')
    
    # Handle both spellings of social_dynamics
    if 'characters_social_dynamics' not in result and 'characters_sodial_dynamics' in result:
        result['characters_social_dynamics'] = result.pop('characters_sodial_dynamics')
    
    return result

def process_files():
    file_pattern = os.path.join(INPUT_ROOT_DIR, 'similarity-by-score_genaigenai_*_*_*_ver*.pkl')
    all_files = glob.glob(file_pattern)
    
    # Group files by reference_film and test_film
    file_groups = {}
    for file in all_files:
        match = re.search(FILE_PATTERN, os.path.basename(file))
        if match:
            reference_film, test_film, year, version = match.groups()
            key = f"{reference_film}_{test_film}"
            if key not in file_groups:
                file_groups[key] = []
            file_groups[key].append((file, reference_film, test_film, year, version))
    
    # Process each group
    for key, files in file_groups.items():
        data_list = []
        for file, reference_film, test_film, year, version in files:
            with open(file, 'rb') as f:
                data = pickle.load(f)
            
            # Assuming the structure is always the same, we take the first item
            first_key = list(data.keys())[0]
            extracted_data = extract_similarity_values(data[first_key])
            extracted_data['filename'] = os.path.basename(file)
            extracted_data['reference_film'] = reference_film
            extracted_data['test_film'] = test_film
            extracted_data['version_number'] = version
            data_list.append(extracted_data)
        
        # Create DataFrame
        df = pd.DataFrame(data_list)
        
        # Reorder columns
        columns = ['reference_film', 'test_film', 'version_number'] + [col for col in df.columns if col not in ['reference_film', 'test_film', 'version_number']]
        df = df[columns]
        
        # Save to CSV
        output_file = os.path.join(OUTPUT_ROOT_DIR, f"summary_genai_{key}.csv")
        df.to_csv(output_file, index=False)
        print(f"Saved {output_file}")

if __name__ == "__main__":
    process_files()