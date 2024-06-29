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
from functools import lru_cache

INPUT_ROOT_DIR = os.path.join('data', 'film_narrative_elements')
OUTPUT_ROOT_DIR = os.path.join('data', 'score_diff_elements')
ELEMENTS_LIST = ['characters', 'plot', 'setting', 'themes']
REFERENCE_FILM = 'elements_raiders-of-the-lost-ark_1981'

def setup_logging():
    logging.basicConfig(filename='story_similarity.log', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(message, exception=None):
    error_message = f"ERROR: {message}"
    if exception:
        error_message += f"\n{str(exception)}"
    print(error_message)
    logging.error(error_message)

def clean_json_data(data):
    if isinstance(data, list) and len(data) == 1:
        data = data[0]
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

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

def get_element_pair_distance(reference_element_dict, test_element_dict, weights_dict):
    ref_flat = flatten_dict(reference_element_dict)
    test_flat = flatten_dict(test_element_dict)
    
    distance = 0
    for feature, weight in weights_dict.items():
        ref_value = str(ref_flat.get(feature, ''))
        test_value = str(test_flat.get(feature, ''))
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
            log_error(f"Empty data for {element} in {reference_key} or {test_key}")
            distances[element] = 0
        else:
            # Calculate distance for each character/plot point/etc.
            element_distances = []
            for ref_item, test_item in zip(reference_element.values(), test_element.values()):
                if isinstance(ref_item, dict) and isinstance(test_item, dict):
                    element_distances.append(get_element_pair_distance(ref_item, test_item, weights_dicts[element]))
                else:
                    log_error(f"Non-dict items found in {element} for {reference_key} or {test_key}")
                    element_distances.append(0)
            distances[element] = sum(element_distances) / len(element_distances) if element_distances else 0
    
    overall_distance = sum(distances[element] * (element_weights_dict[element] / 100) for element in ELEMENTS_LIST)
    distances['overall'] = overall_distance
    
    return distances

def main():
    setup_logging()
    elements_all_films_dict = get_all_film_elements(INPUT_ROOT_DIR)
    
    log_error(f"Film keys: {list(elements_all_films_dict.keys())}")
    log_error(f"Reference film: {REFERENCE_FILM}")
    
    element_distances_all = []
    film_keys = list(elements_all_films_dict.keys())
    
    for reference_key, test_key in combinations(film_keys, 2):
        if reference_key == REFERENCE_FILM or test_key == REFERENCE_FILM:
            reference_key, test_key = (REFERENCE_FILM, test_key) if reference_key == REFERENCE_FILM else (REFERENCE_FILM, reference_key)
            try:
                log_error(f"Processing: {reference_key} vs {test_key}")
                distances = get_story_distance(elements_all_films_dict, reference_key, test_key)
                row = {
                    'reference_film': reference_key,
                    'test_film': test_key,
                    **distances
                }
                element_distances_all.append(row)
            except Exception as e:
                log_error(f"Error processing films {reference_key} and {test_key}: {str(e)}")
                log_error(f"Reference data: {elements_all_films_dict.get(reference_key)}")
                log_error(f"Test data: {elements_all_films_dict.get(test_key)}")

    element_distances_all_df = pd.DataFrame(element_distances_all)
    
    output_file = os.path.join(OUTPUT_ROOT_DIR, 'element_distances_all.csv')
    element_distances_all_df.to_csv(output_file, index=False)
    log_error(f"Element distances saved to {output_file}")
    log_error(str(element_distances_all_df))

if __name__ == "__main__":
    main()
