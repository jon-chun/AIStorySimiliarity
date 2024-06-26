# Iterate over every script and 

# IMPORTS =====
import os
from datetime import datetime
import logging
from openai import OpenAI


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


# SETUP OPENAI =====

# Set the OpenAI API Key in the command line shell

# LINUX CLI: export OPENAI_API_KEY="your_openai_api_key"

# WIN11 PowerShell: $env:OPENAI_API_KEY="your_openai_api_key"
#                   echo $env:OPENAI_API_KEY

# WIN11 Command Terminal: set OPENAI_API_KEY=your_openai_api_key
#                         echo %OPENAI_API_KEY%

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    SLEEP_SECONDS = 0.1

OPENAI_MODEL='gpt-3.5-turbo'
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 0.5

# Configure how many iterations to run
SAMPLE_SIZE = 30


# DEFINE CONSTANTS =====

INPUT_DIR = os.path.join('data','film_scripts_txt')

SCRIPT_REFERENCE = 'script_laura-croft-tomb-raider_2001.txt'
SCRIPT_TITLE_YEAR = 'Raiders of the Lost Ark (1981 film)'

scripts_list_full = sorted(os.listdir(INPUT_DIR))
scripts_list = [string for string in scripts_list_full if string != SCRIPT_REFERENCE]

# Select COMPARISON_TYPE_BY in ['memory','scripts','score','rank']
COMPARISON_TYPE = 'memory'

# PROMPTS =====

from prompts.prompts_compare_with_memory import prompt_similarity_to_memory_start, prompt_similarity_to_memory_middle, prompt_similarity_to_memory_end

# FUNCTIONS =====

def read_file(filename):
    try:
        file_fullpath = os.path.join(INPUT_DIR, filename)
        with open(file_fullpath, 'r', encoding='utf-8') as fp:
            file_text = fp.read()
        return file_text
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return ""
    
def save_to_file(decision, content, file_path):
    """Save content to the specified file, creating any necessary directories."""
    try:
        # Extract the directory path
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directories to {directory}")
    except OSError as e:
        logging.error(f"Error creating directories for {file_path}: {e}")   
        return
    
    try:
        decision_content = f"{decision.strip()}\n{content.strip()}\n"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(decision_content)
        logging.info(f"Successfully wrote to {file_path}")
    except IOError as e:
        logging.error(f"Error writing to {file_path}: {e}")
        

def call_openai(prompt_str):
    
    try:
        completion = openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_str,
                }
            ],
            model=OPENAI_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            # response_format={"type": "json_object"}
        )

        response = completion.choices[0].message.content
        print(f'\n\nOpenAI {OPENAI_MODEL} response: {response}\n\n')
        # return json.loads(response)
        return response

    # except json.JSONDecodeError:
    #     return response  # Return raw response if JSON decoding fails
    
    except Exception as e:
        print(f"Error in API call or JSON parsing: {e}")
        return None



def get_distance_between_one(test_n_text):
    full_prompt = (
        prompt_similarity_to_memory_start +
        test_n_text +
        prompt_similarity_to_memory_middle + 
        SCRIPT_TITLE_YEAR +
        prompt_similarity_to_memory_end
    )
    print(f'  FULL_PROMPT: {full_prompt}')
    response = call_openai(full_prompt)
    return response



def get_distance_between_two(reference_text, test_w_text):

    return abs(len(reference_text) - len(test_w_text))



def similarity_metric(reference_file, test_x_file, test_y_file):
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
        print(f"Error in similarity_metric: {e}")
        return None
    

def rank_two_by_reference(reference_file, test_a_file, test_b_file):
    try:
        result_a = similarity_metric(reference_file, test_a_file, test_b_file)
        result_b = similarity_metric(reference_file, test_b_file, test_a_file)
        return result_a if result_a[1] <= result_b[1] else result_b
    except Exception as e:
        print(f"Error in rank_two_by_reference: {e}")
        return None


def merge(reference_file, left, right):
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
        print(f"Error in merge: {e}")
        return []

def merge_sort(reference_file, files):
    if len(files) <= 1:
        return files
    try:
        mid = len(files) // 2
        left = merge_sort(reference_file, files[:mid])
        right = merge_sort(reference_file, files[mid:])
        return merge(reference_file, left, right)
    except Exception as e:
        print(f"Error in merge_sort: {e}")
        return []
    


# MAIN =====


if COMPARISON_TYPE == 'memory':
    output_root_dir = 'responses_by_memory'
    results = []
    for script_index, script_file in enumerate(scripts_list):
        print(f'PROCESSING: script #{script_index}: {script_file}')
        script_text = read_file(script_file)
        response = get_distance_between_one(script_text)
        print(f'Response: {response}')
        results.append((script_file, response))
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"memory_results_{timestamp}.csv"
    csv_path = os.path.join(output_root_dir, csv_filename)
    
    csv_content = "Script,Response\n"
    for script, response in results:
        csv_content += f"{script},{response}\n"
    
    save_to_file("Memory Comparison Results", csv_content, csv_path)

elif COMPARISON_TYPE in ['scripts', 'score', 'rank']:
    if COMPARISON_TYPE == 'scripts':
        output_root_dir = 'responses_by_scripts'
    elif COMPARISON_TYPE == 'score':
        output_root_dir = 'responses_by_score'
    elif COMPARISON_TYPE == 'rank':
        output_root_dir = 'responses_by_rank'
    else:
        print(f'ERROR: Illegal value COMPARISON_TYPE: {COMPARISON_TYPE}')
        exit() # This branch should never be hit now, defensive for future changes
    try:
        # Calculate distances for each file
        scripts_with_distances = []
        for script in scripts_list:
            try:
                _, distance = similarity_metric(SCRIPT_REFERENCE, script, script)
                scripts_with_distances.append((script, distance))
            except Exception as e:
                print(f"Error calculating distance for {script}: {e}")
        
        # Sort the scripts based on their distances
        scripts_ranked = merge_sort(SCRIPT_REFERENCE, scripts_with_distances)
        
        print("Ranked files with distances:")
        for script, distance in scripts_ranked:
            print(f"{script}: {distance}")
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{COMPARISON_TYPE}_results_{timestamp}.csv"
        csv_path = os.path.join(output_root_dir, csv_filename)
        
        csv_content = "Rank,Script,Distance\n"
        for rank, (script, distance) in enumerate(scripts_ranked, start=1):
            csv_content += f"{rank},{script},{distance}\n"
        
        save_to_file(f"{COMPARISON_TYPE.capitalize()} Comparison Results", csv_content, csv_path)
        
    except Exception as e:
        print(f"Error in main execution: {e}")
else:
    print(f'ERROR: Illegal COMPARISON_TYPE: {COMPARISON_TYPE}')
    exit()