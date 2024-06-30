import os
import re
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import List, Tuple, Dict
from scipy.interpolate import make_interp_spline

# Set up input and output directories
cwd = os.getcwd()
INPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_scripts_summary'))
OUTPUT_ROOT_DIR = os.path.abspath(os.path.join(cwd, '..', 'data', 'graph_diff_scripts'))

# Ensure output directory exists
os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 12

def clean_film_name(film_name: str) -> str:
    return ' '.join(word.capitalize() for word in film_name.replace('-', ' ').split())

def extract_film_info(filename: str) -> Tuple[str, str]:
    pattern = r"summary_diff_scripts_(.+)_(.+)\.csv"
    match = re.match(pattern, filename)
    if match:
        return clean_film_name(match.group(1)), clean_film_name(match.group(2))
    return "", ""


def read_json_file(file_path: str) -> Tuple[dict, str, str]:
    with open(file_path, 'r') as f:
        data = json.load(f)
    ref_film, test_film = extract_film_info(os.path.basename(file_path))
    return data, ref_film, test_film

def extract_film_info(filename: str) -> Tuple[str, str]:
    pattern = r"similarity-by-score_scripts_(.+)_(.+)_ver\d+\.json"
    match = re.match(pattern, filename)
    if match:
        return clean_film_name(match.group(1)), clean_film_name(match.group(2))
    return "", ""


def read_csv_file(file_path: str) -> Tuple[pd.DataFrame, str, str]:
    df = pd.read_csv(file_path)
    ref_film, test_film = extract_film_info(os.path.basename(file_path))
    return df, ref_film, test_film

def process_json_data(json_data: dict) -> dict:
    processed_data = {
        'similarity_overall': json_data['similarity_overall']
    }
    for i in range(1, 5):
        feature_key = f'feature_{i}'
        processed_data[f'{feature_key}_value'] = json_data[feature_key]['value']
        processed_data[f'{feature_key}_description'] = json_data[feature_key]['description']
    return processed_data

def create_bar_chart(data: Dict[str, List[dict]], feature: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    print(f"Debug: Feature = {feature}")
    print(f"Debug: Data keys = {list(data.keys())}")
    
    if feature == 'similarity_overall':
        bar_data = {film: np.mean([d[feature] for d in versions]) for film, versions in data.items()}
    else:
        bar_data = {film: np.mean([d[f'{feature}_value'] for d in versions]) for film, versions in data.items()}
    
    print(f"Debug: bar_data = {bar_data}")
    
    sorted_data = sorted(bar_data.items(), key=lambda x: x[1], reverse=True)
    print(f"Debug: sorted_data = {sorted_data}")
    
    if not sorted_data:
        print(f"Warning: No data to plot for {feature}")
        return
    
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

def create_box_whisker(data: Dict[str, pd.DataFrame], feature: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    plot_data = pd.DataFrame({film: df[f'{feature}_value'] for film, df in data.items()})
    
    sns.boxplot(data=plot_data)
    plt.title(f"GenAI {title}", fontsize=16)
    plt.ylabel('Similarity Score', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_kde_plot(data: Dict[str, pd.DataFrame], feature: str, title: str, filename: str):
    plt.figure(figsize=(12, 6))
    plot_data = pd.DataFrame({film: df[f'{feature}_value'] for film, df in data.items()})
    
    for film in plot_data.columns:
        sns.kdeplot(data=plot_data[film], label=film, fill=True)
    
    plt.title(f"GenAI {title}", fontsize=16)
    plt.xlabel('Similarity Score', fontsize=14)
    plt.ylabel('Density', fontsize=14)
    plt.legend(title='Films', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_radar_chart(data: Dict[str, pd.DataFrame], title: str, filename: str):
    features = ['feature_1_value', 'feature_2_value', 'feature_3_value', 'feature_4_value', 'similarity_overall']
    labels = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Overall']
    n_features = len(features)
    angles = [n / float(n_features) * 2 * np.pi for n in range(n_features)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    for film, df in data.items():
        values = [df[f].mean() for f in features]
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

def create_parallel_coordinates_with_std(data: Dict[str, pd.DataFrame], title: str, filename: str):
    features = ['feature_1_value', 'feature_2_value', 'feature_3_value', 'feature_4_value', 'similarity_overall']
    labels = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4', 'Overall']
    
    feature_stats = {feature: {'mean': np.mean([df[feature].mean() for df in data.values()]),
                               'std': np.mean([df[feature].std() for df in data.values()])}
                     for feature in features}
    
    sorted_features = sorted(feature_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
    sorted_labels = [labels[features.index(f[0])] for f in sorted_features]
    sorted_features = [f[0] for f in sorted_features]

    plt.figure(figsize=(14, 10))
    
    line_styles = [('dotted', (0, (1, 1))), ('dashed', (0, (5, 5))), ('dashdot', (0, (3, 5, 1, 5))), ('loosely dotted', (0, (1, 10))), ('solid', '-')]
    
    mean_lines = []
    for i, (feature, style) in enumerate(zip(sorted_features, line_styles)):
        stats = feature_stats[feature]
        line = plt.axhline(y=stats['mean'], color='red', linestyle=style[1], linewidth=3, alpha=0.5)
        mean_lines.append(line)
        plt.text(i, stats['mean'], f'{stats["mean"]:.2f}', ha='center', va='bottom')

    data_lines = []
    for film, df in data.items():
        means = [df[f].mean() for f in sorted_features]
        stds = [df[f].std() for f in sorted_features]
        
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
    plt.title(f"GenAI {title}", fontsize=16)
    plt.ylim(0, 100)

    film_legend = plt.legend(handles=data_lines, title="Films", loc='lower left', bbox_to_anchor=(0.05, 0.05))
    plt.gca().add_artist(film_legend)

    mean_legend_elements = [Line2D([0], [0], color='red', lw=3, label=label, linestyle=style[1]) 
                            for label, style in zip(sorted_labels, line_styles)]
    mean_legend = plt.legend(handles=mean_legend_elements, title="Feature Means", loc='lower left', bbox_to_anchor=(0.05, 0.3))

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()


def process_and_plot_data(all_data: Dict[str, List[dict]], ref_film: str):
    title_base = f"Similarity comparison with {ref_film}"
    output_base = f"{ref_film.replace(' ', '_')}"

    features = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'similarity_overall']
    
    for feature in features:
         title = f"{feature.capitalize()} {title_base}"
        
        create_bar_chart(all_data, feature, title, os.path.join(OUTPUT_ROOT_DIR, f"bar_chart_{feature}_{output_base}.png"))
        create_box_whisker(all_data, feature, title, os.path.join(OUTPUT_ROOT_DIR, f"box_whisker_{feature}_{output_base}.png"))
        create_kde_plot(all_data, feature, title, os.path.join(OUTPUT_ROOT_DIR, f"kde_{feature}_{output_base}.png"))
    
    create_radar_chart(all_data, f"Feature comparison {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"radar_chart_{output_base}.png"))
    create_parallel_coordinates_with_std(all_data, f"Feature comparison with std {title_base}", os.path.join(OUTPUT_ROOT_DIR, f"parallel_coordinates_std_{output_base}.png"))

def main():
    print(f"Debug: INPUT_ROOT_DIR = {INPUT_ROOT_DIR}")
    
    all_data = {}
    ref_film = ""
    
    for root, dirs, files in os.walk(INPUT_ROOT_DIR):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                json_data, ref_film, test_film = read_json_file(file_path)
                processed_data = process_json_data(json_data)
                
                if test_film not in all_data:
                    all_data[test_film] = []
                all_data[test_film].append(processed_data)
    
    print(f"Debug: all_data keys = {list(all_data.keys())}")
    print(f"Debug: Sample data for first film = {all_data[list(all_data.keys())[0]][0] if all_data else 'No data'}")
    
    # Create a DataFrame from the processed data
    all_df = pd.DataFrame([
        {**{'film': film, 'version': i}, **data}
        for film, versions in all_data.items()
        for i, data in enumerate(versions)
    ])
    
    all_df.to_csv(os.path.join(OUTPUT_ROOT_DIR, "summary_diff_all_scripts.csv"), index=False)
    
    process_and_plot_data(all_data, ref_film)
    print(f"Figures for comparisons with {ref_film} have been saved in {OUTPUT_ROOT_DIR}")

if __name__ == "__main__":
    main()