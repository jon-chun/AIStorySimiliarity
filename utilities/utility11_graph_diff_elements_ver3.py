import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Tuple

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_elements_summary'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'plots_diff_elements'))

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

def create_boxplot(data: pd.DataFrame, columns: List[str], title: str, filename: str):
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=data[columns], orient='h')
    plt.title(title, fontsize=16)
    plt.xlabel('Similarity Score', fontsize=14)
    plt.ylabel('Features', fontsize=14)
    plt.yticks(range(len(columns)), clean_feature_labels(columns))
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_kde_plot(data: pd.DataFrame, columns: List[str], title: str, filename: str):
    plt.figure(figsize=(12, 6))
    for col in columns:
        sns.kdeplot(data=data[col], shade=True, label=col.split('-')[-1])
    plt.title(title, fontsize=16)
    plt.xlabel('Similarity Score', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_violin_plot(data: pd.DataFrame, columns: List[str], title: str, filename: str):
    plt.figure(figsize=(12, 6))
    sns.violinplot(data=data[columns])
    plt.title(title, fontsize=16)
    plt.xlabel('Features', fontsize=14)
    plt.ylabel('Similarity Score', fontsize=14)
    plt.xticks(range(len(columns)), clean_feature_labels(columns), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def process_and_plot_data(df: pd.DataFrame, ref_film: str, ref_year: str, test_film: str, test_year: str):
    title_base = f"Similarity between {ref_film} ({ref_year}) and {test_film} ({test_year})"
    output_base = f"{ref_film.replace(' ', '_')}_{ref_year}_vs_{test_film.replace(' ', '_')}_{test_year}"

    elements = ['overall', 'characters', 'plot', 'setting', 'themes']
    
    for element in elements:
        if element == 'overall':
            columns = ['similarity-mean', 'characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
        else:
            columns = [col for col in df.columns if col.startswith(f'{element}-') and col != f'{element}-overall']
        
        title = f"{element.capitalize()} {title_base}"
        
        # Create boxplot
        create_boxplot(df, columns, title, os.path.join(OUTPUT_ROOT_DIR, f"boxplot_{element}_{output_base}.png"))
        
        # Create KDE plot
        create_kde_plot(df, columns, title, os.path.join(OUTPUT_ROOT_DIR, f"kde_{element}_{output_base}.png"))
        
        # Create violin plot
        create_violin_plot(df, columns, title, os.path.join(OUTPUT_ROOT_DIR, f"violin_{element}_{output_base}.png"))

def main():
    for filename in os.listdir(INPUT_ROOT_DIR):
        if filename.endswith('.csv'):
            file_path = os.path.join(INPUT_ROOT_DIR, filename)
            df, ref_film, ref_year, test_film, test_year = read_csv_file(file_path)
            df = compute_similarity_mean(df)
            process_and_plot_data(df, ref_film, ref_year, test_film, test_year)
            print(f"Plots for {ref_film} vs {test_film} have been saved in {OUTPUT_ROOT_DIR}")

if __name__ == "__main__":
    main()