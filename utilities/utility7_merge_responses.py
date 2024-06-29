import os
import shutil
import pandas as pd

# Define input and output directories
INPUT_A_DIR = os.path.join('..', 'data', 'film_similarity_by_score_genai')
INPUT_B_DIR = os.path.join('..', 'data', 'film_similarity_by_score_genai_paper10')
OUTPUT_DIR = os.path.join('..', 'data', 'film_similarity_by_score_genai_merged')

# Define the list of films
FILM_LIST = [
    "indiana-jones-and-the-dial-of-destiny",
    "indiana-jones-and-the-kingdom-of-the-crystal-skull",
    "indiana-jones-and-the-last-crusade",
    "indiana-jones-and-the-temple-of-doom",
    "la-la-land",
    "laura-croft-tomb-raider",
    "national-treasure",
    "office-space",
    # "raiders-of-the-lost-arc",
    "the-mummy",
    "titanic",
]

def copy_pkl_files(film_name):
    for input_dir in [INPUT_A_DIR, INPUT_B_DIR]:
        for filename in os.listdir(input_dir):
            if filename.endswith('.pkl') and film_name in filename:
                shutil.copy(os.path.join(input_dir, filename), OUTPUT_DIR)

def merge_csv_files(film_name):
    csv_a = None
    csv_b = None
    
    for filename in os.listdir(INPUT_A_DIR):
        if filename.endswith('.csv') and film_name in filename:
            csv_a = pd.read_csv(os.path.join(INPUT_A_DIR, filename))
            break
    
    for filename in os.listdir(INPUT_B_DIR):
        if filename.endswith('.csv') and film_name in filename:
            csv_b = pd.read_csv(os.path.join(INPUT_B_DIR, filename))
            break
    
    if csv_a is not None and csv_b is not None:
        merged_csv = pd.concat([csv_a, csv_b], ignore_index=True)
        merged_csv.to_csv(os.path.join(OUTPUT_DIR, f"{film_name}_merged.csv"), index=False)

def main():
    # Create OUTPUT_DIR if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for film_name in FILM_LIST:
        copy_pkl_files(film_name)
        merge_csv_files(film_name)

if __name__ == "__main__":
    main()