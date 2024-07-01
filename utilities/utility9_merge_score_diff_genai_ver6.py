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

def extract_film_info(filename):
    match = re.match(file_pattern, filename)
    if match:
        reference_film = match.group(1).split('_')[0]  # Remove year from reference film
        test_film, test_year, version = match.groups()[1:]
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
                    # Fix the typo in 'sodial_dynamics'
                    if feature == 'sodial_dynamics':
                        feature = 'social_dynamics'
                    extracted_data[f'{category}_{feature}'] = safe_float(value)
    
    return extracted_data

def process_files(input_root_dir):
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    
    for filename in os.listdir(input_root_dir):
        reference_film, test_film, test_year, version = extract_film_info(filename)
        if all((reference_film, test_film, test_year, version is not None)):
            key = (reference_film, test_film)
            
            file_path = os.path.join(input_root_dir, filename)
            file_data = process_file(file_path)
            
            grouped_data[key][test_year][version] = file_data
    
    return grouped_data

def calculate_average_row(data):
    avg_row = {
        'reference_film': data[0]['reference_film'],
        'test_film': data[0]['test_film'],
        'test_year': data[0]['test_year'],
        'version_number': 'average'
    }
    numeric_columns = [col for col in data[0].keys() if col not in ['reference_film', 'test_film', 'test_year', 'version_number']]
    
    for col in numeric_columns:
        values = [row.get(col) for row in data if row.get(col) != 'N/A' and row.get(col) is not None]
        avg_row[col] = np.mean(values) if values else 'N/A'
    
    return avg_row

def generate_summary(film_pair_data):
    summary_data = []
    for (reference_film, test_film), years_data in film_pair_data.items():
        for test_year, versions_data in years_data.items():
            for version, features in versions_data.items():
                row = {
                    'reference_film': reference_film,
                    'test_film': test_film,
                    'test_year': test_year,
                    'version_number': version
                }
                row.update(features)
                summary_data.append(row)
    
    # Sort by version number
    summary_data.sort(key=lambda x: x['version_number'])
    
    # Add average row
    avg_row = calculate_average_row(summary_data)
    summary_data.append(avg_row)
    
    return summary_data

def main():
    os.makedirs(output_root_dir, exist_ok=True)
    grouped_data = process_files(input_root_dir)
    
    expected_columns = [
        'reference_film', 'test_film', 'test_year', 'version_number',
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
        
        output_file = f'summary_diff_elements_{reference_film}_{test_film}.csv'
        output_path = os.path.join(output_root_dir, output_file)
        df.to_csv(output_path, index=False)
        print(f"Saved {output_file}")

if __name__ == "__main__":
    main()