import os
import json
import pandas as pd
import re

cwd = os.getcwd()
dir_name = 'verify_claude35sonnet'
subdir_name = 'verify_claude35sonnet_ranking'
dir_name = 'verify_gpt4o'
subdir_name = 'verify_gpt4o_ranking'

input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', dir_name, subdir_name))
output_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'verify_summary'))

def merge_verify_ranking_files(input_root_dir, output_root_dir):
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)
    
    # Pattern to extract model_name, test_film, and version_number from filenames
    pattern = re.compile(r"verify_(?P<model_name>.+)_ranking_(?P<test_film>.+)_ver(?P<version_number>\d+)\.json")

    # Dictionary to group dataframes by (model_name, test_film)
    grouped_data = {}

    # Process all files in the input directory
    print(f"Searching for files in: {input_root_dir}")
    for file in os.listdir(input_root_dir):
        print(f"Found file: {file}")
        match = pattern.match(file)
        if file.endswith('.json'):
            if match:
                print(f"Processing file: {file}")
                model_name = match.group('model_name')
                test_film = match.group('test_film')
                version_number = match.group('version_number')

                file_path = os.path.join(input_root_dir, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Convert the JSON data to a DataFrame
                df = pd.DataFrame.from_dict(data, orient='index')
                df['rank'] = df.index
                df = df.reset_index(drop=True)

                # Add new columns
                df.insert(0, 'model_name', model_name)
                df.insert(1, 'test_film', test_film)
                df.insert(2, 'version_number', version_number)

                # Append to the existing list of dataframes for this (model_name, test_film)
                key = (model_name, test_film)
                if key not in grouped_data:
                    grouped_data[key] = []
                grouped_data[key].append(df)
            else:
                print(f"File {file} doesn't match the expected pattern")

    if not grouped_data:
        print("No files were successfully processed.")

    # Write grouped dataframes to CSV files
    for (model_name, test_film), dfs in grouped_data.items():
        combined_df = pd.concat(dfs, ignore_index=True)
        output_filename = f"summary_verify_ranking_{model_name}_{test_film}.csv"
        output_file_path = os.path.join(output_root_dir, output_filename)
        combined_df.to_csv(output_file_path, index=False)

if __name__ == "__main__":
    merge_verify_ranking_files(input_root_dir, output_root_dir)