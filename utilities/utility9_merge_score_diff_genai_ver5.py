import os
import re
import numpy as np
import pandas as pd
import pickle
from collections import defaultdict

# Global configuration
input_root_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'score_diff_genai'))
output_root_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'score_diff_genai_summary'))

file_pattern = r'similarity-by-score_genaigenai_(.+)_script_(.+)_(\d{4})_ver(\d+)\.pkl'

def safe_float(value):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None

def process_file(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    
    extracted_data = {}
    for category in ['characters', 'plot', 'setting', 'themes']:
        if category in data[list(data.keys())[0]]:
            category_data = data[list(data.keys())[0]][category]
            if 'similarity_overall' in category_data:
                extracted_data[f'{category}-overall'] = safe_float(category_data['similarity_overall'])
            if 'similarity_by_features' in category_data:
                for feature, value in category_data['similarity_by_features'].items():
                    if isinstance(value, dict):
                        for sub_feature, sub_value in value.items():
                            extracted_data[f'{category}-{sub_feature}'] = safe_float(sub_value)
                    else:
                        extracted_data[f'{category}-{feature}'] = safe_float(value)
    
    return extracted_data

def process_files(input_root_dir):
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for filename in os.listdir(input_root_dir):
        match = re.match(file_pattern, filename)
        if match:
            reference_film, test_film, test_year, version = match.groups()
            key = (reference_film, test_film)
            
            file_path = os.path.join(input_root_dir, filename)
            file_data = process_file(file_path)
            
            for feature, value in file_data.items():
                grouped_data[key][test_year][feature].append(value)
    
    return grouped_data

def generate_summary(film_pair_data):
    summary_data = []
    for (reference_film, test_film), years_data in film_pair_data.items():
        for test_year, features in years_data.items():
            row = {
                'reference_film': reference_film,
                'test_film': test_film,
                'test_year': test_year
            }
            for feature, values in features.items():
                numeric_values = [v for v in values if v is not None]
                if numeric_values:
                    row[feature] = np.mean(numeric_values)
                else:
                    row[feature] = 'N/A'
            summary_data.append(row)
    return summary_data

def main():
    os.makedirs(output_root_dir, exist_ok=True)
    grouped_data = process_files(input_root_dir)
    
    for (reference_film, test_film), film_pair_data in grouped_data.items():
        summary_data = generate_summary({(reference_film, test_film): film_pair_data})
        df = pd.DataFrame(summary_data)
        
        output_file = f'summary_diff_elements_{reference_film}_{test_film}.csv'
        output_path = os.path.join(output_root_dir, output_file)
        df.to_csv(output_path, index=False)
        print(f"Saved {output_file}")

if __name__ == "__main__":
    main()