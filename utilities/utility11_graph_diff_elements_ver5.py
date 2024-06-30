import os
import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict
from scipy.interpolate import make_interp_spline

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

def create_bar_chart(data: Dict[str, pd.DataFrame], element: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    if element == 'overall':
        bar_data = {film: df['similarity-mean'].mean() for film, df in data.items()}
    else:
        bar_data = {film: df[f'{element}-overall'].mean() for film, df in data.items()}
    
    sorted_data = sorted(bar_data.items(), key=lambda x: x[1], reverse=True)
    films, scores = zip(*sorted_data)
    
    plt.bar(films, scores)
    plt.title(f"GenAI {title}", fontsize=16)
    plt.ylabel('Similarity Score', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    for i, v in enumerate(scores):
        plt.text(i, v + 1, f'{v:.2f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def create_box_whisker(data: Dict[str, pd.DataFrame], element: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    if element == 'overall':
        plot_data = pd.DataFrame({film: df['similarity-mean'] for film, df in data.items()})
    else:
        plot_data = pd.DataFrame({
            film: df[[col for col in df.columns if col.startswith(f'{element}-') and col != f'{element}-overall']].melt()['value']
            for film, df in data.items()
        })
    
    if plot_data.empty:
        print(f"No data to plot for {element}. Skipping this plot.")
        return
    
    # Calculate mean values for sorting
    mean_values = plot_data.mean().sort_values(ascending=False)
    plot_data = plot_data[mean_values.index]
    
    sns.boxplot(data=plot_data)
    plt.title(f"GenAI {title}", fontsize=16)
    plt.ylabel('Similarity Score', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def create_kde_plot(data: Dict[str, pd.DataFrame], element: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    if element == 'overall':
        plot_data = pd.DataFrame({film: df['similarity-mean'] for film, df in data.items()})
    else:
        plot_data = pd.DataFrame({
            film: df[[col for col in df.columns if col.startswith(f'{element}-') and col != f'{element}-overall']].melt()['value']
            for film, df in data.items()
        })
    
    if plot_data.empty:
        print(f"No data to plot for {element}. Skipping this plot.")
        return
    
    for film in plot_data.columns:
        sns.kdeplot(data=plot_data[film], label=film, shade=True)
    
    plt.title(f"GenAI {title}", fontsize=16)
    plt.xlabel('Similarity Score', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.legend(title='Films', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

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
    plt.title(f"GenAI {title}", fontsize=16)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_parallel_coordinates(data: Dict[str, pd.DataFrame], title: str, filename: str):
    elements = ['similarity-mean', 'characters-overall', 'plot-overall', 'setting-overall', 'themes-overall']
    labels = ['Overall', 'Characters', 'Plot', 'Setting', 'Themes']
    plt.figure(figsize=(12, 8))
    
    for film, df in data.items():
        means = [df[e].mean() for e in elements]
        stds = [df[e].std() for e in elements]
        
        plt.plot(labels, means, marker='o', label=film)
        plt.fill_between(labels, np.array(means) - np.array(stds), np.array(means) + np.array(stds), alpha=0.2)
    
    plt.ylabel('Similarity Score')
    plt.title(f"GenAI {title}", fontsize=16)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def process_and_plot_data(all_data: Dict[str, pd.DataFrame], ref_film: str, ref_year: str):
    title_base = f"Similarity comparison with {ref_film} ({ref_year})"
    output_base = f"{ref_film.replace(' ', '_')}_{ref_year}"

    elements = ['overall', 'characters', 'plot', 'setting', 'themes']
    
    for element in elements:
        title = f"{element.capitalize()} {title_base}"
        
        # Create bar chart
        create_bar_chart(all_data, element, title, os.path.join(OUTPUT_ROOT_DIR, f"bar_chart_{element}_{output_base}.png"))
        
        # Create box and whisker plot
        create_box_whisker(all_data, element, title, os.path.join(OUTPUT_ROOT_DIR, f"box_whisker_{element}_{output_base}.png"))
        
        # Create KDE plot
        create_kde_plot(all_data, element, title, os.path.join(OUTPUT_ROOT_DIR, f"kde_{element}_{output_base}.png"))
    
    # Create radar chart
    create_radar_chart(all_data, f"Element comparison {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"radar_chart_{output_base}.png"))
    
    # Create parallel coordinates plot
    create_parallel_coordinates(all_data, f"Element comparison {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"parallel_coordinates_{output_base}.png"))


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