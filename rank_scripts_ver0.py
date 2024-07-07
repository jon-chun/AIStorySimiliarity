import os
from datetime import datetime
import logging
from openai import OpenAI
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

# SETUP OPENAI =====

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    SLEEP_SECONDS = 0.1


MODEL_NAME = 'gpt-3.5-turbo' # 'gpt-4o'
# 'gpt-3.5-turbo is limited to 16k tokens ~12kb plain text file 
# 'gpt-4o' has 128k tokens window
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 0.5

# Configure how many iterations to run
SAMPLE_SIZE = 30

# DEFINE CONSTANTS =====

INPUT_DIR = os.path.join('data', 'film_scripts_txt')
SCRIPT_REFERENCE = 'script_lara-croft-tomb-raider_2001.txt'
SCRIPT_TITLE_YEAR = '###FILM: Raiders of the Lost Ark\n###YEAR: 1981\n'
SCRIPT_TITLE_YEAR_FILENAME = 'raiders-of-the-lost-ark_1981'

scripts_list_full = sorted(os.listdir(INPUT_DIR))
scripts_list = [string for string in scripts_list_full if string != SCRIPT_REFERENCE]

# Select COMPARISON_TYPE_BY in ['memory','scripts','score','rank']
COMPARISON_TYPE = 'memory'

# Add overwrite flag
OVERWRITE_FLAG = False

# PROMPTS =====

from prompts.prompts_compare_with_memory import prompt_similarity_to_memory_start, prompt_similarity_to_memory_middle, prompt_similarity_to_memory_end

# FUNCTIONS =====

def read_file(filename: str) -> str:
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
        file_fullpath = os.path.join(INPUT_DIR, filename)
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

def call_openai(prompt_str: str) -> Optional[str]:
    """
    Call the OpenAI API with the given prompt.

    Args:
        prompt_str (str): The prompt to send to the API.

    Returns:
        Optional[str]: The API response content, or None if there was an error.
    """
    try:
        logger.info(f"Sending prompt to OpenAI: {prompt_str[:50]}...")
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
        logger.info(f"Received response from OpenAI: {response[:50]}...")
        return response
    except Exception as e:
        logger.error(f"Error in API call: {e}")
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




# MAIN =====

def main():
    if COMPARISON_TYPE == 'memory':
        output_root_dir = 'responses_by_memory'
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

    elif COMPARISON_TYPE in ['scripts', 'score', 'rank']:
        output_root_dir = f'responses_by_{COMPARISON_TYPE}'
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