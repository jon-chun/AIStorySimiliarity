import os
import re
import logging
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import List, Tuple, Dict
from scipy.interpolate import make_interp_spline


# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'figures_diff_genai'))

REFERENCE_FILM = 'raiders-of-the-lost-ark'

TEST_FILM_LIST = [
    'indiana-jones-and-the-last-crusade',
    'indiana-jones-and-the-temple-of-doom',
    'la-la-land',
    'laura-croft-tomb-raider',
    'national-treasure',
    'office-space',
    'the-mummy',
    'titanic'
]

# Ensure output directory exists
os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 12


# def log_and_print(message: str, level: str = "info"):

def log_and_print(message: str):
    # getattr(logger, level)(message)
    print(message)

def clean_film_name(film_name: str) -> str:
    return ' '.join(word.capitalize() for word in film_name.replace('_', ' ').split())

def extract_film_info(filename: str) -> Tuple[str, str]:
    pattern = r"summary_genai_(.+)_script_(.+)\.csv"
    match = re.match(pattern, filename)
    if match:
        log_and_print(f"  IN extract_film_info(): with group1: {match.group(1)}, group2: {match.group(2)}")
        return match.group(1), match.group(2)
    return "", ""

def read_csv_file(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    log_and_print(f"df.shape(): {df.shape}")
    return df

def compute_similarity_mean(df: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    log_and_print(f"Computing similarity mean for DataFrame with shape: {df.shape}")
    
    overall_columns = ['characters_similarity_overall', 'plot_similarity_overall', 'setting_similarity_overall', 'themes_similarity_overall']
    means = df[overall_columns].mean()
    means['similarity_mean'] = means.mean()
    
    log_and_print("Computed means:")
    log_and_print(means)
    return means, df[overall_columns]


def clean_feature_labels(columns: List[str]) -> List[str]:
    elements = ['characters', 'plot', 'setting', 'themes']
    return [col.split('_')[-1] if any(col.startswith(e) for e in elements) else col for col in columns]

def create_bar_chart(data_means: Dict[str, pd.Series], element: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    log_and_print(f"Creating bar chart for {element}")
    
    if element == 'overall':
        bar_data = {film: values['similarity_mean'] for film, values in data_means.items()}
    else:
        bar_data = {film: values[f'{element}_similarity_overall'] for film, values in data_means.items()}
    
    log_and_print(f"Bar data for {element}: {bar_data}")

    sorted_data = sorted(bar_data.items(), key=lambda x: x[1], reverse=True)
    films, scores = zip(*sorted_data)
    
    plt.bar(films, scores)
    plt.title(f"[GenAI] {title}", fontsize=16)
    plt.ylabel('Similarity Score', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    for i, v in enumerate(scores):
        plt.text(i, v + 1, f'{v:.2f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def create_box_whisker(data_original: Dict[str, pd.DataFrame], element: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    
    if element == 'overall':
        plot_data = pd.DataFrame({film: df['similarity_mean'] for film, df in data_original.items()})
    else:
        plot_data = pd.DataFrame({film: df[f'{element}_similarity_overall'] for film, df in data_original.items()})


    if plot_data.empty:
        log_and_print(f"No data to plot for {element}. Skipping this plot.")
        return
    
    # Calculate mean values for sorting
    mean_values = plot_data.mean().sort_values(ascending=False)
    plot_data = plot_data[mean_values.index]
    
    sns.boxplot(data=plot_data)
    plt.title(f"[GenAI] {title}", fontsize=16)
    plt.ylabel('Similarity Score', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_kde_plot(data_original: Dict[str, pd.DataFrame], element: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    
    if element == 'overall':
        plot_data = pd.DataFrame({film: df.mean(axis=1) for film, df in data_original.items()})
    else:
        plot_data = pd.DataFrame({film: df[f'{element}_similarity_overall'] for film, df in data_original.items()})
    
    if plot_data.empty:
        log_and_print(f"No data to plot for {element}. Skipping this plot.")
        return
    
    for film in plot_data.columns:
        sns.kdeplot(data=plot_data[film], label=film, fill=True)
    
    plt.title(f"[GenAI] {title}", fontsize=16)
    plt.xlabel('Similarity Score', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.legend(title='Films', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_radar_chart(data_means: Dict[str, pd.Series], title: str, filename: str):
    elements = ['similarity_mean', 'characters_similarity_overall', 'plot_similarity_overall', 'setting_similarity_overall', 'themes_similarity_overall']
    labels = ['Overall', 'Characters', 'Plot', 'Setting', 'Themes']
    n_elements = len(elements)
    angles = [n / float(n_elements) * 2 * np.pi for n in range(n_elements)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    for film, means in data_means.items():
        values = [means[e] for e in elements]
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=film)
        ax.fill(angles, values, alpha=0.1)

    # ... rest of the function remains the same

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title(f"[GenAI] {title}", fontsize=16)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_parallel_coordinates(data: Dict[str, pd.DataFrame], title: str, filename: str):
    elements = ['characters_similarity_overall', 'plot_similarity_overall', 'setting_similarity_overall', 'themes_similarity_overall']
    labels = ['Characters', 'Plot', 'Setting', 'Themes']
    
    element_stats = {element: {'mean': np.mean([df[element].mean() for df in data.values()]),
                               'std': np.mean([df[element].std() for df in data.values()])}
                     for element in elements}
    
    sorted_elements = sorted(element_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
    sorted_labels = [labels[elements.index(e[0])] for e in sorted_elements]
    sorted_elements = [e[0] for e in sorted_elements]

    plt.figure(figsize=(14, 10))
    
    line_styles = [('dotted', (0, (1, 1))), ('dashed', (0, (5, 5))), ('dashdot', (0, (3, 5, 1, 5))), ('loosely dotted', (0, (1, 10)))]
    
    mean_lines = []
    for i, (element, style) in enumerate(zip(sorted_elements, line_styles)):
        stats = element_stats[element]
        line = plt.axhline(y=stats['mean'], color='red', linestyle=style[1], linewidth=3, alpha=0.5)
        mean_lines.append(line)
        plt.text(i, stats['mean'], f'{stats["mean"]:.2f}', ha='center', va='bottom')

    data_lines = []
    for film, df in data.items():
        means = [df[e].mean() for e in sorted_elements]
        line, = plt.plot(sorted_labels, means, marker='o', label=film)
        data_lines.append(line)
    
    plt.ylabel('Similarity Score')
    plt.title(f"[GenAI] {title}", fontsize=16)
    plt.ylim(0, 100)

    film_legend = plt.legend(handles=data_lines, title="Films", loc='lower left', bbox_to_anchor=(0.05, 0.05))
    plt.gca().add_artist(film_legend)

    mean_legend_elements = [Line2D([0], [0], color='red', lw=3, label=label, linestyle=style[1]) 
                            for label, style in zip(sorted_labels, line_styles)]
    mean_legend = plt.legend(handles=mean_legend_elements, title="Element Means", loc='lower left', bbox_to_anchor=(0.05, 0.3))

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_parallel_coordinates_with_std(data: Dict[str, pd.DataFrame], title: str, filename: str):
    elements = ['characters_similarity_overall', 'plot_similarity_overall', 'setting_similarity_overall', 'themes_similarity_overall']
    labels = ['Characters', 'Plot', 'Setting', 'Themes']
    
    element_stats = {element: {'mean': np.mean([df[element].mean() for df in data.values()]),
                               'std': np.mean([df[element].std() for df in data.values()])}
                     for element in elements}
    
    sorted_elements = sorted(element_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
    sorted_labels = [labels[elements.index(e[0])] for e in sorted_elements]
    sorted_elements = [e[0] for e in sorted_elements]

    plt.figure(figsize=(14, 10))
    
    line_styles = [('dotted', (0, (1, 1))), ('dashed', (0, (5, 5))), ('dashdot', (0, (3, 5, 1, 5))), ('loosely dotted', (0, (1, 10)))]
    
    mean_lines = []
    for i, (element, style) in enumerate(zip(sorted_elements, line_styles)):
        stats = element_stats[element]
        line = plt.axhline(y=stats['mean'], color='red', linestyle=style[1] , linewidth=3, alpha=0.5)
        mean_lines.append(line)
        plt.text(i, stats['mean'], f'{stats["mean"]:.2f}', ha='center', va='bottom')

    data_lines = []
    for film, df in data.items():
        means = [df[e].mean() for e in sorted_elements]
        stds = [df[e].std() for e in sorted_elements]
        
        x_smooth = np.linspace(0, len(sorted_labels) - 1, 300)
        spl = make_interp_spline(range(len(sorted_labels)), means, k=3)
        y_smooth = spl(x_smooth)
        
        spl_upper = make_interp_spline(range(len(sorted_labels)), np.array(means) + np.array(stds), k=3)
        spl_lower = make_interp_spline(range(len(sorted_labels)), np.array(means) - np.array(stds), k=3)
        y_upper = spl_upper(x_smooth)
        y_lower = spl_lower(x_smooth)
        
        line, = plt.plot(x_smooth, y_smooth, label=film)
        plt.fill_between(x_smooth, y_lower, y_upper, alpha=0.2)
        data_lines.append(line)

    plt.xticks(range(len(sorted_labels)), sorted_labels)
    plt.ylabel('Similarity Score')
    plt.title(f"[GenAI] {title}", fontsize=16)
    plt.ylim(0, 100)

    film_legend = plt.legend(handles=data_lines, title="Films", loc='lower left', bbox_to_anchor=(0.05, 0.05))
    plt.gca().add_artist(film_legend)

    mean_legend_elements = [Line2D([0], [0], color='red', lw=3, label=label, linestyle=style[1]) 
                            for label, style in zip(sorted_labels, line_styles)]
    mean_legend = plt.legend(handles=mean_legend_elements, title="Element Means", loc='lower left', bbox_to_anchor=(0.05, 0.3))

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def process_and_plot_data(data_means: Dict[str, pd.Series], data_original: Dict[str, pd.DataFrame], REFERENCE_FILM: str):
    log_and_print(f"Processing data for {len(data_means)} test films")
    title_base = f"Similarity comparison with {REFERENCE_FILM}"
    output_base = f"{REFERENCE_FILM.replace(' ', '_')}"
    
    elements = ['overall', 'characters', 'plot', 'setting', 'themes']
    
    for element in elements:
        title = f"{element.capitalize()} {title_base}"
        
        create_bar_chart(data_means, element, title, os.path.join(OUTPUT_ROOT_DIR, f"bar_chart_{element}_{output_base}.png"))
        create_box_whisker(data_original, element, title, os.path.join(OUTPUT_ROOT_DIR, f"box_whisker_{element}_{output_base}.png"))
        create_kde_plot(data_original, element, title, os.path.join(OUTPUT_ROOT_DIR, f"kde_{element}_{output_base}.png"))
    
    create_radar_chart(data_means, f"Element comparison {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"radar_chart_{output_base}.png"))
    create_parallel_coordinates(data_means, f"Element comparison {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"parallel_coordinates_{output_base}.png"))
    create_parallel_coordinates_with_std(data_original, f"Element comparison with std {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"parallel_coordinates_std_{output_base}.png"))




def main():
    log_and_print("Starting main() function")
    all_data_means = {}
    all_data_original = {}
    
    for filename in os.listdir(INPUT_ROOT_DIR):
        if filename.endswith('.csv'):
            file_path = os.path.join(INPUT_ROOT_DIR, filename)
            reference_film, test_film = extract_film_info(filename)
            
            if reference_film == REFERENCE_FILM and test_film in TEST_FILM_LIST:
                df = read_csv_file(file_path)
                log_and_print(f"Read file: {filename}")
                log_and_print(f"DataFrame shape: {df.shape}")
                
                group_key = f"{reference_film}_{test_film}"
                means, original_data = compute_similarity_mean(df)
                all_data_means[group_key] = means
                all_data_original[group_key] = original_data
                
                log_and_print(f"Processed test film: {test_film}")
    
    # Log statistics for each group
    log_and_print("Statistics for each group:")
    for group_key, means in all_data_means.items():
        log_and_print(f"Group: {group_key}")
        for key, value in means.items():
            log_and_print(f"  {key}: {value:.2f}")

    # Modify the process_and_plot_data function to work with the new data structure
    process_and_plot_data(all_data_means, all_data_original, REFERENCE_FILM)


if __name__ == "__main__":
    main()

