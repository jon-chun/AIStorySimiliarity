import os
import json
import pandas as pd
import logging
from itertools import combinations
from similarity_customizations.similarity_weights import (
    characters_weights_dict,
    plot_weights_dict,
    setting_weights_dict,
    themes_weights_dict,
    element_weights_dict
)
from fix_busted_json import repair_json as fix_busted_repair_json
from json_repair import repair_json

INPUT_ROOT_DIR = os.path.join('data', 'film_narrative_elements')
OUTPUT_ROOT_DIR = os.path.join('data', 'score_diff_elements')
PROMPT_DIR = os.path.join('prompts')
ELEMENTS_LIST = ['characters', 'plot', 'setting', 'themes']
REFERENCE_FILM = 'elements_raiders-of-the-lost-ark_1981'

def log_error(message, exception=None):
    error_message = f"ERROR: {message}"
    if exception:
        error_message += f"\n{str(exception)}"
    print(error_message)
    logging.error(error_message)

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
    

def get_all_film_elements(input_dir):
    elements_all_films_dict = {}
    for film_dir in os.listdir(input_dir):
        film_path = os.path.join(input_dir, film_dir)
        if os.path.isdir(film_path):
            film_elements = {}
            for element in ELEMENTS_LIST:
                element_file = f"{film_dir}_{element}.json"
                element_path = os.path.join(film_path, element_file)
                if os.path.exists(element_path):
                    film_elements[element] = read_json_file(element_path)
            elements_all_films_dict[film_dir] = film_elements
    return elements_all_films_dict

def compare_nested_dict(dict1, dict2, prefix=''):
    distance = 0
    all_keys = set(dict1.keys()) | set(dict2.keys())
    for key in all_keys:
        val1 = dict1.get(key, '')
        val2 = dict2.get(key, '')
        if isinstance(val1, dict) and isinstance(val2, dict):
            distance += compare_nested_dict(val1, val2, prefix=f"{prefix}{key}_")
        else:
            distance += abs(len(str(val1)) - len(str(val2)))
    return distance

def get_element_pair_distance(reference_element_dict, test_element_dict, weights_dict):
    total_distance = 0
    for main_key, main_weight in weights_dict.items():
        ref_value = reference_element_dict.get(main_key, {})
        test_value = test_element_dict.get(main_key, {})
        if isinstance(ref_value, dict) and isinstance(test_value, dict):
            distance = compare_nested_dict(ref_value, test_value)
        else:
            distance = abs(len(str(ref_value)) - len(str(test_value)))
        total_distance += distance * (main_weight / 100)
    return total_distance

def get_story_distance(elements_dict, reference_key, test_key):
    distances = {}
    weights_dicts = {
        'characters': characters_weights_dict,
        'plot': plot_weights_dict,
        'setting': setting_weights_dict,
        'themes': themes_weights_dict
    }
    
    for element in ELEMENTS_LIST:
        reference_element = elements_dict.get(reference_key, {}).get(element, {})
        test_element = elements_dict.get(test_key, {}).get(element, {})
        
        if not reference_element or not test_element:
            print(f"Warning: Empty data for {element} in {reference_key} or {test_key}")
            distances[element] = 0
        else:
            distances[element] = get_element_pair_distance(reference_element, test_element, weights_dicts[element])
    
    overall_distance = sum(distances[element] * (element_weights_dict[element] / 100) for element in ELEMENTS_LIST)
    distances['overall'] = overall_distance
    
    return distances

def main():
    logging.basicConfig(filename='story_similarity.log', level=logging.DEBUG)
    elements_all_films_dict = get_all_film_elements(INPUT_ROOT_DIR)
    
    print("Film keys:", list(elements_all_films_dict.keys()))
    print(f"Reference film data structure:")
    for element, data in elements_all_films_dict.get(REFERENCE_FILM, {}).items():
        print(f"{element}: {json.dumps(data, indent=2)[:500]}...")  # Print first 500 characters of each element
    
    element_distances_all = []
    film_keys = list(elements_all_films_dict.keys())
    
    for reference_key, test_key in combinations(film_keys, 2):
        if reference_key == REFERENCE_FILM or test_key == REFERENCE_FILM:
            reference_key, test_key = (REFERENCE_FILM, test_key) if reference_key == REFERENCE_FILM else (REFERENCE_FILM, reference_key)
            try:
                print(f"Processing: {reference_key} vs {test_key}")
                distances = get_story_distance(elements_all_films_dict, reference_key, test_key)
                row = {
                    'reference_film': reference_key,
                    'test_film': test_key,
                    **distances
                }
                element_distances_all.append(row)
            except Exception as e:
                log_error(f"Error processing films {reference_key} and {test_key}: {str(e)}")
                log_error(f"Reference data: {json.dumps(elements_all_films_dict.get(reference_key), indent=2)[:500]}...")
                log_error(f"Test data: {json.dumps(elements_all_films_dict.get(test_key), indent=2)[:500]}...")

    element_distances_all_df = pd.DataFrame(element_distances_all)
    
    output_file = os.path.join(OUTPUT_ROOT_DIR, 'element_distances_all.csv')
    element_distances_all_df.to_csv(output_file, index=False)
    print(f"Element distances saved to {output_file}")
    print(element_distances_all_df)

if __name__ == "__main__":
    main()