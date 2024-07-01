import os
import pandas as pd

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))

# Ensure the output directory exists
os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

# Function to extract reference_film, test_film, and test_year from the filename
def extract_film_info(filename):
    parts = filename.split('_')
    reference_film = parts[2]
    test_film = parts[4]
    test_year = parts[5]
    return reference_film, test_film, test_year

# Dictionary to hold dataframes grouped by (reference_film, test_film)
dataframes = {}

# Iterate over files in the input directory
for filename in os.listdir(INPUT_ROOT_DIR):
    if filename.endswith('.csv'):
        filepath = os.path.join(INPUT_ROOT_DIR, filename)
        reference_film, test_film, test_year = extract_film_info(filename)
        key = (reference_film, test_film, test_year)

        # Read the current file into a DataFrame
        df = pd.read_csv(filepath)
        
        # Add filename parts to the DataFrame
        df['reference_film'] = reference_film
        df['test_film'] = f"{test_film}_{test_year}"
        df['version_number'] = int(filename.split('_')[-1].replace('ver', '').replace('.csv', ''))

        # If key is already in dictionary, append data to the existing DataFrame
        if key in dataframes:
            dataframes[key] = pd.concat([dataframes[key], df], ignore_index=True)
        else:
            dataframes[key] = df

# Write aggregated DataFrames to the output directory
for (reference_film, test_film, test_year), df in dataframes.items():
    output_filename = f"summary_diff_genai_genai_{reference_film}_1981_{test_film}_{test_year}.csv"
    output_filepath = os.path.join(OUTPUT_ROOT_DIR, output_filename)
    
    # Reorder columns to match the desired format
    desired_columns = [
        'reference_film', 'test_film', 'version_number', 'characters', 'plot',
        'setting', 'themes', 'overall'
    ]
    df = df[desired_columns]
    
    df.to_csv(output_filepath, index=False)

print("Aggregation and file writing complete.")
