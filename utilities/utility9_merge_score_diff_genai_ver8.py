import os
import re
import numpy as np
import pandas as pd
import pickle
from collections import defaultdict

# Global configuration
input_root_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'score_diff_genai'))
output_root_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'score_diff_genai_summary'))

file_pattern = r'similarity-by-score_genaigenai_(.+?)_(.+?)_(\d{4})_ver(\d+)\.pkl'

def safe_float(value):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except ValueError:
        return None

def extract_film_info(filename):
    match = re.match(file_pattern, filename)
    if match:
        reference_film, test_film, test_year, version = match.groups()
        return reference_film, test_film, test_year, int(version)
    return None, None, None, None

def process_file(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    
    extracted_data = {}
    main_data = data[list(data.keys())[0]]
    
    for category in ['characters', 'plot', 'setting', 'themes']:
        if category in main_data:
            category_data = main_data[category]
            extracted_data[f'{category}_similarity_overall'] = safe_float(category_data.get('similarity_overall'))
            
            similarity_features = category_data.get('similarity_by_features', {})
            if category == 'setting' or category == 'themes':
                similarity_features = similarity_features.get('features', {})
            
            for feature, value in similarity_features.items():
                if feature != 'film_title':  # Exclude film_title for setting
                    # Fix the typo in 'social_dynamics'
                    if feature == 'social_dynamics':
                        feature = 'social_dynamics'
                    extracted_data[f'{category}_{feature}'] = safe_float(value)
    
    return extracted_data

def process_files(input_root_dir):
    grouped_data = defaultdict(lambda: defaultdict(dict))
    
    for filename in os.listdir(input_root_dir):
        if filename.endswith('.pkl'):
            reference_film, test_film, test_year, version = extract_film_info(filename)
            if all((reference_film, test_film, test_year, version is not None)):
                key = (reference_film, test_film)
                
                file_path = os.path.join(input_root_dir, filename)
                file_data = process_file(file_path)
                
                # Use a unique identifier for each file to avoid overwriting
                unique_id = f"{test_year}_ver{version}"
                grouped_data[key][unique_id] = file_data
                print(f"Processed {filename}: {file_data}")  # Debugging statement
            else:
                print(f"Skipping file (pattern not matched): {filename}")  # Debugging statement
        else:
            print(f"Skipping file (not a .pkl file): {filename}")  # Debugging statement
    
    return grouped_data

def generate_summary(film_pair_data):
    summary_data = []
    for (reference_film, test_film), versions_data in film_pair_data.items():
        for version, features in versions_data.items():
            row = {
                'reference_film': reference_film,
                'test_film': test_film,
                'version_number': version
            }
            row.update(features)
            summary_data.append(row)
    
    # Sort by version number
    summary_data.sort(key=lambda x: x['version_number'])
    
    return summary_data

def main():
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)
        print(f"Created output directory: {output_root_dir}")  # Debugging statement
    else:
        print(f"Output directory already exists: {output_root_dir}")  # Debugging statement

    grouped_data = process_files(input_root_dir)
    
    expected_columns = [
        'reference_film', 'test_film', 'version_number',
        'characters_similarity_overall', 'characters_role', 'characters_backstory', 'characters_strengths',
        'characters_weakness', 'characters_psychology', 'characters_beliefs', 'characters_motivations',
        'characters_social_dynamics', 'characters_arc',
        'plot_similarity_overall', 'plot_protagonist_intro', 'plot_inciting_incident', 'plot_rising_action',
        'plot_climax', 'plot_resolution', 'plot_consequences', 'plot_final_outcome', 'plot_loose_ends',
        'plot_subplots',
        'setting_similarity_overall', 'setting_time_period', 'setting_geographical_location', 'setting_cultural_context',
        'setting_social_class', 'setting_ideology_and_beliefs', 'setting_economic_and_political_context',
        'themes_similarity_overall', 'themes_main_theme', 'themes_secondary_themes', 'themes_tertiary_themes',
        'themes_resolution_main_them', 'themes_resolution_secondary_themes', 'themes_resolution_tertiary_themes'
    ]
    
    for (reference_film, test_film), film_pair_data in grouped_data.items():
        summary_data = generate_summary({(reference_film, test_film): film_pair_data})
        df = pd.DataFrame(summary_data)
        
        # Ensure all expected columns are present
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 'N/A'
        
        # Reorder columns to match expected format
        df = df[expected_columns]
        
        output_file = f'summary_diff_genai_{reference_film}_{test_film}.csv'
        output_path = os.path.join(output_root_dir, output_file)
        df.to_csv(output_path, index=False)
        print(f"Saved {output_file} with {len(df)} rows")  # Debugging statement

if __name__ == "__main__":
    main()
