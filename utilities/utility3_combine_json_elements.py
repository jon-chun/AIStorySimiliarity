import os
import json

# Constants
INPUT_ROOT_DIR = os.path.join('..', 'data', 'film_narrative_elements')
ELEMENTS = ['characters', 'plot', 'setting', 'themes']

# Instructions templates
INSTRUCTIONS_OVERALL = "\n###NARRATIVE ELEMENTS:\m\n"
INSTRUCTIONS_CHARACTERS = "\n###CHARACTERS:\n\n"
INSTRUCTIONS_PLOT = "\n###PLOT:\n\n"
INSTRUCTIONS_SETTING = "\n###SETTING:\n\n"
INSTRUCTIONS_THEMES = "\n###THEMES:\n\n"

def extract_film_info(subdir):
    parts = subdir.split('_')
    year = parts[-1]
    name = '_'.join(parts[1:-1])
    return name, year

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def combine_json_elements(input_dir, film_name, film_year):
    # combined_data = INSTRUCTIONS_OVERALL
    combined_data = f"###FILM: {film_name}\n\n"
    combined_data += f"###YEAR: {film_year}\n\n"
    
    film_name_clean = film_name.replace('-',' ').upper()
    for element in ELEMENTS:
        file_name = f"elements_{film_name}_{film_year}_{element}.json"
        file_path = os.path.join(input_dir, file_name)
        
        if os.path.exists(file_path):
            element_data = read_json_file(file_path)
            

            
            if element == 'characters':
                combined_data += INSTRUCTIONS_CHARACTERS

            elif element == 'plot':
                combined_data += INSTRUCTIONS_PLOT
            elif element == 'setting':
                combined_data += INSTRUCTIONS_SETTING
            elif element == 'themes':
                combined_data += INSTRUCTIONS_THEMES
            
            combined_data += json.dumps(element_data, indent=2)
        else:
            print(f"Warning: {file_name} not found in {input_dir}")

    return combined_data

def main():
    for subdir in os.listdir(INPUT_ROOT_DIR):
        input_dir = os.path.join(INPUT_ROOT_DIR, subdir)
        
        if os.path.isdir(input_dir):
            film_name, film_year = extract_film_info(subdir)
            output_filename = f"elements_{film_name}_{film_year}_all.json"
            output_path = os.path.join(input_dir, output_filename)
            
            combined_data = combine_json_elements(input_dir, film_name, film_year)
            
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(combined_data)
            
            print(f"Created combined file: {output_path}")

if __name__ == "__main__":
    main()