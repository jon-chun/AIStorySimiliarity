import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Dict

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_elements_summary'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'plots_diff_elements'))

# Ensure output directory exists
os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

def read_csv_files(input_dir: str) -> pd.DataFrame:
    """Read all CSV files in the input directory and concatenate them."""
    all_data = []
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_dir, filename)
            df = pd.read_csv(file_path)
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

def compute_similarity_mean(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the similarity mean for each row."""
    overall_columns = ['characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    df['similarity-mean'] = df[overall_columns].mean(axis=1)
    return df

def create_boxplot(data: pd.DataFrame, columns: List[str], title: str, filename: str):
    """Create and save a box-whisker plot."""
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=data[columns], orient='h')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_ROOT_DIR, filename), dpi=300)
    plt.close()

def process_and_plot_data(df: pd.DataFrame):
    """Process the data and create all required plots."""
    # Plot a: similarity-mean and 4 main elements-overall
    main_columns = ['similarity-mean', 'characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    create_boxplot(df, main_columns, 'Overall Similarity and Main Elements', 'overall_similarity.png')

    # Plot b: character features
    character_columns = [col for col in df.columns if col.startswith('characters-') and col != 'characters-overall']
    create_boxplot(df, character_columns, 'Character Features', 'character_features.png')

    # Plot c: plot features
    plot_columns = [col for col in df.columns if col.startswith('plot-') and col != 'plot-overall']
    create_boxplot(df, plot_columns, 'Plot Features', 'plot_features.png')

    # Plot d: setting features
    setting_columns = [col for col in df.columns if col.startswith('setting-') and col != 'setting-overall']
    create_boxplot(df, setting_columns, 'Setting Features', 'setting_features.png')

    # Plot e: themes features
    themes_columns = [col for col in df.columns if col.startswith('themes-') and col != 'themes-overall']
    create_boxplot(df, themes_columns, 'Themes Features', 'themes_features.png')

def main():
    # Read all CSV files
    all_data = read_csv_files(INPUT_ROOT_DIR)

    # Compute similarity mean
    all_data = compute_similarity_mean(all_data)

    # Process data and create plots
    process_and_plot_data(all_data)

    print(f"Plots have been saved in {OUTPUT_ROOT_DIR}")

if __name__ == "__main__":
    main()import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_elements_summary'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'plots_diff_elements'))

# Ensure output directory exists
os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 12

def extract_film_info(filename: str) -> Tuple[str, str, str, str]:
    """Extract reference and test film information from the filename."""
    pattern = r"summary_diff_elements_elements_(.+)_(\d{4})_(.+)_(\d{4})\.csv"
    match = re.match(pattern, filename)
    if match:
        return match.group(1), match.group(2), match.group(3), match.group(4)
    return "", "", "", ""

def read_csv_files(input_dir: str) -> List[Tuple[pd.DataFrame, str, str, str, str]]:
    """Read all CSV files in the input directory and return a list of DataFrames with film info."""
    all_data = []
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_dir, filename)
            df = pd.read_csv(file_path)
            ref_film, ref_year, test_film, test_year = extract_film_info(filename)
            all_data.append((df, ref_film, ref_year, test_film, test_year))
    return all_data

def compute_similarity_mean(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the similarity mean for each row."""
    overall_columns = ['characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    df['similarity-mean'] = df[overall_columns].mean(axis=1)
    return df

def create_boxplot_with_kde(data: pd.DataFrame, columns: List[str], title: str, filename: str, element: str):
    """Create and save a box-whisker plot with KDE."""
    plt.figure(figsize=(14, 8))
    
    # Create box plot
    ax = sns.boxplot(data=data[columns], orient='h', width=0.6)
    
    # Create KDE plot
    for i, col in enumerate(columns):
        sns.kdeplot(data=data[col], ax=ax, vertical=True, color='r', linewidth=2, alpha=0.6)
    
    plt.title(title, fontsize=16)
    plt.xlabel('Similarity Score', fontsize=14)
    plt.ylabel('Features', fontsize=14)
    
    # Simplify y-axis labels
    y_labels = [label.get_text().replace(f'{element}-', '') for label in ax.get_yticklabels()]
    ax.set_yticklabels(y_labels)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_ROOT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

def process_and_plot_data(df: pd.DataFrame, ref_film: str, ref_year: str, test_film: str, test_year: str):
    """Process the data and create all required plots."""
    title_base = f"Similarity between {ref_film} ({ref_year})\nand {test_film} ({test_year})"
    
    # Plot a: similarity-mean and 4 main elements-overall
    main_columns = ['similarity-mean', 'characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    create_boxplot_with_kde(df, main_columns, f"Overall {title_base}", 'overall_similarity.png', '')

    # Plot b: character features
    character_columns = [col for col in df.columns if col.startswith('characters-') and col != 'characters-overall']
    create_boxplot_with_kde(df, character_columns, f"Character {title_base}", 'character_features.png', 'characters-')

    # Plot c: plot features
    plot_columns = [col for col in df.columns if col.startswith('plot-') and col != 'plot-overall']
    create_boxplot_with_kde(df, plot_columns, f"Plot {title_base}", 'plot_features.png', 'plot-')

    # Plot d: setting features
    setting_columns = [col for col in df.columns if col.startswith('setting-') and col != 'setting-overall']
    create_boxplot_with_kde(df, setting_columns, f"Setting {title_base}", 'setting_features.png', 'setting-')

    # Plot e: themes features
    themes_columns = [col for col in df.columns if col.startswith('themes-') and col != 'themes-overall']
    create_boxplot_with_kde(df, themes_columns, f"Themes {title_base}", 'themes_features.png', 'themes-')

def main():
    # Read all CSV files
    all_data = read_csv_files(INPUT_ROOT_DIR)

    for df, ref_film, ref_year, test_film, test_year in all_data:
        # Compute similarity mean
        df = compute_similarity_mean(df)

        # Process data and create plots
        process_and_plot_data(df, ref_film, ref_year, test_film, test_year)

        print(f"Plots for {ref_film} vs {test_film} have been saved in {OUTPUT_ROOT_DIR}")

if __name__ == "__main__":
    main()