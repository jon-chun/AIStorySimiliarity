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
from fix_busted_json import repair_json
from json_repair import repair_json 
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

# SETUP COMPARISON =====
# Select COMPARISION_TYPE from ['genai-genai','element-element','script-script']
COMPARISON_TYPE = 'element-element'

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


# IMPORT PROMPTS =====

if COMPARISON_TYPE == 'element-element':
    # For RefElements-TestElements Comparisons
    from prompts.prompts_compare_characters import prompt_similarity_characters as prompt_compare_characters
    from prompts.prompts_compare_plot import prompt_similarity_plot as prompt_compare_plot
    from prompts.prompts_compare_setting import prompt_similarity_setting as prompt_compare_setting
    from prompts.prompts_compare_themes import prompt_similarity_themes as prompt_compare_themes
elif COMPARISON_TYPE == 'genai-genai':
    # For RefGenAI-RefGenAI Comparisons
    from prompts.prompts_rubric_characters import prompt_similarity_characters
    from prompts.prompts_rubric_plot import prompt_similarity_plot
    from prompts.prompts_rubric_setting import prompt_similarity_setting
    from prompts.prompts_rubric_themes import prompt_similarity_themes
else:
    print(f"ERROR: Illegal value for COMPARISON_TYPE: {COMPARISON_TYPE}")
    exit()


# DEFINE CONSTANTS =====

# INPUTS to compare by full scripts
INPUT_SCRIPTS_DIR = os.path.join('data', 'film_scripts_txt')
# INPUTS to compare by extracted narrative elements
INPUT_ELEMENTS_DIR = os.path.join('data','film_narrative_elements')

# REFERENCE FILM
SCRIPT_REFERENCE = 'raiders-of-the-lost-ark'
SCRIPT_TITLE_YEAR = '###FILM: Raiders of the Lost Ark\n###YEAR: 1981\n'
SCRIPT_TITLE_YEAR_FILENAME = 'raiders-of-the-lost-ark_1981'

scripts_list_full = sorted(os.listdir(INPUT_SCRIPTS_DIR))
scripts_list = [string.split('.')[0] for string in scripts_list_full] # Remove filename .ext suffix
scripts_list = [string.split('_')[1:] for string in scripts_list] # Remove leading (type)_ prefix
scripts_list = [string for string in scripts_list if string[0] != SCRIPT_REFERENCE]
print(f"FIRST scripts_list: {scripts_list}")

ELEMENTS_TYPE_LIST = ['characters','plot','setting','themes']

if COMPARISON_TYPE == 'genai-genai':
    OUTPUT_DIR_SIM_BY_SCORE = os.path.join('data', 'film_similarity_by_score_genai')
    output_filename_pkl = f"similarity-by-score_genai_{SCRIPT_REFERENCE}.pkl"
    output_fullpath_pkl = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, output_filename_pkl)
    output_filename_csv = f"similarity-by-score_genai_{SCRIPT_REFERENCE}.csv"
    output_fullpath_csv = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, output_filename_csv)
elif COMPARISON_TYPE == 'element-element':
    OUTPUT_DIR_SIM_BY_SCORE = os.path.join('data', 'film_similarity_by_score_elements')
    output_filename_pkl = f"similarity-by-score_elements_{SCRIPT_REFERENCE}.pkl"
    output_fullpath_pkl = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, output_filename_pkl)
    output_filename_csv = f"similarity-by-score_elements_{SCRIPT_REFERENCE}.csv"
    output_fullpath_csv = os.path.join(OUTPUT_DIR_SIM_BY_SCORE, output_filename_csv)
    INPUT_DIR_ELEMENTS = os.path.join('data','film_narrative_elements')
else:
    print(f"ERROR: Illegal value for COMPARISON_TYPE: {COMPARISON_TYPE}")
    exit()



# Add overwrite flag
OVERWRITE_FLAG = False

# PROMPTS =====

from prompts.prompts_compare_with_memory import prompt_similarity_to_memory_start, prompt_similarity_to_memory_middle, prompt_similarity_to_memory_end

# FUNCTIONS =====

def log_and_terminal(message: str, level: str = "info"):
    """
    Log a message and print it to the terminal.

    Args:
        message (str): The message to log and print.
        level (str): The logging level ('info', 'error', etc.). Defaults to 'info'.
    """
    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "debug":
        logger.debug(message)
    else:
        logger.info(message)
    
    print(message)

def read_file(input_dir: str, filename: str) -> str:
    try:
        file_fullpath = os.path.join(input_dir, filename)
        with open(file_fullpath, 'r', encoding='utf-8') as fp:
            file_text = fp.read()
        logger.info(f"Successfully read file: {filename}")
        return file_text
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return ""

def save_to_file(decision: str, content: str, file_path: str) -> None:
    try:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directories to {directory}")
        
        decision_content = f"{decision.strip()}\n{content.strip()}\n"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(decision_content)
        logger.info(f"Successfully wrote to {file_path}")
    except OSError as e:
        logger.error(f"Error creating directories or writing to {file_path}: {e}")

def save_to_pkl(dictionary: Dict[str, any], file_path: str) -> None:
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(dictionary, file)
        print(f"Dictionary successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the dictionary to {file_path}: {e}")

def read_from_pkl(file_path: str) -> Dict[str, any]:
    try:
        with open(file_path, 'rb') as file:
            dictionary = pickle.load(file)
        print(f"Dictionary successfully read from {file_path}")
        return dictionary
    except Exception as e:
        print(f"An error occurred while reading the dictionary from {file_path}: {e}")
        return {}

def save_to_csv(df: pd.DataFrame, output_fullpath_csv: str) -> None:
    try:
        df.to_csv(output_fullpath_csv, index=False)
        print(f"DataFrame successfully saved to {output_fullpath_csv}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame to {output_fullpath_csv}: {e}")

def read_from_csv(input_fullpath_csv: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(input_fullpath_csv)
        print(f"DataFrame successfully read from {input_fullpath_csv}")
        return df
    except Exception as e:
        print(f"An error occurred while reading the DataFrame from {input_fullpath_csv}: {e}")
        return pd.DataFrame()

def call_openai(prompt_str: str) -> Optional[Dict]:

    try:
        for attempt in range(MAX_RETRY_DICT_PARSE):

            log_and_terminal(f"Sending prompt to OpenAI: {prompt_str}\n")
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
            log_and_terminal(f"Received response from OpenAI: {response}")

            
            try:
                # Two options to try to repair malformed JSON string response
                # A. https://github.com/Qarj/fix-busted-json 202404 27s
                # B. https://github.com/mangiucugna/json_repair/ 20040627 429s
                try:
                    response_fix_json_pass1 = repair_json(response) # Attempt to repair malformed JSON string
                except:
                    response_fix_json_pass1 = response
                try:
                    response_fix_json_pass2 = repair_json(response_fix_json_pass1)
                except:
                    response_fix_json_pass2 = response_fix_json_pass1

                response_dict = json.loads(response_fix_json_pass2)
                log_and_terminal(f"Successfully parsed response to dictionary on attempt {attempt + 1}")
                return response_dict
            except json.JSONDecodeError as parse_error:
                log_and_terminal(f"Attempt {attempt + 1} failed to parse response to dictionary: {parse_error}", level="error")
                if attempt == MAX_RETRY_DICT_PARSE - 1:
                    log_and_terminal("Max retry attempts reached. Returning None.", level="error")
                    return None

    except Exception as e:
        log_and_terminal(f"Error in API call: {e}", level="error")
        return None

def get_distance_between_one(test_n_text: str) -> Optional[str]:
    """
    Get the distance between the reference script and the given test script.

    Args:
        test_n_text (str): The content of the test script.

    Returns:
        Optional[str]: The response from the OpenAI API, or None if there was an error.
    """
    full_prompt = (
        prompt_similarity_to_memory_start +
        test_n_text +
        prompt_similarity_to_memory_middle + 
        SCRIPT_TITLE_YEAR +
        prompt_similarity_to_memory_end
    )
    logger.info(f"Constructed full prompt: {full_prompt[:50]}...")
    return call_openai(full_prompt)

def get_distance_between_two(reference_text: str, test_w_text: str) -> int:
    """
    Calculate the absolute difference in length between two texts.

    Args:
        reference_text (str): The reference text.
        test_w_text (str): The test text.

    Returns:
        int: The absolute difference in length between the two texts.
    """
    return abs(len(reference_text) - len(test_w_text))

def similarity_metric(reference_file: str, test_x_file: str, test_y_file: str) -> Optional[Tuple[str, int]]:
    """
    Calculate the similarity metric between a reference file and two test files.

    Args:
        reference_file (str): The filename of the reference script.
        test_x_file (str): The filename of the first test script.
        test_y_file (str): The filename of the second test script.

    Returns:
        Optional[Tuple[str, int]]: A tuple containing the filename of the more similar script and its distance,
                                   or None if there was an error.
    """
    try:
        reference_text = read_file(reference_file)
        test_x_text = read_file(test_x_file)
        test_y_text = read_file(test_y_file)

        if not reference_text or not test_x_text or not test_y_text:
            raise Exception("One or more files could not be read")

        diff_ref_x = get_distance_between_two(reference_text, test_x_text)
        diff_ref_y = get_distance_between_two(reference_text, test_y_text)

        return (test_y_file, diff_ref_y) if diff_ref_x > diff_ref_y else (test_x_file, diff_ref_x)
    except Exception as e:
        logger.error(f"Error in similarity_metric: {e}")
        return None

def rank_two_by_reference(reference_file: str, test_a_file: str, test_b_file: str) -> Optional[Tuple[str, int]]:
    """
    Rank two test files against a reference file.

    Args:
        reference_file (str): The filename of the reference script.
        test_a_file (str): The filename of the first test script.
        test_b_file (str): The filename of the second test script.

    Returns:
        Optional[Tuple[str, int]]: A tuple containing the filename of the more similar script and its distance,
                                   or None if there was an error.
    """
    try:
        result_a = similarity_metric(reference_file, test_a_file, test_b_file)
        result_b = similarity_metric(reference_file, test_b_file, test_a_file)
        return result_a if result_a[1] <= result_b[1] else result_b
    except Exception as e:
        logger.error(f"Error in rank_two_by_reference: {e}")
        return None

def merge(reference_file: str, left: List[Tuple[str, int]], right: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
    """
    Merge two sorted lists of scripts based on their similarity to a reference file.

    Args:
        reference_file (str): The filename of the reference script.
        left (List[Tuple[str, int]]): The left sorted list of (script, distance) tuples.
        right (List[Tuple[str, int]]): The right sorted list of (script, distance) tuples.

    Returns:
        List[Tuple[str, int]]: A merged and sorted list of (script, distance) tuples.
    """
    result = []
    try:
        while left and right:
            left_file, left_distance = left[0]
            right_file, right_distance = right[0]
            comparison = rank_two_by_reference(reference_file, left_file, right_file)
            if comparison is None:
                raise Exception("Comparison failed")
            if comparison[0] == left_file:
                result.append(left.pop(0))
            else:
                result.append(right.pop(0))
        result.extend(left if left else right)
        return result
    except Exception as e:
        logger.error(f"Error in merge: {e}")
        return []

def merge_sort(reference_file: str, files: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
    """
    Sort a list of scripts based on their similarity to a reference file using merge sort.

    Args:
        reference_file (str): The filename of the reference script.
        files (List[Tuple[str, int]]): A list of (script, distance) tuples to sort.

    Returns:
        List[Tuple[str, int]]: A sorted list of (script, distance) tuples.
    """
    if len(files) <= 1:
        return files
    try:
        mid = len(files) // 2
        left = merge_sort(reference_file, files[:mid])
        right = merge_sort(reference_file, files[mid:])
        return merge(reference_file, left, right)
    except Exception as e:
        logger.error(f"Error in merge_sort: {e}")
        return []


def summarize_narrative(script_text):
    pass


def clean_title(title_dirty):
    # print(f"IN clean_title() with title_dirty: {title_dirty}")
    # script_indiana-jones-and-the-dial-of-destiny_2023
    title_clean = title_dirty.replace('-',' ').title() #  + f" ({title_dirty.split('_')[-1]})"
    # print(f"IN clea_title() with title_clean: {title_clean}")
    return title_clean


def get_element_description(film_name, narrative_element):
    for film_subdir_name in sorted(os.listdir(INPUT_DIR_ELEMENTS)):
        if film_name.lower() not in film_subdir_name.lower():
            continue

        element_description_subdir = os.path.join(INPUT_DIR_ELEMENTS, film_subdir_name)
        for file_description_name in sorted(os.listdir(element_description_subdir)):
            if narrative_element not in file_description_name:
                continue

            element_description_fullpath = os.path.join(element_description_subdir, file_description_name)
            try:
                with open(element_description_fullpath, 'r') as file:
                    description_text = file.read().strip()
                    print('  IN get_element_description: ')
                    print(f"    for element_description_fullpath: {element_description_fullpath}")
                    print(f"        returning description_text: {description_text}")
                    return description_text
            except IOError as e:
                print(f"Error reading file {element_description_fullpath}: {e}")
                return None

    print(f"No matching description found for film '{film_name}' and element '{narrative_element}'")
    return None

def get_element_distance(film_reference, film_test, narrative_element, unique_id):
    title_clean_reference = clean_title(film_reference)
    title_clean_test = clean_title(film_test)
    print(f"  IN get_element_distance(): title_clean_reference: {title_clean_reference}, title_clean_test: {title_clean_test}")

    reference_element_description = get_element_description(film_reference, narrative_element)
    prompt_header_reference_elements = f"\n\n###REFERENCE_FILM:\n{film_reference}\n\n{reference_element_description}\n"
    
    test_element_description = get_element_description(film_test, narrative_element)
    prompt_header_test_elements = f"\n\n###TEST_FILM:\n{film_test}\n\n{test_element_description}\n"

    try:
        prompt_compare_value = eval(f"prompt_compare_{narrative_element}")
    except NameError:
        raise ValueError(f"Variable prompt_similarity_{narrative_element} is not defined")

    prompt_full = f"ID: {unique_id}\n\n" + prompt_header_reference_elements + prompt_header_test_elements + prompt_compare_value
    
    # Log the prompt being sent (for debugging purposes)
    # print(f"PROMPT_FULL to OpenAI for {narrative_element}:")
    # print(prompt_full)

    response_raw = call_openai(prompt_full)
    time.sleep(SLEEP_SECONDS)
    
    # Log the raw response (for debugging purposes)
    print(f"RESPONSE from OpenAI for {narrative_element}:")
    print(json.dumps(response_raw, indent=2))

    if isinstance(response_raw, dict):
        response_dict = response_raw
    elif isinstance(response_raw, list) and len(response_raw) > 0:
        response_dict = response_raw[0]
    else:
        raise ValueError(f"Unexpected response format from OpenAI API for {narrative_element}")

    # Ensure the response has the expected structure
    if 'similarity_overall' not in response_dict:
        raise ValueError(f"Response for {narrative_element} does not contain 'similarity_overall'")

    similarity_overall = response_dict['similarity_overall']

    return response_dict


def get_genai_distance(script_reference, film_name, narrative_element, unique_id):
    title_clean_reference = clean_title(SCRIPT_REFERENCE)
    title_clean_test = clean_title(film_name)
    prompt_header = f"\n\n###REFERENCE_FILM:\n{title_clean_reference}\n\n###TEST_FILM:\n{title_clean_test}\n"

    try:
        prompt_similarity_value = eval(f"prompt_similarity_{narrative_element}")
    except NameError:
        raise ValueError(f"Variable prompt_similarity_{narrative_element} is not defined")

    prompt_full = f"ID: {unique_id}\n\n" + prompt_header + prompt_similarity_value
    
    # Log the prompt being sent (for debugging purposes)
    # print(f"PROMPT_FULL to OpenAI for {narrative_element}:")
    # print(prompt_full)

    response_raw = call_openai(prompt_full)
    time.sleep(SLEEP_SECONDS)
    
    # Log the raw response (for debugging purposes)
    print(f"RESPONSE from OpenAI for {narrative_element}:")
    print(json.dumps(response_raw, indent=2))

    if isinstance(response_raw, dict):
        response_dict = response_raw
    elif isinstance(response_raw, list) and len(response_raw) > 0:
        response_dict = response_raw[0]
    else:
        raise ValueError(f"Unexpected response format from OpenAI API for {narrative_element}")

    # Ensure the response has the expected structure
    if 'similarity_overall' not in response_dict:
        raise ValueError(f"Response for {narrative_element} does not contain 'similarity_overall'")

    similarity_overall = response_dict['similarity_overall']

    return response_dict




# DO NOT USE: for illustrative purpose only
# results in duplicate respones due to local client-side caching
@lru_cache(maxsize=None)
def cached_get_genai_distance(SCRIPT_REFERENCE: str, film_name: str, narrative_element: str) -> Dict[str, any]:
    return get_genai_distance(SCRIPT_REFERENCE, film_name, narrative_element)

# Generate a unique ID to inject into the prompt to try to avoid remote caching on OpenAI side
# and duplicate responses
def generate_unique_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def main():
    print("PROCESSING: ")
    print(f"  FILM_REFERENCE: {SCRIPT_REFERENCE}")
    print(f"  film_list: {scripts_list}\n")

    print(f"SIMILARITY #1.A. rank_by_score of RefGen-TestGen")
    columns_list = ['film', 'datetime', 'sample', 'unique_id'] + ELEMENTS_TYPE_LIST + ['overall']
    rankbyscore_refgentestgen_filmdf = pd.DataFrame(columns=columns_list)

    scripts_list_filtered = scripts_list  # DEBUG scripts_list[-4:]

    for sample in range(SAMPLE_SIZE):
        print(f"Processing sample {sample + 1} of {SAMPLE_SIZE}")
        rankbyscore_refgentestgen_filmdict = {}

        for film_index, film_info in enumerate(scripts_list_filtered):
            film_name, film_year = film_info
            
            if COMPARISON_TYPE == 'genai-genai':
                output_file = f"{output_fullpath_csv.rsplit('.', 1)[0]}_{film_name}.csv"
            elif COMPARISON_TYPE == 'element-element':
                output_file = f"{output_fullpath_csv.rsplit('.', 1)[0]}_{film_name}.csv"
            else:
                print(f"ERROR: Illegal value for COMPARISON_TYPE: {COMPARISON_TYPE}")
                exit()
            print(f'MAIN: output_file: {output_file}')

            if os.path.exists(output_file) and not OVERWRITE_FLAG:
                print(f"Appending to existing file for film {film_name}.")
            else:
                print(f"Creating new file for film {film_name}.")
            
            try:
                print(f"PROCESSING film #{film_index}: {film_name}) vs REFERENCE: {SCRIPT_REFERENCE}")

                datetime_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                unique_id = generate_unique_id()
                film_similarity_row_dict = {'film': f"{film_name}", 'datetime': datetime_str, 'sample': sample + 1, 'unique_id': unique_id}
                similarity_sum = 0
                rankbyscore_refgentestgen_elementdict = {}

                for narrative_element in ELEMENTS_TYPE_LIST:
                    print(f"  NARRATIVE ELEMENT: {narrative_element}")
                    output_file = f"{output_fullpath_csv.rsplit('.', 1)[0]}_{film_name}_{narrative_element}.csv"
                    print(f"    output_file = {output_file}")
                    print(f"      SCRIPT_REFERENCE: {SCRIPT_REFERENCE}")
                    print(f"      film_name: {film_name}")
                    if COMPARISON_TYPE == 'genai-genai':
                        similarity_element_dict = get_genai_distance(SCRIPT_REFERENCE, film_name, narrative_element, unique_id)
                    elif COMPARISON_TYPE == 'element-element':
                        similarity_element_dict = get_element_distance(SCRIPT_REFERENCE, film_name, narrative_element, unique_id)
                    else:
                        print(f"ERROR: Illegal value for COMPARISON_TYPE: {COMPARISON_TYPE}")
                        exit()
                    print(f"\n\n\nsimilarity_element_dict for {narrative_element}:")
                    print(json.dumps(similarity_element_dict, indent=4, ensure_ascii=False))
                    rankbyscore_refgentestgen_elementdict[narrative_element] = similarity_element_dict

                    similarity_overall = similarity_element_dict['similarity_overall']
                    print(f"similarity_overall for {narrative_element}: {similarity_overall}")
                    film_similarity_row_dict[narrative_element] = similarity_overall
                    similarity_sum += similarity_overall

                overall_similarity = similarity_sum / len(ELEMENTS_TYPE_LIST)
                print(f"Overall similarity for {film_name}): {overall_similarity}")
                film_similarity_row_dict['overall'] = overall_similarity
                
                new_row_df = pd.DataFrame([film_similarity_row_dict])
                rankbyscore_refgentestgen_filmdf = pd.concat([rankbyscore_refgentestgen_filmdf, new_row_df], ignore_index=True)
                rankbyscore_refgentestgen_filmdict[f"{film_name})_{datetime_str}"] = rankbyscore_refgentestgen_elementdict

                # Save results after each film is processed
                try:
                    pkl_output_file = f"{output_fullpath_pkl.rsplit('.', 1)[0]}_{film_name}_{datetime_str}.pkl"
                    save_to_pkl(rankbyscore_refgentestgen_filmdict, pkl_output_file)
                    
                    if os.path.exists(output_file) and not OVERWRITE_FLAG:
                        existing_df = pd.read_csv(output_file)
                        updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                    else:
                        updated_df = new_row_df
                    
                    save_to_csv(updated_df, output_file)
                    print(f"Data saved successfully for {film_name}, sample {sample + 1}")
                except Exception as e:
                    print(f"Error saving output files for {film_name}, sample {sample + 1}: {str(e)}")

            except Exception as e:
                print(f"Error processing film {film_name}): {str(e)}")
                continue

    # Final save of the complete DataFrame
    if not rankbyscore_refgentestgen_filmdf.empty:
        rankbyscore_refgentestgen_filmdf.sort_values(by=['film', 'sample', 'datetime'], ascending=[True, True, False], inplace=True)
        try:
            final_datetime_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            final_pkl_output = f"{output_fullpath_pkl.rsplit('.', 1)[0]}_{final_datetime_str}.pkl"
            save_to_pkl(rankbyscore_refgentestgen_filmdict, final_pkl_output)
            save_to_csv(rankbyscore_refgentestgen_filmdf, output_fullpath_csv)
            print(f"Final data saved successfully to {final_pkl_output} and {output_fullpath_csv}")
        except Exception as e:
            print(f"Error saving final output files: {str(e)}")
    else:
        print("ERROR: No data to save. All film processing attempts failed.")

    print(f"\n\n\nJSON.DUMPS(rankbyscore_refgentestgen_filmdict)")
    print(json.dumps(rankbyscore_refgentestgen_filmdict, indent=4, ensure_ascii=False))

    print(f"\n\nHEAD: rankbyscore_refgentestgen_filmdf.head()")
    print(rankbyscore_refgentestgen_filmdf.head())

if __name__ == "__main__":
    main()