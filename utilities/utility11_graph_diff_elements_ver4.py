import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_elements_summary'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'figures_diff_elements'))

# Ensure output directory exists
os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 12

def clean_film_name(film_name: str) -> str:
    return ' '.join(word.capitalize() for word in film_name.replace('-', ' ').split())

def extract_film_info(filename: str) -> Tuple[str, str, str, str]:
    pattern = r"summary_diff_elements_elements_(.+)_(\d{4})_(.+)_(\d{4})\.csv"
    match = re.match(pattern, filename)
    if match:
        return clean_film_name(match.group(1)), match.group(2), clean_film_name(match.group(3)), match.group(4)
    return "", "", "", ""

def read_csv_file(file_path: str) -> Tuple[pd.DataFrame, str, str, str, str]:
    df = pd.read_csv(file_path)
    ref_film, ref_year, test_film, test_year = extract_film_info(os.path.basename(file_path))
    return df, ref_film, ref_year, test_film, test_year

def compute_similarity_mean(df: pd.DataFrame) -> pd.DataFrame:
    overall_columns = ['characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    df['similarity-mean'] = df[overall_columns].mean(axis=1)
    return df

def clean_feature_labels(columns: List[str]) -> List[str]:
    elements = ['characters', 'plot', 'setting', 'themes']
    return [col.split('-')[-1] if any(col.startswith(e) for e in elements) else col for col in columns]

# ... (keep the existing create_boxplot, create_kde_plot, and create_violin_plot functions)

def create_heatmap(data: Dict[str, pd.DataFrame], element: str, title: str, filename: str):
    plt.figure(figsize=(12, 10))
    if element == 'overall':
        heatmap_data = pd.DataFrame({film: [df['similarity-mean'].mean()] for film, df in data.items()}, 
                                    index=['Overall Similarity'])
    else:
        heatmap_data = pd.DataFrame({film: [df[f'{element}-overall'].mean()] for film, df in data.items()}, 
                                    index=[f'{element.capitalize()} Overall'])
    
    sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd', fmt='.2f')
    plt.title(title, fontsize=16)
    plt.ylabel('')  # Remove y-axis label as it's redundant
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def process_and_plot_data(all_data: Dict[str, pd.DataFrame], ref_film: str, ref_year: str):
    title_base = f"Similarity comparison with {ref_film} ({ref_year})"
    output_base = f"{ref_film.replace(' ', '_')}_{ref_year}"

    elements = ['overall', 'characters', 'plot', 'setting', 'themes']
    
    for element in elements:
        title = f"{element.capitalize()} {title_base}"
        
        # Create heatmap
        create_heatmap(all_data, element, title, os.path.join(OUTPUT_ROOT_DIR, f"heatmap_{element}_{output_base}.png"))
    
    # Create radar chart
    create_radar_chart(all_data, f"Element comparison {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"radar_chart_{output_base}.png"))
    
    # Create parallel coordinates plot
    create_parallel_coordinates(all_data, f"Element comparison {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"parallel_coordinates_{output_base}.png"))

import numpy as np

def create_radar_chart(data: Dict[str, pd.DataFrame], title: str, filename: str):
    elements = ['similarity-mean', 'characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    labels = ['Overall', 'Characters', 'Plot', 'Setting', 'Themes']
    n_elements = len(elements)
    angles = [n / float(n_elements) * 2 * np.pi for n in range(n_elements)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    for film, df in data.items():
        values = [df[e].mean() for e in elements]
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=film)
        ax.fill(angles, values, alpha=0.1)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_parallel_coordinates(data: Dict[str, pd.DataFrame], title: str, filename: str):
    elements = ['similarity-mean', 'characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    labels = ['Overall', 'Characters', 'Plot', 'Setting', 'Themes']
    plt.figure(figsize=(12, 8))
    for film, df in data.items():
        values = [df[e].mean() for e in elements]
        plt.plot(labels, values, marker='o', label=film)
    plt.ylabel('Similarity Score')
    plt.title(title, fontsize=16)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    all_data = {}
    ref_film, ref_year = "", ""
    
    for filename in os.listdir(INPUT_ROOT_DIR):
        if filename.endswith('.csv'):
            file_path = os.path.join(INPUT_ROOT_DIR, filename)
            df, ref_film, ref_year, test_film, test_year = read_csv_file(file_path)
            df = compute_similarity_mean(df)
            all_data[f"{test_film} ({test_year})"] = df
    
    # Save the combined dataframe
    combined_df = pd.concat(all_data.values(), keys=all_data.keys())
    combined_df.to_csv(os.path.join(OUTPUT_ROOT_DIR, "summary_diff_all_elements.csv"))
    
    process_and_plot_data(all_data, ref_film, ref_year)
    print(f"Figures for comparisons with {ref_film} have been saved in {OUTPUT_ROOT_DIR}")

if __name__ == "__main__":
    main()