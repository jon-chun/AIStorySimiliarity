import os
import json

# Configuration
VERSION_MAX = 10
ELEMENT_TYPES = ['characters', 'plot', 'setting', 'themes']
EXTENSION_TYPE = 'json' # in ['json','pkl','md']


# CUSTOMIZE file names and subdir paths
reference_film = "raiders-of-the-lost-ark"

test_film = "office-space"
test_film = 'indiana-jones-and-the-last-crusade'
test_film = 'national-treasure'

path_part1 = 'score_diff_scripts'
path_part2 = 'scripts_raiders-of-the-lost-ark_office-space'
path_part2 = 'scripts_raiders-of-the-lost-ark_indiana-jones-and-the-last-crusade'
path_part2 = 'scripts_raiders-of-the-lost-ark_national-treasure'


cwd = os.getcwd()
# output_dir = os.path.abspath(os.path.join(cwd, '..', 'data', path_part1, path_part2))

# If executing in output director
output_dir = os.path.abspath(os.path.join(cwd, '..', path_part2))

def create_empty_json_files(output_dir, reference_film, test_film):
    for element_type in ELEMENT_TYPES:
        for version in range(VERSION_MAX):
            filename = f"scripts_{reference_film}_{test_film}_elements-{element_type}_ver{version}.{EXTENSION_TYPE}"
            file_path = os.path.join(output_dir, filename)

            # Check if the file already exists
            if os.path.exists(file_path):
                print(f"Skipping: {filename} (already exists)")
            else:
                # Create an empty JSON file
                with open(file_path, 'w') as f:
                    json.dump({"content": "empty"}, f)

                print(f"CREATING: filepath: {file_path}")
                print(f"Created: {filename}")

def main():
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Call the function to create empty JSON files
    create_empty_json_files(output_dir, reference_film, test_film)

if __name__ == "__main__":
    main()