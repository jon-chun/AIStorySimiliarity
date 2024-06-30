import os
import json
import pandas as pd
import numpy as np
import re
import logging
from typing import List, Dict, Any
from collections import defaultdict
from fix_busted_json import repair_json as fix_busted_repair_json
from json_repair import repair_json
import logging

IMPUTE_VALUE = True
MIN_IMPUTE_PERCENT = 50
IMPUTE_METHOD = 'mean'  # Options: 'mean', 'median', 'mode'
ELEMENT_TYPES = ['characters','plot','setting','themes']

# Global configuration
MAX_SCRIPT_CT = 5
INPUT_FILE_TYPE = 'json'
OVERWRITE_FLAG = False

# Get the current working directory and set up paths
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts_summary'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_minor_json_errors(json_string):
    """Attempt to fix minor JSON errors."""
    # Remove trailing commas
    json_string = re.sub(r',\s*}', '}', json_string)
    json_string = re.sub(r',\s*]', ']', json_string)
    
    # Add missing quotes to keys
    json_string = re.sub(r'(\w+)(?=\s*:)', r'"\1"', json_string)
    
    # Replace single quotes with double quotes
    json_string = json_string.replace("'", '"')
    
    return json_string

def robust_json_parse(json_string):
    """Attempt to parse potentially malformed JSON strings."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        logging.warning("Initial JSON parsing failed. Attempting to repair...")
        try:
            fixed_json = fix_minor_json_errors(json_string)
            return json.loads(fixed_json)
        except:
            logging.warning("First repair attempt failed. Trying alternative methods...")
            try:
                fixed_json = fix_busted_repair_json(json_string)
                return json.loads(fixed_json)
            except:
                try:
                    fixed_json = repair_json(json_string)
                    return json.loads(fixed_json)
                except:
                    logging.error(f"Unable to parse JSON string: {json_string[:100]}...")
                    return {}

def process_file(file_path: str) -> Dict[str, Any]:
    logging.info(f"Processing file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.strip():
            logging.warning(f"Empty file: {file_path}")
            return {}
        data = robust_json_parse(content)
        # Extract only the similarity scores from top-level keys and convert to float if possible
        extracted_data = {}
        for k, v in data.items():
            if isinstance(v, dict) and 'similarity' in v:
                try:
                    extracted_data[k] = float(v['similarity'])
                except ValueError:
                    extracted_data[k] = v['similarity']
            else:
                extracted_data[k] = v
        logging.debug(f"Extracted data from {file_path}: {extracted_data}")
        return extracted_data
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")
        return {}
    
def process_subdir_files(subdir_path: str) -> List[Dict[str, Any]]:
    all_data = []
    for file in os.listdir(subdir_path):
        if file.endswith('.json'):
            file_path = os.path.join(subdir_path, file)
            data = process_file(file_path)
            if data:
                ref_film, test_film, element_type, version = extract_film_info(file)
                if all((ref_film, test_film, element_type, version)):
                    row = {
                        'reference_film': ref_film,
                        'test_film': test_film,
                        'version_number': int(version),
                        'element_type': element_type
                    }
                    row.update({f'{element_type}-{k}': v for k, v in data.items()})
                    all_data.append(row)
    return all_data

def process_files(input_root_dir: str, output_root_dir: str) -> None:
    for subdir in os.listdir(input_root_dir):
        subdir_path = os.path.join(input_root_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue
        
        logging.info(f"Processing subdirectory: {subdir}")
        
        # Process all files in the subdirectory
        all_data = process_subdir_files(subdir_path)
        
        if not all_data:
            logging.info(f"No data to process in {subdir}")
            continue
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Pivot the DataFrame to combine all element types
        df_pivot = df.pivot(index=['reference_film', 'test_film', 'version_number'], 
                            columns='element_type', 
                            values=[col for col in df.columns if col.startswith(('characters-', 'plot-', 'setting-', 'themes-'))])
        
        # Flatten column names
        df_pivot.columns = [f'{col[1]}-{col[0]}' for col in df_pivot.columns]
        df_pivot.reset_index(inplace=True)
        
        # Calculate averages for numeric columns only
        numeric_columns = df_pivot.select_dtypes(include=[np.number]).columns
        avg_row = df_pivot[numeric_columns].mean().to_frame().T
        avg_row['reference_film'] = df_pivot['reference_film'].iloc[0]
        avg_row['test_film'] = df_pivot['test_film'].iloc[0]
        avg_row['version_number'] = 'average'
        
        # Combine data and average
        df_final = pd.concat([df_pivot, avg_row], ignore_index=True)
        
        # Impute missing values if IMPUTE_VALUE is True
        if IMPUTE_VALUE:
            df_final = impute_missing_values(df_final)
        
        # Save the summary DataFrame
        ref_film = df_final['reference_film'].iloc[0]
        test_film = df_final['test_film'].iloc[0]
        output_file = f'summary_diff_elements_{ref_film}_{test_film}.csv'
        output_path = os.path.join(output_root_dir, output_file)
        save_summary_data(df_final, output_path)

def extract_film_info(filename):
    """Extract reference film, test film, element type, and version from filename."""
    match = re.search(r'scripts_(.+)_(.+)_elements-(.+)_ver(\d+)\.json', filename)
    if match:
        return match.groups()
    return None, None, None, None


def process_group(group: pd.DataFrame, ref_film: str, test_film: str, element_type: str) -> Dict[str, Any]:
    summary_row = {
        'reference_film': ref_film,
        'test_film': test_film,
        'element_type': element_type
    }
    
    for column in group.columns:
        if column.startswith(f'{element_type}-'):
            summary_row[column] = group[column].mean()
    
    return summary_row

def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Imputing missing values")
    for column in df.columns:
        if df[column].dtype in ['float64', 'int64']:
            valid_percent = df[column].notnull().mean() * 100
            if valid_percent >= MIN_IMPUTE_PERCENT:
                if IMPUTE_METHOD == 'mean':
                    impute_value = df[column].mean()
                elif IMPUTE_METHOD == 'median':
                    impute_value = df[column].median()
                elif IMPUTE_METHOD == 'mode':
                    impute_value = df[column].mode()[0]
                else:
                    logging.warning(f"Unknown imputation method: {IMPUTE_METHOD}. Using mean.")
                    impute_value = df[column].mean()
                
                df[column].fillna(impute_value, inplace=True)
                logging.info(f"Imputed {column} using {IMPUTE_METHOD} method")
        else:
            logging.info(f"Skipping imputation for non-numeric column: {column}")
    return df
  

def save_summary_data(df: pd.DataFrame, output_path: str) -> None:
    if os.path.exists(output_path):
        logging.info(f"Updating existing file: {output_path}")
        existing_df = pd.read_csv(output_path)
        df = pd.concat([existing_df, df]).drop_duplicates().reset_index(drop=True)
    
    df.to_csv(output_path, index=False)
    logging.info(f"Saved summary data to {output_path}")


def main():
    logging.info("Starting utility10_merge_score_diff_scripts.py")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)
    
    process_files(INPUT_ROOT_DIR, OUTPUT_ROOT_DIR)
    
    logging.info("Finished processing all files")

if __name__ == "__main__":
    main()