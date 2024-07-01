import os
import pandas as pd
import pickle
import re
from collections import defaultdict
import numpy as np

# Global configuration
INPUT_FILE_TYPE = 'pkl'
MAX_VERSIONS = 33  # Adjust based on the maximum version number

# Set up input and output paths
cwd = os.getcwd()
input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai'))
output_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))

def process_file(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    
    # Extract relevant information from the data structure
    extracted_data = {}
    for category in ['characters', 'plot', 'setting', 'themes']:
        if category in data[list(data.keys())[0]]:
            category_data = data[list(data.keys())[0]][category]
            if 'similarity_overall' in category_data:
                extracted_data[f'{category}-overall'] = category_data['similarity_overall']
            if 'similarity_by_features' in category_data:
                for feature, value in category_data['similarity_by_features'].items():
                    if isinstance(value, dict):
                        for sub_feature, sub_value in value.items():
                            extracted_data[f'{category}-{sub_feature}'] = sub_value
                    else:
                        extracted_data[f'{category}-{feature}'] = value
    
    return extracted_data

def process_files(input_root_dir, output_root_dir):
    file_pattern = r'similarity-by-score_genaigenai_(.+)_(.+)_(\d{4})_ver(\d+)\.pkl'
    grouped_data = defaultdict(lambda: defaultdict(list))
    
    for filename in os.listdir(input_root_dir):
        match = re.match(file_pattern, filename)
        if match:
            reference_film, test_film, test_year, version = match.groups()
            key = (reference_film, test_film, test_year)
            
            file_path = os.path.join(input_root_dir, filename)
            file_data = process_file(file_path)
            
            for feature, value in file_data.items():
                grouped_data[key][feature].append(value)
    
    summary_data = []
    for (reference_film, test_film, test_year), features in grouped_data.items():
        row = {
            'reference_film': reference_film,
            'test_film': test_film,
            'test_year': test_year
        }
        for feature, values in features.items():
            row[feature] = np.mean(values)
        summary_data.append(row)
    
    df = pd.DataFrame(summary_data)
    output_file = 'summary_diff_elements_genai.csv'
    output_path = os.path.join(output_root_dir, output_file)
    df.to_csv(output_path, index=False)
    print(f"Saved {output_file}")

def main():
    os.makedirs(output_root_dir, exist_ok=True)
    process_files(input_root_dir, output_root_dir)

if __name__ == "__main__":
    main()