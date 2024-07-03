import os
import json
import pandas as pd
import re

cwd = os.getcwd()
input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'verify_claude35sonnet', 'verify_claude35sonnet_facts-reasoning'))
output_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'verify_summary'))


def merge_verify_files(input_root_dir, output_root_dir):
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)
    
    # Pattern to extract model_name and test_film from filenames
    pattern = re.compile(r"verify_(?P<model_name>.+)_facts-reasoning_(?P<test_film>.+)_ver\d+\.json")

    # Dictionary to group dataframes by (model_name, test_film)
    grouped_data = {}

    # Crawl through all files in the input directory
    for root, _, files in os.walk(input_root_dir):
        for file in files:
            print(f"PROCESSING: file: {file}")
            if file.endswith('.json'):
                print(f'PROCESSSING: file: {file}')
                match = pattern.match(file)
                if match:
                    model_name = match.group('model_name')
                    test_film = match.group('test_film')
                    key = (model_name, test_film)

                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    # Convert the JSON data to a DataFrame
                    df = pd.DataFrame([data])

                    # Append to the existing list of dataframes for this (model_name, test_film)
                    if key not in grouped_data:
                        grouped_data[key] = []
                    grouped_data[key].append(df)

    # Write grouped dataframes to CSV files
    for (model_name, test_film), dfs in grouped_data.items():
        combined_df = pd.concat(dfs, ignore_index=True)
        output_filename = f"summary_verify_{model_name}_{test_film}.csv"
        output_file_path = os.path.join(output_root_dir, output_filename)
        combined_df.to_csv(output_file_path, index=False)

if __name__ == "__main__":

    merge_verify_files(input_root_dir, output_root_dir)
