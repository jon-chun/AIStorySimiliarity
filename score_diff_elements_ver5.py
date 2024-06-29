import os
import json
import pandas as pd
from itertools import combinations
from similarity_customizations.similarity_weights import (
    characters_weights_dict,
    plot_weights_dict,
    setting_weights_dict,
    themes_weights_dict,
    element_weights_dict
)

INPUT_ROOT_DIR = os.path.join('data', 'film_narrative_elements')
OUTPUT_ROOT_DIR = os.path.join('data', 'score_diff_elements')
PROMPT_DIR = os.path.join('prompts')
ELEMENTS_LIST = ['characters', 'plot', 'setting', 'themes']
REFERENCE_FILM = 'elements_raiders-of-the-lost-ark_1981'

def clean_json_data(data):
    if isinstance(data, list) and len(data) == 1:
        data = data[0]
    if isinstance(data, dict):
        return data
    return {}

def read_json_file(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return clean_json_data(data)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading {filepath}: {e}")
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
            distances[element] = 0
        else:
            # Calculate distance for each character/plot point/etc.
            element_distances = []
            for ref_item, test_item in zip(reference_element.values(), test_element.values()):
                element_distances.append(get_element_pair_distance(ref_item, test_item, weights_dicts[element]))
            distances[element] = sum(element_distances) / len(element_distances) if element_distances else 0
    
    overall_distance = sum(distances[element] * (element_weights_dict[element] / 100) for element in ELEMENTS_LIST)
    distances['overall'] = overall_distance
    
    return distances

def main():
    elements_all_films_dict = get_all_film_elements(INPUT_ROOT_DIR)
    
    print("Film keys:", list(elements_all_films_dict.keys()))
    
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