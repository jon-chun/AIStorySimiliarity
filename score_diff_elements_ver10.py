import os
import json
import time
import pandas as pd
import pickle
from itertools import combinations
from typing import List, Dict, Tuple, Optional
from openai import OpenAI

from fix_busted_json import repair_json as fix_busted_repair_json
from json_repair import repair_json

from similarity_customizations.similarity_weights import (
    characters_weights_dict,
    plot_weights_dict,
    setting_weights_dict,
    themes_weights_dict,
    element_weights_dict
)

from prompts.prompts_compare_element_characters import prompt_compare_characters
from prompts.prompts_compare_element_plot import prompt_compare_plot
from prompts.prompts_compare_element_setting import prompt_compare_setting
from prompts.prompts_compare_element_themes import prompt_compare_themes

import logging

# Set up logging
logging.basicConfig(filename='error.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(message, exception=None, TERMINAL_TOO=True):
    error_message = f"ERROR: {message}"
    if exception:
        error_message += f"\n{str(exception)}"
    
    # Always log to file
    logging.error(error_message)
    
    # Print to terminal only if TERMINAL_TOO is True
    if TERMINAL_TOO:
        print(error_message)

# SETUP OPENAI =====

# Set the OpenAI API Key in the command line shell

# 1. LINUX CLI: export OPENAI_API_KEY="your_openai_api_key"
# 2. WIN11 PowerShell: $env:OPENAI_API_KEY="your_openai_api_key"
#                   echo $env:OPENAI_API_KEY
# 3. WIN11 Command Terminal: set OPENAI_API_KEY=your_openai_api_key
#                         echo %OPENAI_API_KEY%

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    SLEEP_SECONDS = 1

MODEL_NAME = 'gpt-3.5-turbo' # 'gpt-4o'
# 'gpt-3.5-turbo is limited to 16k tokens ~12kb plain text file 
# 'gpt-4o' has 128k tokens window
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.5

# Set to True if you want to reprocess all films, else make for more efficient restarting without reprocessing
OVERWRITE_FLAG = False  

# Max retries to parse OpenAI API response into Python Dictionary
MAX_RETRY_DICT_PARSE = 30

# Configure how many iterations to run
SAMPLE_SIZE = 30

INPUT_ROOT_DIR = os.path.join('.','data', 'film_narrative_elements')
OUTPUT_ROOT_DIR = os.path.join('.','data', 'score_diff_elements')
ELEMENTS_LIST = ['characters', 'plot', 'setting', 'themes']
ELEMENTS_LIST = ['characters']
REFERENCE_FILM = 'elements_raiders-of-the-lost-ark_1981'


def call_openai(prompt_str: str) -> Optional[Dict]:

    try:
        for attempt in range(MAX_RETRY_DICT_PARSE):

            log_error(f"Sending prompt to OpenAI: {prompt_str}\n", TERMINAL_TOO=False)
            completion = openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_str,
                    }
                ],
                model=MODEL_NAME,
                temperature=DEFAULT_TEMPERATURE,
                top_p=DEFAULT_TOP_P,
                response_format={ "type": "json_object" },
            )

            time.sleep(SLEEP_SECONDS)
            print(f'  PAUSE 5 Seconds between OpenAI API calls')
            response = completion.choices[0].message.content
            log_error(f"Received response from OpenAI: {response}")

            
            try:
                # Two options to try to repair malformed JSON string response
                # A. https://github.com/Qarj/fix-busted-json 202404 27s
                # B. https://github.com/mangiucugna/json_repair/ 20040627 429s
                try:
                    response_fix_json_pass1 = fix_busted_repair_json(response) # Attempt to repair malformed JSON string
                except:
                    response_fix_json_pass1 = response
                try:
                    response_fix_json_pass2 = repair_json(response_fix_json_pass1)
                except:
                    response_fix_json_pass2 = response_fix_json_pass1

                response_dict = json.loads(response_fix_json_pass2)
                log_error(f"Successfully parsed response to dictionary on attempt {attempt + 1}")
                return response_dict
            except json.JSONDecodeError as parse_error:
                log_error(f"Attempt {attempt + 1} failed to parse response to dictionary: {parse_error}", level="error")
                if attempt == MAX_RETRY_DICT_PARSE - 1:
                    log_error("Max retry attempts reached. Returning None.", level="error")
                    return None

    except Exception as e:
        log_error(f"Error in API call: {e}", level="error")
        return None

def version_filename(base_name: str, version: int) -> str:
    """Generate a versioned filename."""
    name, ext = os.path.splitext(base_name)
    return f"{name}_ver{version}{ext}"


def clean_string(s):
    return ''.join(char for char in s if char.isalnum())

def clean_json_data(data):
    if isinstance(data, list):
        if len(data) == 1:
            return clean_json_data(data[0])
        return data
    if isinstance(data, dict):
        return data
    return {}

def repair_json_string(response):
    try:
        # First, try to parse it as is
        json.loads(response)
        return response
    except json.JSONDecodeError:
        # If that fails, try the repair functions
        try:
            response_fix_json_pass1 = fix_busted_repair_json(response)
        except Exception as e:
            response_fix_json_pass1 = response
            log_error(f"Warning: fix_busted_repair_json failed: {e}")
        try:
            response_fix_json_pass2 = repair_json(response_fix_json_pass1)
        except Exception as e:
            response_fix_json_pass2 = response_fix_json_pass1
            log_error(f"Warning: repair_json failed: {e}")
        return response_fix_json_pass2

def read_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            raw_data = file.read()
        repaired_data = repair_json_string(raw_data)
        data = json.loads(repaired_data)
        return clean_json_data(data)
    except Exception as e:
        log_error(f"Error reading {filepath}: {e}")
        # If JSON parsing fails, try to read it as a Python literal
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = eval(file.read())
            return clean_json_data(data)
        except Exception as e2:
            log_error(f"Error reading {filepath} as Python literal: {e2}")
            return {}

def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def get_all_film_elements(input_dir):
    elements_all_films_dict = {}
    for film_dir in os.listdir(input_dir):
        film_path = os.path.join(input_dir, film_dir)
        if os.path.isdir(film_path):
            film_elements = {}
            for element in ELEMENTS_LIST:
                element_file = f"{film_dir}_{element}.json"
                element_path = os.path.join(film_path, element_file)
                print(f"  Looking for element filepath: {element_path}")
                if os.path.exists(element_path):
                    print(f"  FOUND IT!")
                    film_element_text = read_text_file(element_path)
                    # print(film_element_text)
                    film_elements[element] = film_element_text
                else:
                    print(f"\n\n>>>MISSING!!! Could not find element_path: {element_path}<<<\n\n")
            elements_all_films_dict[film_dir] = film_elements
    
    # If you want to save the dictionary as a JSON file, you can use:
    # with open('elements_all_films.json', 'w') as f:
    #     json.dump(elements_all_films_dict, f, indent=4)
    
    return elements_all_films_dict

def get_element_pair_distance(reference_element_string, test_element_string, element):
    if element == 'characters':
        prompt_compare = prompt_compare_characters
    elif element == 'plot':
        prompt_compare = prompt_compare_plot
    elif element == 'setting':
        prompt_compare = prompt_compare_setting
    elif element == 'themes':
        prompt_compare = prompt_compare_themes
    else:
        print(f"ERROR: Illegal value for element: {element}")
        return None

    prompt_reference_text = f"\n\n###REFERENCE_ELEMENT\n\n{reference_element_string}\n\n"
    prompt_test_string = f"###TEST_ELEMENT:\n\n{test_element_string}\n\n"

    full_prompt = prompt_reference_text + prompt_test_string + prompt_compare

    response = call_openai(full_prompt)
    time.sleep(SLEEP_SECONDS)
    return response  # This now returns the dictionary from call_openai

def get_story_distance(elements_dict, reference_key, test_key):
    elements_distances_dict = {}
    overall_similarities = []

    for element in ELEMENTS_LIST:
        reference_element = elements_dict.get(reference_key, {}).get(element, "")
        test_element = elements_dict.get(test_key, {}).get(element, "")
        
        if not reference_element or not test_element:
            print(f"Warning: Empty data for {element} in {reference_key} or {test_key}")
            elements_distances_dict[element] = {'similarity': 0, 'reasoning': 'Insufficient data'}
        else:
            print(f'  IN get_story_distance() about to call get_element_pair_distance(element={element})')
            response_dict = get_element_pair_distance(reference_element, test_element, element)
            if response_dict is not None and 'overall' in response_dict:
                elements_distances_dict[element] = response_dict
                overall_similarities.append(response_dict['overall']['similarity'])
            else:
                elements_distances_dict[element] = {'similarity': 0, 'reasoning': 'Error in processing'}
    
    for key, value in elements_distances_dict.items():
        print(f"   key={key}: value={value}\n\n")
    time.sleep(SLEEP_SECONDS)
    
    # Calculate overall similarity
    if overall_similarities:
        overall_similarity = sum(overall_similarities) / len(overall_similarities)
        overall_reasoning = 'Average of element overall similarities'
    else:
        overall_similarity = 0
        overall_reasoning = 'No valid element similarities found'
    
    elements_distances_dict['overall'] = {
        'similarity': round(overall_similarity, 2),
        'reasoning': overall_reasoning
    }
    
    return elements_distances_dict


def save_dataframe(df, base_path):
    """Save DataFrame as both CSV and pickle files."""
    csv_path = f"{base_path}.csv"
    pkl_path = f"{base_path}.pkl"
    
    df.to_csv(csv_path, index=False)
    with open(pkl_path, 'wb') as f:
        pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"Data saved to {csv_path} and {pkl_path}")

# Update compare_films function to use save_dataframe
def compare_films(elements_all_films_dict: Dict, reference_key: str, test_key: str, version: int) -> Optional[Dict]:
    """Compare two films and save the results if the output doesn't already exist."""
    base_filename = f"compare_elements_{reference_key}_{test_key}"
    output_file = os.path.join(OUTPUT_ROOT_DIR, version_filename(base_filename, version))
    
    if os.path.exists(f"{output_file}.csv") or os.path.exists(f"{output_file}.pkl"):
        print(f"Skipping existing comparison: {reference_key} vs {test_key} (Version {version})")
        return None

    try:
        print(f"Processing: {reference_key} vs {test_key} (Version {version})")
        distances = get_story_distance(elements_all_films_dict, reference_key, test_key)
        
        # Create and save the individual comparison DataFrame
        individual_comparison_df = pd.DataFrame([distances])
        save_dataframe(individual_comparison_df, output_file)
        print(f"Individual comparison saved to {output_file}")
        
        return {
            'reference_film': reference_key,
            'test_film': test_key,
            'version': version,
            **distances
        }
    except Exception as e:
        log_error(f"Error processing films {reference_key} and {test_key}: {str(e)}")
        log_error(f"Reference data: {elements_all_films_dict.get(reference_key)}")
        log_error(f"Test data: {elements_all_films_dict.get(test_key)}")
        return None

# Update load_existing_comparisons function to try loading pickle file first
def load_existing_comparisons(version: int) -> List[Dict]:
    """Load existing comparisons for a specific version, preferring pickle files."""
    base_filename = version_filename('element_distances_all', version)
    pkl_file = os.path.join(OUTPUT_ROOT_DIR, f"{base_filename}.pkl")
    csv_file = os.path.join(OUTPUT_ROOT_DIR, f"{base_filename}.csv")
    
    if os.path.exists(pkl_file):
        with open(pkl_file, 'rb') as f:
            return pickle.load(f).to_dict('records')
    elif os.path.exists(csv_file):
        return pd.read_csv(csv_file).to_dict('records')
    return []

def get_latest_version_and_film(output_dir: str) -> Tuple[int, Optional[str]]:
    """
    Find the latest version number and the last processed film.
    Returns a tuple of (version_number, last_processed_film).
    If no files found, returns (0, None).
    """
    files = sorted(os.listdir(output_dir))
    latest_version = -1
    last_film = None
    
    for file in reversed(files):
        if file.startswith("compare_elements_") and file.endswith(".pkl"):
            parts = file.split("_")
            if len(parts) >= 4:
                try:
                    version = int(parts[-1].split(".")[0][3:])  # Extract version number
                    if version > latest_version:
                        latest_version = version
                        last_film = "_".join(parts[2:-1])  # Join film name parts
                        break
                except ValueError:
                    continue
    
    return max(0, latest_version), last_film

def main():
    print("Starting main function")
    
    if not os.path.exists(INPUT_ROOT_DIR):
        print(f"Error: INPUT_ROOT_DIR does not exist: {INPUT_ROOT_DIR}")
        return
    
    if not os.path.exists(OUTPUT_ROOT_DIR):
        print(f"Creating OUTPUT_ROOT_DIR: {OUTPUT_ROOT_DIR}")
        os.makedirs(OUTPUT_ROOT_DIR)
    
    elements_all_films_dict = get_all_film_elements(INPUT_ROOT_DIR)
    if not elements_all_films_dict:
        print("Error: No film elements found")
        return
    
    film_keys = sorted(elements_all_films_dict.keys())
    print(f"Found {len(film_keys)} films: {film_keys}")
    
    if REFERENCE_FILM not in film_keys:
        print(f"Error: REFERENCE_FILM '{REFERENCE_FILM}' not found in film_keys")
        return
    
    latest_version, last_processed_film = get_latest_version_and_film(OUTPUT_ROOT_DIR)
    start_version = latest_version if last_processed_film else 0
    start_film_index = film_keys.index(last_processed_film) + 1 if last_processed_film in film_keys else 0
    
    print(f"Resuming from version {start_version}, film index {start_film_index}")
    
    for version in range(start_version, start_version + SAMPLE_SIZE):
        print(f"Processing version {version}")
        element_distances_all = load_existing_comparisons(version)
        existing_comparisons = {(row['reference_film'], row['test_film']) for row in element_distances_all}
        
        comparisons_made = 0
        for i, test_key in enumerate(film_keys):
            if i < start_film_index and version == start_version:
                continue  # Skip already processed films in the first iteration
            
            if test_key != REFERENCE_FILM:
                reference_key = REFERENCE_FILM
                if (reference_key, test_key) not in existing_comparisons:
                    print(f"Comparing {reference_key} and {test_key}")
                    result = compare_films(elements_all_films_dict, reference_key, test_key, version)
                    if result:
                        element_distances_all.append(result)
                        comparisons_made += 1
        
        print(f"Made {comparisons_made} new comparisons in version {version}")

        # Create and save the overall distances DataFrame
        if element_distances_all:
            element_distances_all_df = pd.DataFrame(element_distances_all)
            overall_output_file = os.path.join(OUTPUT_ROOT_DIR, version_filename('element_distances_all', version))
            save_dataframe(element_distances_all_df, overall_output_file)
            print(f"Overall element distances (Version {version}) saved")
        else:
            log_error(f"No valid comparisons were made in version {version}")
        
        start_film_index = 0  # Reset for next versions

    print("Main function completed")

if __name__ == "__main__":
    main()