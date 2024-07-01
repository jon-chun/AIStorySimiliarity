import os
import pandas as pd
import pickle
import re

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))

FILE_PATTERN = r'similarity-by-score_genaigenai_(.+?)_(.+?)_(\d{4})_ver(\d+)\.pkl'

def extract_similarity_values(data, element):
    if element not in data:
        print(f"Warning: '{element}' not found in data.")
        return {}
    
    similarity_by_features = data[element].get('similarity_by_features', {})
    extracted_values = {f"{element}_{key}": value for key, value in similarity_by_features.items()}
    extracted_values[f"{element}_similarity_overall"] = data[element].get('similarity_overall', 0)
    return extracted_values

def process_pkl_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    
    # Log the structure of the data for debugging
    print(f"Processing file: {file_path}")
    for top_key, top_value in data.items():
        print(f"Top-level key: {top_key}")
        if isinstance(top_value, dict):
            print(f"Second-level keys: {list(top_value.keys())}")
            result = {}
            for element in ['characters', 'plot', 'setting', 'themes']:
                if element in top_value:
                    result.update(extract_similarity_values(top_value, element))
            result['filename'] = os.path.basename(file_path)
            return result
    return {}

def main():

    pattern = re.compile(FILE_PATTERN)
    grouped_files = {}

    # Group files by the unique combination of reference_film and test_film
    for root, _, files in os.walk(INPUT_ROOT_DIR):
        for file in files:
            if file.endswith('.pkl'):
                match = pattern.match(file)
                if match:
                    reference_film, test_film, year, version = match.groups()
                    key = f"{reference_film}_{test_film}"
                    if key not in grouped_files:
                        grouped_files[key] = []
                    grouped_files[key].append(os.path.join(root, file))

    # Process each group of files and save the results
    for key, file_paths in grouped_files.items():
        summary_data = []
        for file_path in file_paths:
            similarity_values = process_pkl_file(file_path)
            if similarity_values:  # Only append if there's valid data
                summary_data.append(similarity_values)

        if summary_data:
            df = pd.DataFrame(summary_data)
            output_file = os.path.join(OUTPUT_ROOT_DIR, f"summary_genai_scores_{key}.csv")
            df.to_csv(output_file, index=False)
            print(f"Saved {output_file}")
        else:
            print(f"No data to save for {key}")

if __name__ == "__main__":
    main()
