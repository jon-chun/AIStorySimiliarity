import os
import string
import random
import json
import time
import datetime
import pandas as pd
import pickle
import logging
from openai import OpenAI
from typing import List, Dict, Tuple, Optional
from json_repair import repair_json

# Configuration
COMPARISON_TYPE = 'genaigenai'  # Options: 'genaigenai', 'elementelement'
MODEL_NAME = 'gpt-3.5-turbo'
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 0.5
OVERWRITE_FLAG = False
MAX_RETRY_DICT_PARSE = 3
SAMPLE_SIZE = 33
SLEEP_SECONDS = 1

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# OpenAI setup
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Import prompts based on comparison type
if COMPARISON_TYPE == 'elementelement':
    from prompts.prompts_compare_characters import prompt_similarity_characters as prompt_compare_characters
    from prompts.prompts_compare_plot import prompt_similarity_plot as prompt_compare_plot
    from prompts.prompts_compare_setting import prompt_similarity_setting as prompt_compare_setting
    from prompts.prompts_compare_themes import prompt_similarity_themes as prompt_compare_themes
elif COMPARISON_TYPE == 'genaigenai':
    from prompts.prompts_rubric_characters import prompt_similarity_characters
    from prompts.prompts_rubric_plot import prompt_similarity_plot
    from prompts.prompts_rubric_setting import prompt_similarity_setting
    from prompts.prompts_rubric_themes import prompt_similarity_themes
else:
    raise ValueError(f"Invalid COMPARISON_TYPE: {COMPARISON_TYPE}")

# Constants
SCRIPT_REFERENCE = 'raiders-of-the-lost-ark'
SCRIPT_TITLE_YEAR = '###FILM: Raiders of the Lost Ark\n###YEAR: 1981\n'
INPUT_SCRIPTS_DIR = os.path.join('data', 'film_scripts_txt')
INPUT_ELEMENTS_DIR = os.path.join('data', 'film_narrative_elements')
ELEMENTS_TYPE_LIST = ['characters', 'plot', 'setting', 'themes']

# Setup output paths
OUTPUT_DIR_SIM_BY_SCORE = os.path.join('data', f'score_diff_genai') # {COMPARISON_TYPE}')
output_filename_pkl = f"compare_{COMPARISON_TYPE}_{SCRIPT_REFERENCE}.pkl"
output_fullpath_pkl = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, output_filename_pkl)
output_filename_csv = f"compare_{COMPARISON_TYPE}_{SCRIPT_REFERENCE}.csv"
output_fullpath_csv = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, output_filename_csv)

# Helper functions
def log_and_print(message: str, level: str = "info"):
    getattr(logger, level)(message)
    print(message)

def repair_json_string(response: str) -> str:
    try:
        json.loads(response)
        return response
    except json.JSONDecodeError:
        return repair_json(response)

def read_json_file(filepath: str) -> Dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.loads(repair_json_string(file.read()))
    except Exception as e:
        log_and_print(f"Error reading {filepath}: {e}", "error")
        return {}

def version_filename(base_name: str, version: int) -> str:
    name = os.path.splitext(base_name)[0]  # Remove any existing extension
    name = name.replace('.txt', '')  # Remove any embedded .txt
    return f"{name}_ver{version}.csv"

def get_latest_version_and_film(output_dir: str) -> Tuple[int, Optional[str]]:
    files = sorted(os.listdir(output_dir))
    for file in reversed(files):
        if file.startswith("compare_genaigenai_") and file.endswith(".pkl"):
            parts = file.split("_")
            if len(parts) >= 4:
                try:
                    return int(parts[-1].split(".")[0][3:]), "_".join(parts[2:-1])
                except ValueError:
                    continue
    return 0, None

def read_file(input_dir: str, filename: str) -> str:
    try:
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as fp:
            return fp.read()
    except Exception as e:
        log_and_print(f"Error reading file {filename}: {e}", "error")
        return ""

def save_to_file(content: str, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    log_and_print(f"Successfully wrote to {file_path}")

def save_to_pkl(dictionary: Dict, file_path: str) -> None:
    with open(file_path, 'wb') as file:
        pickle.dump(dictionary, file)
    log_and_print(f"Dictionary saved to {file_path}")

def read_from_pkl(file_path: str) -> Dict:
    try:
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        log_and_print(f"Error reading from {file_path}: {e}", "error")
        return {}

def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    df.to_csv(output_path, index=False)
    log_and_print(f"DataFrame saved to {output_path}")

def read_from_csv(input_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(input_path)
    except Exception as e:
        log_and_print(f"Error reading from {input_path}: {e}", "error")
        return pd.DataFrame()

def call_openai(prompt_str: str) -> Optional[Dict]:
    for attempt in range(MAX_RETRY_DICT_PARSE):
        try:
            completion = openai_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_str}],
                model=MODEL_NAME,
                temperature=DEFAULT_TEMPERATURE,
                top_p=DEFAULT_TOP_P,
                response_format={"type": "json_object"},
            )
            response = completion.choices[0].message.content
            return json.loads(repair_json_string(response))
        except Exception as e:
            log_and_print(f"Attempt {attempt + 1} failed: {e}", "error")
    return None

def get_element_description(film_name: str, narrative_element: str) -> Optional[str]:
    for film_subdir_name in sorted(os.listdir(INPUT_ELEMENTS_DIR)):
        if film_name.lower() not in film_subdir_name.lower():
            continue
        element_description_subdir = os.path.join(INPUT_ELEMENTS_DIR, film_subdir_name)
        for file_description_name in sorted(os.listdir(element_description_subdir)):
            if narrative_element not in file_description_name:
                continue
            element_description_fullpath = os.path.join(element_description_subdir, file_description_name)
            try:
                with open(element_description_fullpath, 'r') as file:
                    return file.read().strip()
            except IOError as e:
                log_and_print(f"Error reading file {element_description_fullpath}: {e}", "error")
    log_and_print(f"No matching description found for film '{film_name}' and element '{narrative_element}'", "warning")
    return None

def get_similarity(film_reference: str, film_test: str, narrative_element: str, unique_id: str) -> Dict:
    prompt_header = f"\n\n###REFERENCE_FILM:\n{film_reference}\n\n###TEST_FILM:\n{film_test}\n"
    prompt_similarity_value = globals()[f"prompt_similarity_{narrative_element}"]
    prompt_full = f"ID: {unique_id}\n\n{prompt_header}{prompt_similarity_value}"
    
    response_dict = call_openai(prompt_full)
    time.sleep(SLEEP_SECONDS)
    
    if not isinstance(response_dict, dict) or 'similarity_overall' not in response_dict:
        raise ValueError(f"Unexpected response format from OpenAI API for {narrative_element}")
    
    return response_dict

def generate_unique_id(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    log_and_print(f"Processing reference film: {SCRIPT_REFERENCE}")
    
    latest_version, last_processed_film = get_latest_version_and_film(OUTPUT_DIR_SIM_BY_SCORE)
    start_version = latest_version if last_processed_film else 0
    # scripts_list = [f for f in os.listdir(INPUT_SCRIPTS_DIR) if f.endswith('.txt') and SCRIPT_REFERENCE not in f]
    scripts_list = [f.replace('.txt', '') for f in os.listdir(INPUT_SCRIPTS_DIR) if f.endswith('.txt') and SCRIPT_REFERENCE not in f]
    start_film_index = scripts_list.index(last_processed_film) + 1 if last_processed_film in scripts_list else 0

    log_and_print(f"Resuming from version {start_version}, film index {start_film_index}")

    for sample in range(start_version, start_version + SAMPLE_SIZE):
        log_and_print(f"Processing sample {sample + 1} of {start_version + SAMPLE_SIZE}")
        rankbyscore_refgentestgen_filmdict = {}

        for film_index, film_name in enumerate(scripts_list[start_film_index:], start=start_film_index):
            film_name = film_name.replace('.txt', '')  # Ensure .txt is removed

            output_file = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, version_filename(f"similarity-by-score_{COMPARISON_TYPE}_{SCRIPT_REFERENCE}_{film_name.replace('.txt', '')}",sample))
            # output_file = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, version_filename(f"compare_genigenai_{COMPARISON_TYPE}_{SCRIPT_REFERENCE}_{film_name}", sample))

            if os.path.exists(f"{output_file}.csv") and not OVERWRITE_FLAG:
                log_and_print(f"Skipping existing file for film {film_name} (Version {sample})")
                continue

            try:
                log_and_print(f"Processing film #{film_index}: {film_name} vs REFERENCE: {SCRIPT_REFERENCE}")

                datetime_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                unique_id = generate_unique_id()
                film_similarity_row_dict = {'film': film_name, 'datetime': datetime_str, 'sample': sample + 1, 'unique_id': unique_id}
                
                for narrative_element in ELEMENTS_TYPE_LIST:
                    log_and_print(f"  NARRATIVE ELEMENT: {narrative_element}")
                    similarity_element_dict = get_similarity(SCRIPT_REFERENCE, film_name, narrative_element, unique_id)
                    rankbyscore_refgentestgen_filmdict.setdefault(f"{film_name}_{datetime_str}", {})[narrative_element] = similarity_element_dict
                    film_similarity_row_dict[narrative_element] = similarity_element_dict['similarity_overall']

                film_similarity_row_dict['overall'] = sum(film_similarity_row_dict[e] for e in ELEMENTS_TYPE_LIST) / len(ELEMENTS_TYPE_LIST)
                
                new_row_df = pd.DataFrame([film_similarity_row_dict])
                
                save_to_pkl(rankbyscore_refgentestgen_filmdict, f"{output_file}.pkl")
                save_to_csv(new_row_df, f"{output_file}.csv")
                log_and_print(f"Data saved successfully for {film_name}, sample {sample + 1}")

            except Exception as e:
                log_and_print(f"Error processing film {film_name}: {str(e)}", "error")

        start_film_index = 0  # Reset for next versions

    log_and_print("Processing complete")

if __name__ == "__main__":
    main()