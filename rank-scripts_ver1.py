import os
import json
import pandas as pd
from datetime import datetime
import pickle
import logging
from openai import OpenAI
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

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
    SLEEP_SECONDS = 0.1

MODEL_NAME = 'gpt-3.5-turbo' # 'gpt-4o'
# 'gpt-3.5-turbo is limited to 16k tokens ~12kb plain text file 
# 'gpt-4o' has 128k tokens window
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 0.5

# Max retries to parse OpenAI API response into Python Dictionary
MAX_RETRY_DICT_PARSE = 3

# Configure how many iterations to run
SAMPLE_SIZE = 30

# DEFINE CONSTANTS =====

# INPUTS to compare by full scripts
INPUT_SCRIPTS_DIR = os.path.join('data', 'film_scripts_txt')
# INPUTS to compare by extracted narrative elements
INPUT_ELEMENTS_DIR = os.path.join('data','film_narrative_elements')

# REFERENCE FILM
SCRIPT_REFERENCE = 'script_raiders-of-the-lost-ark_1981'
SCRIPT_TITLE_YEAR = '###FILM: Raiders of the Lost Ark\n###YEAR: 1981\n'
SCRIPT_TITLE_YEAR_FILENAME = 'raiders-of-the-lost-ark_1981'

scripts_list_full = sorted(os.listdir(INPUT_SCRIPTS_DIR))
scripts_list = [string.split('.')[0] for string in scripts_list_full]
scripts_list = [string.split('_')[1:] for string in scripts_list]
scripts_list = [string for string in scripts_list if string != SCRIPT_REFERENCE]

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
    """
    Read the content of a file.

    Args:
        filename (str): The name of the file to read.

    Returns:
        str: The content of the file.

    Raises:
        Exception: If there's an error reading the file.
    """
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
    """
    Save content to the specified file, creating any necessary directories.

    Args:
        decision (str): A description of the content being saved.
        content (str): The content to be saved.
        file_path (str): The path where the file should be saved.

    Returns:
        None
    """
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
    """
    Save a multi-layer nested dictionary to a pickle file.

    Args:
        dictionary (Dict[str, Any]): The dictionary to save.
        file_path (str): The path to the file where the dictionary will be saved.
    """
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(dictionary, file)
        print(f"Dictionary successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the dictionary to {file_path}: {e}")

def read_from_pkl(file_path: str) -> Dict[str, any]:
    """
    Read a multi-layer nested dictionary from a pickle file.

    Args:
        file_path (str): The path to the pickle file to read.

    Returns:
        Dict[str, Any]: The dictionary read from the file.
    """
    try:
        with open(file_path, 'rb') as file:
            dictionary = pickle.load(file)
        print(f"Dictionary successfully read from {file_path}")
        return dictionary
    except Exception as e:
        print(f"An error occurred while reading the dictionary from {file_path}: {e}")
        return {}

def save_to_csv(df: pd.DataFrame, output_fullpath_csv: str) -> None:
    """
    Save a DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        output_fullpath_csv (str): The full path where the CSV file will be saved.
    """
    try:
        df.to_csv(output_fullpath_csv, index=False)
        print(f"DataFrame successfully saved to {output_fullpath_csv}")
    except Exception as e:
        print(f"An error occurred while saving the DataFrame to {output_fullpath_csv}: {e}")

def read_from_csv(input_fullpath_csv: str) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.

    Args:
        input_fullpath_csv (str): The full path to the CSV file to read.

    Returns:
        pd.DataFrame: The DataFrame read from the CSV file.
    """
    try:
        df = pd.read_csv(input_fullpath_csv)
        print(f"DataFrame successfully read from {input_fullpath_csv}")
        return df
    except Exception as e:
        print(f"An error occurred while reading the DataFrame from {input_fullpath_csv}: {e}")
        return pd.DataFrame()

def call_openai(prompt_str: str) -> Optional[Dict]:
    """
    Call the OpenAI API with the given prompt and return the response as a dictionary.

    Args:
        prompt_str (str): The prompt to send to the API.
        openai_client (OpenAI): The OpenAI client instance.

    Returns:
        Optional[Dict]: The API response content as a dictionary, or None if there was an error.
    """
    try:
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
        )

        response = completion.choices[0].message.content
        log_and_terminal(f"Received response from OpenAI: {response}")

        for attempt in range(MAX_RETRY_DICT_PARSE):
            try:
                response_dict = json.loads(response)
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
    title_clean = title_dirty.split("_")[1].replace('-',' ').title() + f" ({title_dirty.split('_')[-1]})"
    # print(f"IN clea_title() with title_clean: {title_clean}")
    return title_clean

from prompts.prompts_rubric_characters import prompt_similarity_characters
from prompts.prompts_rubric_plot import prompt_similarity_plot
from prompts.prompts_rubric_setting import prompt_similarity_setting
from prompts.prompts_rubric_themes import prompt_similarity_themes

def get_genai_distance(SCRIPT_REFERENCE, film_name):
    title_clean_reference = clean_title(SCRIPT_REFERENCE)
    title_clean_test = clean_title(film_name)
    prompt_header = f"\n\n###REFERENCE_FILM:\n{title_clean_reference}\n\n###TEST_FILM:\n{title_clean_test}\n"
    full_prompt_characters = prompt_header + prompt_similarity_characters
    # print(f"IN get_genai_distance() with full_prompt_characters: {full_prompt_characters}")
    response_characters_raw = call_openai(full_prompt_characters)
    return response_characters_raw


def get_genai_distance(SCRIPT_REFERENCE, film_name, narrative_element):
    title_clean_reference = clean_title(SCRIPT_REFERENCE)
    title_clean_test = clean_title(film_name)
    prompt_header = f"\n\n###REFERENCE_FILM:\n{title_clean_reference}\n\n###TEST_FILM:\n{title_clean_test}\n"
    full_prompt_characters = prompt_header + prompt_similarity_characters

    try:
        # Use eval to get the value of the variable named by the narrative_element
        prompt_similarity_value = eval(f"prompt_similarity_{narrative_element}")
    except NameError:
        raise ValueError(f"Variable prompt_similarity_{narrative_element} is not defined")
        return None

    full_prompt_characters = prompt_header + prompt_similarity_value
    response_characters_raw = call_openai(full_prompt_characters)
    
    # Return the response directly without adding an extra nesting level
    return response_characters_raw









# MAIN =====

def main():
    print("PROCESSING: ")
    print(f"  SCRIPT_REFERENCE: {SCRIPT_REFERENCE}")
    scripts_list = ['national-treasure_2004']
    print(f"  scripts_list: {scripts_list}\n")

    ELEMENT_TYPES_LIST = ['characters', 'plot', 'setting', 'themes']

    print(f"SIMILARITY #1.A. rank_by_score of RefGen-TestGen")
    rank_by_score_refgen_testgen_dict = {}
    columns_list = ['film'] + ELEMENT_TYPES_LIST + ['overall']
    film_similarity_rows = []

    for film_index, film_name in enumerate(scripts_list):
        try:
            print(f"PROCESSING film #{film_index}: {film_name}")
            film_similarity_row_dict = {'film': film_name}
            similarity_sum = 0
            rank_by_score_refgen_testgen_element_dict = {}

            for narrative_element in ELEMENT_TYPES_LIST:
                print(f"  NARRATIVE ELEMENT: {narrative_element}")
                similarity_element_dict = get_genai_distance(SCRIPT_REFERENCE, film_name, narrative_element)
                rank_by_score_refgen_testgen_element_dict[narrative_element] = similarity_element_dict
                film_similarity_row_dict[narrative_element] = similarity_element_dict['similarity_overall']
                similarity_sum += film_similarity_row_dict[narrative_element]

                print(f"\n\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                print(f"IN main() with element_{narrative_element}_dict: {similarity_element_dict}")
                print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n\n")

            similarity_overall = similarity_sum / len(ELEMENT_TYPES_LIST)
            film_similarity_row_dict['overall'] = similarity_overall
            film_similarity_rows.append(film_similarity_row_dict)
            rank_by_score_refgen_testgen_dict[film_name] = rank_by_score_refgen_testgen_element_dict

        except Exception as e:
            print(f"Error processing film {film_name}: {str(e)}")
            continue

    # Create DataFrame after loop
    rank_by_score_refgen_testgen_df = pd.DataFrame(film_similarity_rows, columns=columns_list)

    OUTPUT_DIR_SIM_BY_SCORE_GENAI = os.path.join('data', 'film_similarity_by_score_genai')
    output_filename_pkl = f"similarity_by_score_genai_{SCRIPT_REFERENCE}.pkl"
    output_fullpath_pkl = os.path.join(OUTPUT_DIR_SIM_BY_SCORE_GENAI, output_filename_pkl)
    output_filename_csv = f"similarity_by_score_genai_{SCRIPT_REFERENCE}.csv"
    output_fullpath_csv = os.path.join(OUTPUT_DIR_SIM_BY_SCORE_GENAI, output_filename_csv)

    try:
        save_to_pkl(rank_by_score_refgen_testgen_dict, output_fullpath_pkl)
        save_to_csv(rank_by_score_refgen_testgen_df, output_fullpath_csv)
    except Exception as e:
        print(f"Error saving output files: {str(e)}")

    print(json.dumps(rank_by_score_refgen_testgen_dict, indent=4, ensure_ascii=False))
    print(rank_by_score_refgen_testgen_dict['national-treasure_2004']['overall'])


    # B. rank_order: Rank by merge_sort(comparison_closer(reference, test1, test2))
    print(f"SIMILARITY #1.A. rank_by_order of RefGen-TestGen")
    rank_by_order_refgen_testgen_dict = {}



    # SIMILARITY METHOD #1: (refgen-testelem) reference_genai_vs_test_elements
    # TODO

    # SIMILARITY METHOD #2: (refgen-testscr) reference_genai_vs_test_scripts
    # TODO

    # SIMILARITY METHOD #3: (refelem-testgen) reference_elements_vs_test_genai
    # TODO

    # SIMILARITY METHOD #4 (refelem-testelem) reference_elements_vs_test_elements
    # NOW

    # SIMILARITY METHOD #5 (refelem-testscr) reference_elements_vs_test_script
    # TODO

    # SIMILARITY METHOD #6 (refscr-testgen) reference_script_vs_test_genai
    # TODO
    
    # SIMILARITY METHOD #7 (refscr-testelem) reference_script_vs_test_elements
    # TODO

    # SIMILARITY METHOD #8 (refscr-testscr) reference_script_vs_test_script
    # NOW


    # SIMILARITY METHOD #6 reference_script_vs_test_genai
        # Calculate distance between REFERENCE_TEXT and every other TEST_TEXT
        # COMPARE generating REFERENCE_TEXT from LLM

    COMPARISON_TYPE=""
    if False:
        results = []
        for script_index, script_file in enumerate(scripts_list):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"rank_by_{COMPARISON_TYPE}_{MODEL_NAME}_{SCRIPT_TITLE_YEAR_FILENAME}_{timestamp}.csv"
            csv_path = os.path.join(output_root_dir, MODEL_NAME, csv_filename)
            
            if os.path.exists(csv_path) and not OVERWRITE_FLAG:
                logger.info(f"Skipping existing file: {csv_path}")
                continue
            
            logger.info(f"Processing: script #{script_index}: {script_file}")
            script_text = read_file(script_file)
            script_narrative_summary = summarize_narrative(script_text)
            response = get_distance_between_one(script_text)
            logger.info(f"Response for {script_file}: {response[:50]}...")
            results.append((script_file, response))
        
        csv_content = "Script,Response\n"
        for script, response in results:
            csv_content += f"{script},{response}\n"
        
        save_to_file("Memory Comparison Results", csv_content, csv_path)

    elif COMPARISON_TYPE == 'score':
        # Calculate distance between reference text and every other test text
        # COMPARE both REFERENCE_TEXT and TEST_TEXT in
        #   subdir: ./data/film_narrative_elements/elements_{film_title}_{film_year}
        #     4 files ./elements_{film_title}_{film_year}_{narrative_type}.json
        #     here narrative_element in ['characters','plot','setting','themes']

        pass


    elif COMPARISON_TYPE == 'rank':
        # Calculate a rank order between 2 TEST_TEXTs to 
        # find which is more silimar to REFERENCE_TEXT
        # Use a Bubble Sort to rank order all TEST_TEXTs 
        # by similarity to REFERENCE_TEXT
        #   subdir: ./data/film_narrative_elements/elements_{film_title}_{film_year}
        #     4 files ./elements_{film_title}_{film_year}_{narrative_type}.json
        #     here narrative_element in ['characters','plot','setting','themes']
        pass

    elif COMPARISON_TYPE == 'scripts':
        # 

        try:
            scripts_with_distances = []
            for script in scripts_list:
                try:
                    _, distance = similarity_metric(SCRIPT_REFERENCE, script, script)
                    scripts_with_distances.append((script, distance))
                except Exception as e:
                    logger.error(f"Error calculating distance for {script}: {e}")
            
            scripts_ranked = merge_sort(SCRIPT_REFERENCE, scripts_with_distances)
            
            logger.info("Ranked files with distances:")
            for script, distance in scripts_ranked:
                logger.info(f"{script}: {distance}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"rank_by_{COMPARISON_TYPE}_{MODEL_NAME}_{SCRIPT_TITLE_YEAR_FILENAME}_{timestamp}.csv"
            csv_path = os.path.join(output_root_dir, MODEL_NAME, csv_filename)
            
            if os.path.exists(csv_path) and not OVERWRITE_FLAG:
                logger.info(f"Skipping existing file: {csv_path}")
                return
            
            csv_content = "Rank,Script,Distance\n"
            for rank, (script, distance) in enumerate(scripts_ranked, start=1):
                csv_content += f"{rank},{script},{distance}\n"
            
            save_to_file(f"{COMPARISON_TYPE.capitalize()} Comparison Results", csv_content, csv_path)
            
        except Exception as e:
            logger.error(f"Error in main execution: {e}")
    else:
        logger.error(f"ERROR: Illegal COMPARISON_TYPE: {COMPARISON_TYPE}")
        exit()

if __name__ == "__main__":
    main()