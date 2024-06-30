import os
import pandas as pd
import pickle
import re
from collections import defaultdict
import json
from fix_busted_json import repair_json as fix_busted_repair_json
from json_repair import repair_json

# Global configuration
INPUT_FILE_TYPE = 'csv'  # Change this to 'pkl' for pickle files

# Get the current working directory and set up paths
cwd = os.getcwd()
input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_elements'))
output_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_elements_summary'))

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
                print(f"Warning: Unable to parse JSON string: {json_string[:100]}...")
                return {}

def process_file(file_path):
    """Process a single file and return the data."""
    if INPUT_FILE_TYPE == 'pkl':
        with open(file_path, 'rb') as f:
            return pickle.load(f)
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
    # Get all files of the specified type and sort them
    files = sorted([f for f in os.listdir(input_root_dir) if f.endswith(f'.{INPUT_FILE_TYPE}')])
    
    # Group files by film combinations
    film_groups = defaultdict(list)
    for file in files:
        match = re.search(r'elements_(.+)_elements_(.+)_ver(\d+)', file)
        if match:
            reference_film, test_film, version = match.groups()
            film_groups[(reference_film, test_film)].append((file, int(version)))
    
    for (reference_film, test_film), group_files in film_groups.items():
        summary_df = pd.DataFrame()
        
        for file, version in sorted(group_files, key=lambda x: x[1]):
            data = process_file(os.path.join(input_root_dir, file))
            
            row = {
                'reference_film': reference_film,
                'test_film': test_film,
                'version_number': version
            }
            
            # Process each column
            for col, features in [
                ('characters', ['overall', 'backstory', 'strengths', 'weakness', 'psychology', 'beliefs', 'motivations', 'social_dynamics']),
                ('plot', ['overall', 'protagonist_introduction', 'inciting_incident', 'rising_action', 'climax', 'resolution', 'consequences', 'final_outcome', 'loose_ends', 'subplots']),
                ('setting', ['overall', 'time_period', 'geographical_location', 'cultural_context', 'social_class', 'ideology_and_beliefs', 'economic_and_political_context']),
                ('themes', ['overall', 'main_theme', 'secondary_themes', 'tertiary_themes', 'resolution_main_theme', 'resolution_secondary_themes', 'resolution_tertiary_themes'])
            ]:
                if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                    col_data = data['data'][0][0].get(col, {})
                    for feature in features:
                        if feature in col_data:
                            row[f'{col}-{feature}'] = col_data[feature].get('similarity')
                else:
                    print(f"Warning: Unexpected data structure in file {file}")
            
            summary_df = pd.concat([summary_df, pd.DataFrame([row])], ignore_index=True)
        
        # Save the summary DataFrame to CSV
        output_file = f'summary_diff_elements_{reference_film}_{test_film}.csv'
        output_path = os.path.join(output_root_dir, output_file)
        summary_df.to_csv(output_path, index=False)
        print(f"Saved {output_file}")

def main():
    # Ensure output directory exists
    os.makedirs(output_root_dir, exist_ok=True)
    
    process_files(input_root_dir, output_root_dir)

if __name__ == "__main__":
    main()