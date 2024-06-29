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
        response_fix_json_pass1 = fix_busted_repair_json(response) # Attempt to repair malformed JSON string
    except Exception as e:
        response_fix_json_pass1 = response
        print(f"Warning: fix_busted_repair_json failed: {e}")
    try:
        response_fix_json_pass2 = repair_json(response_fix_json_pass1)
    except Exception as e:
        response_fix_json_pass2 = response_fix_json_pass1
        print(f"Warning: repair_json failed: {e}")
    return response_fix_json_pass2

def read_json_file(filepath):
    try:
        with open(filepath, 'r') as file:
            raw_data = file.read()
        repaired_data = repair_json_string(raw_data)
        data = json.loads(repaired_data)
        return clean_json_data(data)
    except (IOError, json.JSONDecodeError) as e:
        log_error(f"Error reading {filepath}: {e}")
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

def get_element_pair_distance(reference_element_dict, test_element_dict, weights_dict):
    distance = 0
    for feature, weight in weights_dict.items():
        ref_value = str(reference_element_dict.get(feature, ''))
        test_value = str(test_element_dict.get(feature, ''))
        if not ref_value and not test_value:
            continue
        feature_distance = abs(len(ref_value) - len(test_value))
        distance += feature_distance * (weight / 100)
    return distance

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
            print(f"Reference element: {reference_element}")
            print(f"Test element: {test_element}")
            distances[element] = 0
        else:
            distances[element] = get_element_pair_distance(reference_element, test_element, weights_dicts[element])
    
    overall_distance = sum(distances[element] * (element_weights_dict[element] / 100) for element in ELEMENTS_LIST)
    distances['overall'] = overall_distance
    
    return distances

def main():
    elements_all_films_dict = get_all_film_elements(INPUT_ROOT_DIR)
    json.dumps(elements_all_films_dict)
    
    print("Film keys:", list(elements_all_films_dict.keys()))
    print(f"Reference film data: {json.dumps(elements_all_films_dict.get(REFERENCE_FILM), indent=2)}")
    
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
                print(f"Error processing films {reference_key} and {test_key}: {str(e)}")
                print(f"Reference data: {elements_all_films_dict.get(reference_key)}")
                print(f"Test data: {elements_all_films_dict.get(test_key)}")

    element_distances_all_df = pd.DataFrame(element_distances_all)
    
    output_file = os.path.join(OUTPUT_ROOT_DIR, 'element_distances_all.csv')
    element_distances_all_df.to_csv(output_file, index=False)
    print(f"Element distances saved to {output_file}")
    print(element_distances_all_df)

if __name__ == "__main__":
    main()