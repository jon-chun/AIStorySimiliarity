import os
import json
import time
import pandas as pd
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
    SLEEP_SECONDS = 5

MODEL_NAME = 'gpt-3.5-turbo' # 'gpt-4o'
# 'gpt-3.5-turbo is limited to 16k tokens ~12kb plain text file 
# 'gpt-4o' has 128k tokens window
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 0.5

# Set to True if you want to reprocess all films, else make for more efficient restarting without reprocessing
OVERWRITE_FLAG = False  

# Max retries to parse OpenAI API response into Python Dictionary
MAX_RETRY_DICT_PARSE = 3

# Configure how many iterations to run
SAMPLE_SIZE = 3

INPUT_ROOT_DIR = os.path.join('.','data', 'film_narrative_elements')
OUTPUT_ROOT_DIR = os.path.join('.','data', 'score_diff_elements')
ELEMENTS_LIST = ['characters', 'plot', 'setting', 'themes']
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

"""
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
        exit()

    prompt_reference_text = f"\n\n###REFERENCE_ELEMENT\n\n{reference_element_string}\n\n"
    prompt_test_string = f"###TEST_ELEMENT:\n\n{test_element_string}\n\n"

    full_prompt = prompt_reference_text + prompt_test_string + prompt_compare

    # print(f"\n\n\n\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{full_prompt}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n\n\n")

    # log_error.info(f"Constructed full prompt: {full_prompt[:50]}...")

    response = call_openai(full_prompt)
    # print(f"type(response): {type(response)}")
    time.sleep(SLEEP_SECONDS)
    return 

def get_story_distance(elements_dict, reference_key, test_key):
    elements_distances_dict = {}
    for element in ELEMENTS_LIST:
        reference_element = elements_dict.get(reference_key, {}).get(element, "")
        test_element = elements_dict.get(test_key, {}).get(element, "")
        
        if not reference_element or not test_element:
            print(f"Warning: Empty data for {element} in {reference_key} or {test_key}")
            elements_distances_dict[element] = 0
        else:
            print(f'  IN get_story_distance() about to call get_element_pair_distance(element={element})')
            response_dict = get_element_pair_distance(reference_element, test_element, element)
            elements_distances_dict[element] = response_dict
            
    
    for key, value in elements_distances_dict.items():
        print(f"   key={key}: value={value}\n\n")
    time.sleep(SLEEP_SECONDS)
    elements_distances_dict['overall'] = sum(elements_distances_dict.values())
    return elements_distances_dict
"""
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
    for element in ELEMENTS_LIST:
        reference_element = elements_dict.get(reference_key, {}).get(element, "")
        test_element = elements_dict.get(test_key, {}).get(element, "")
        
        if not reference_element or not test_element:
            print(f"Warning: Empty data for {element} in {reference_key} or {test_key}")
            elements_distances_dict[element] = {'similarity': 0, 'reasoning': 'Insufficient data'}
        else:
            print(f'  IN get_story_distance() about to call get_element_pair_distance(element={element})')
            response_dict = get_element_pair_distance(reference_element, test_element, element)
            if response_dict is not None:
                elements_distances_dict[element] = response_dict
            else:
                elements_distances_dict[element] = {'similarity': 0, 'reasoning': 'Error in processing'}
    
    for key, value in elements_distances_dict.items():
        print(f"   key={key}: value={value}\n\n")
    time.sleep(SLEEP_SECONDS)
    
    # Calculate overall similarity
    overall_similarity = sum(value.get('similarity', 0) for value in elements_distances_dict.values() if isinstance(value, dict))
    elements_distances_dict['overall'] = {'similarity': overall_similarity, 'reasoning': 'Aggregate of all element similarities'}
    
    return elements_distances_dict

"""
def main():
    elements_all_films_dict = get_all_film_elements(INPUT_ROOT_DIR)
    # print("JSON.DUMPS(elements_all_films_dict)")
    print(json.dumps(elements_all_films_dict, indent=4))

    film_keys = list(elements_all_films_dict.keys())
    print("Film keys:", film_keys)

    for film_key_now in film_keys:
        print(json.dumps(elements_all_films_dict[film_key_now],indent=4))
        print('\n\n\n')

    print(f"Reference film data structure:")
    # for element, data in elements_all_films_dict.get(REFERENCE_FILM, {}).items():
    #     print(f"{element}: {data[:100]}...")  # Print first 100 characters of each element

    element_distances_all = []
    # film_keys = list(elements_all_films_dict.keys())
    
    for reference_key, test_key in combinations(film_keys, 2):
        if reference_key == REFERENCE_FILM or test_key == REFERENCE_FILM:
            reference_key, test_key = (REFERENCE_FILM, test_key) if reference_key == REFERENCE_FILM else (REFERENCE_FILM, reference_key)
            try:
                print(f"Processing: {reference_key} vs {test_key}")
                print(f' CALLING get_story_distance with ref_key: {reference_key}, test_key: {test_key}')
                distances = get_story_distance(elements_all_films_dict, reference_key, test_key)
                row = {
                    'reference_film': reference_key,
                    'test_film': test_key,
                    **distances
                }
                element_distances_all.append(row)
            except Exception as e:
                print(f"Error processing films {reference_key} and {test_key}: {str(e)}")
                print(f"Reference data: {elements_all_films_dict.get(reference_key)}")
                print(f"Test data: {elements_all_films_dict.get(test_key)}")

    element_distances_all_df = pd.DataFrame(element_distances_all)
    
    output_file = os.path.join(OUTPUT_ROOT_DIR, 'element_distances_all.csv')
    element_distances_all_df.to_csv(output_file, index=False)
    print(f"Element distances saved to {output_file}")
    print(element_distances_all_df)


""";

def main():
    elements_all_films_dict = get_all_film_elements(INPUT_ROOT_DIR)
    # print(json.dumps(elements_all_films_dict, indent=4))

    film_keys = list(elements_all_films_dict.keys())
    print("Film keys:", film_keys)

    for film_key_now in film_keys:
        print(json.dumps(elements_all_films_dict[film_key_now], indent=4))
        print('\n\n\n')

    print(f"Reference film data structure:")

    element_distances_all = []
    
    for reference_key, test_key in combinations(film_keys, 2):
        if reference_key == REFERENCE_FILM or test_key == REFERENCE_FILM:
            reference_key, test_key = (REFERENCE_FILM, test_key) if reference_key == REFERENCE_FILM else (REFERENCE_FILM, reference_key)
            try:
                print(f"Processing: {reference_key} vs {test_key}")
                print(f' CALLING get_story_distance with ref_key: {reference_key}, test_key: {test_key}')
                distances = get_story_distance(elements_all_films_dict, reference_key, test_key)
                
                # Create and save the individual comparison DataFrame
                individual_comparison_df = pd.DataFrame([distances])
                individual_output_file = os.path.join(OUTPUT_ROOT_DIR, f"compare_elements_{reference_key}_{test_key}.csv")
                individual_comparison_df.to_csv(individual_output_file, index=False)
                print(f"Individual comparison saved to {individual_output_file}")
                
                # Add to the overall distances list
                row = {
                    'reference_film': reference_key,
                    'test_film': test_key,
                    **distances
                }
                element_distances_all.append(row)
            except Exception as e:
                print(f"Error processing films {reference_key} and {test_key}: {str(e)}")
                print(f"Reference data: {elements_all_films_dict.get(reference_key)}")
                print(f"Test data: {elements_all_films_dict.get(test_key)}")

    # Create and save the overall distances DataFrame
    element_distances_all_df = pd.DataFrame(element_distances_all)
    overall_output_file = os.path.join(OUTPUT_ROOT_DIR, 'element_distances_all.csv')
    element_distances_all_df.to_csv(overall_output_file, index=False)
    print(f"Overall element distances saved to {overall_output_file}")
    # print(element_distances_all_df)

if __name__ == "__main__":
    main()