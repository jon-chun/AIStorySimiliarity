import os
import pandas as pd

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary_raw'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))

# Ensure the output directory exists
os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

# Desired column names in the output files
desired_columns = [
    "reference_film", "test_film", "version_number", "characters-overall", "characters-backstory",
    "characters-strengths", "characters-weakness", "characters-psychology", "characters-beliefs",
    "characters-motivations", "characters-social_dynamics", "plot-overall", "plot-protagonist_introduction",
    "plot-inciting_incident", "plot-rising_action", "plot-climax", "plot-resolution", "plot-consequences",
    "plot-final_outcome", "plot-loose_ends", "plot-subplots", "setting-overall", "setting-time_period",
    "setting-geographical_location", "setting-cultural_context", "setting-social_class",
    "setting-ideology_and_beliefs", "setting-economic_and_political_context", "themes-overall", "themes-main_theme",
    "themes-secondary_themes", "themes-tertiary_themes", "themes-resolution_main_theme",
    "themes-resolution_secondary_themes", "themes-resolution_tertiary_themes"
]

def reformat_file(input_file, output_file):
    df = pd.read_csv(input_file)

    # Create new columns
    df['reference_film'] = 'elements_raiders-of-the-lost-ark_1981'
    df['test_film'] = df.apply(lambda row: f"{row['test_film']}_{row['test_year']}", axis=1)
    
    # Create a new DataFrame with desired columns
    new_df = pd.DataFrame()
    new_df['reference_film'] = df['reference_film']
    new_df['test_film'] = df['test_film']
    new_df['version_number'] = df['version_number']
    new_df['characters-overall'] = df['characters_similarity_overall']
    new_df['characters-backstory'] = df['characters_backstory']
    new_df['characters-strengths'] = df['characters_strengths']
    new_df['characters-weakness'] = df['characters_weakness']
    new_df['characters-psychology'] = df['characters_psychology']
    new_df['characters-beliefs'] = df['characters_beliefs']
    new_df['characters-motivations'] = df['characters_motivations']
    new_df['characters-social_dynamics'] = df['characters_social_dynamics']
    new_df['plot-overall'] = df['plot_similarity_overall']
    new_df['plot-protagonist_introduction'] = df['plot_protagonist_intro']
    new_df['plot-inciting_incident'] = df['plot_inciting_incident']
    new_df['plot-rising_action'] = df['plot_rising_action']
    new_df['plot-climax'] = df['plot_climax']
    new_df['plot-resolution'] = df['plot_resolution']
    new_df['plot-consequences'] = df['plot_consequences']
    new_df['plot-final_outcome'] = df['plot_final_outcome']
    new_df['plot-loose_ends'] = df['plot_loose_ends']
    new_df['plot-subplots'] = df['plot_subplots']
    new_df['setting-overall'] = df['setting_similarity_overall']
    new_df['setting-time_period'] = df['setting_time_period']
    new_df['setting-geographical_location'] = df['setting_geographical_location']
    new_df['setting-cultural_context'] = df['setting_cultural_context']
    new_df['setting-social_class'] = df['setting_social_class']
    new_df['setting-ideology_and_beliefs'] = df['setting_ideology_and_beliefs']
    new_df['setting-economic_and_political_context'] = df['setting_economic_and_political_context']
    new_df['themes-overall'] = df['themes_similarity_overall']
    new_df['themes-main_theme'] = df['themes_main_theme']
    new_df['themes-secondary_themes'] = df['themes_secondary_themes']
    new_df['themes-tertiary_themes'] = df['themes_tertiary_themes']
    new_df['themes-resolution_main_theme'] = df['themes_resolution_main_them']
    new_df['themes-resolution_secondary_themes'] = df['themes_resolution_secondary_themes']
    new_df['themes-resolution_tertiary_themes'] = df['themes_resolution_tertiary_themes']

    # Write the reformatted DataFrame to the output file
    print(f'  IN reformat_file(): writing new_df.shape={new_df.shape}')
    new_df.to_csv(output_file, index=False)

# Iterate over all the summary_*.csv files in the input directory
for filename in os.listdir(INPUT_ROOT_DIR):
    if filename.startswith("summary_") and filename.endswith(".csv"):
        print(f'PROCESSING: filename={filename}')
        input_file = os.path.join(INPUT_ROOT_DIR, filename)
        output_file = os.path.join(OUTPUT_ROOT_DIR, filename)
        reformat_file(input_file, output_file)
