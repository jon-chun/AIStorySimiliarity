import os
import pickle
import json

INPUT_DIR = os.path.join('..', 'data', 'film_similarity_by_score_genai')
INPUT_FILENAME = 'similarity_by_score_genai_raiders-of-the-lost-ark_titanic.pkl'
INPUT_FULLPATH = os.path.join(INPUT_DIR, INPUT_FILENAME)

def read_and_verify_pkl(input_file_path):
    # Read the pickle file
    with open(input_file_path, 'rb') as f:
        data = pickle.load(f)
    
    # Convert the dictionary to a JSON formatted string
    json_data = json.dumps(data, indent=4)
    
    # Print the JSON formatted string to the screen
    print(json_data)

def main():
    
    
    read_and_verify_pkl(INPUT_FULLPATH)

if __name__ == '__main__':
    main()
