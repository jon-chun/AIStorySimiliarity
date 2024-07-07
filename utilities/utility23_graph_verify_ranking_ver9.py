import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import numpy as np
import glob

# Set the style for the plots
plt.style.use('default')
sns.set_palette("Set2")

# Set up directories
cwd = os.getcwd()
output_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'figures_verify'))
os.makedirs(output_dir, exist_ok=True)

def normalize_film_name(name):
    return name.lower().replace(' ', '-').replace(':', '')

def read_json_files(directory, model_name):
    all_data = []
    for filename in glob.glob(os.path.join(directory, '*.json')):
        with open(filename, 'r') as f:
            data = json.load(f)
            df = pd.DataFrame.from_dict(data, orient='index')
            df['model_name'] = model_name
            df['normalized_name'] = df['name'].apply(normalize_film_name)
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)

def read_genai_summaries(directory):
    all_files = glob.glob(os.path.join(directory, "summary_diff_genai_genai_*.csv"))
    df_list = []
    for filename in all_files:
        df = pd.read_csv(filename)
        df_list.append(df)
    combined_df = pd.concat(df_list, ignore_index=True)
    
    avg_scores = combined_df.groupby('test_film')['overall'].mean().reset_index()
    avg_scores['normalized_name'] = avg_scores['test_film'].apply(lambda x: normalize_film_name(x.split('_')[0]))
    return avg_scores

def calculate_rankings(df, genai_df):
    gpt4o_ranks = df[df['model_name'] == 'gpt4o'].groupby('normalized_name')['similarity'].mean().rank(ascending=False)
    claude_ranks = df[df['model_name'] == 'claude35sonnet'].groupby('normalized_name')['similarity'].mean().rank(ascending=False)
    genai_ranks = genai_df.set_index('normalized_name')['overall'].rank(ascending=False)
    
    all_movies = list(set(gpt4o_ranks.index) | set(claude_ranks.index) | set(genai_ranks.index))
    rankings = pd.DataFrame(index=all_movies)
    rankings['GPT4o'] = gpt4o_ranks
    rankings['Claude 3.5 Sonnet'] = claude_ranks
    rankings['GenAI'] = genai_ranks
    
    return rankings.fillna(len(all_movies))

# Read data
claude_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'verify_claude35sonnet', 'verify_claude35sonnet_ranking'))
claude_df = read_json_files(claude_dir, 'claude35sonnet')

gpt4o_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'verify_gpt4o', 'verify_gpt4o_ranking'))
gpt4o_df = read_json_files(gpt4o_dir, 'gpt4o')

genai_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai_summary'))
genai_df = read_genai_summaries(genai_dir)

# Combine the dataframes
combined_df = pd.concat([gpt4o_df, claude_df])

# Calculate rankings
rankings = calculate_rankings(combined_df, genai_df)
rankings_sorted = rankings.sort_values('GenAI')

# Calculate stats
claude_stats = claude_df.groupby('normalized_name')['similarity'].agg(['mean', 'std'])
gpt4o_stats = gpt4o_df.groupby('normalized_name')['similarity'].agg(['mean', 'std'])
genai_stats = genai_df.groupby('normalized_name')['overall'].agg(['mean', 'std'])

all_stats = pd.DataFrame({
    'GenAI_mean': genai_stats['mean'],
    'GenAI_std': genai_stats['std'],
    'Claude 3.5 Sonnet_mean': claude_stats['mean'],
    'Claude 3.5 Sonnet_std': claude_stats['std'],
    'GPT4o_mean': gpt4o_stats['mean'],
    'GPT4o_std': gpt4o_stats['std']
})

all_stats = all_stats.reindex(rankings_sorted.index)

# Visualizations

# 1. Bar plot with error bars
plt.figure(figsize=(14, 8))
x = range(len(all_stats.index))
width = 0.25

plt.bar(x, all_stats['GenAI_mean'], width, yerr=all_stats['GenAI_std'], label='GenAI', align='center', alpha=0.8, ecolor='black', capsize=5)
plt.bar([i + width for i in x], all_stats['Claude 3.5 Sonnet_mean'], width, yerr=all_stats['Claude 3.5 Sonnet_std'], label='Claude 3.5 Sonnet', align='center', alpha=0.8, ecolor='black', capsize=5)
plt.bar([i + 2*width for i in x], all_stats['GPT4o_mean'], width, yerr=all_stats['GPT4o_std'], label='GPT4o', align='center', alpha=0.8, ecolor='black', capsize=5)

plt.ylabel('Average Overall Similarity Score')
plt.xlabel('Test Films')
plt.title('Average Overall Similarity Scores Grouped by Model (with Standard Deviation)')
plt.xticks([i + width for i in x], all_stats.index, rotation=45, ha='right')
plt.legend()
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'bar_similarity_scores_grouped_by_model.png'))
plt.close()
print("Saved: bar_similarity_scores_grouped_by_model.png")

# 2. Heatmap of rankings
plt.figure(figsize=(10, 12))
sns.heatmap(rankings_sorted, annot=True, cmap='YlOrRd', fmt='.0f')
plt.title('Heatmap of Rankings (Sorted by GenAI Rank)')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'heatmap_rankings_sorted.png'))
plt.close()
print("Saved: heatmap_rankings_sorted.png")

# 3. Horizontal Heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(rankings_sorted.T, annot=True, cmap='YlOrRd', fmt='.0f')
plt.title('Horizontal Heatmap of Rankings (Sorted by GenAI Rank)')
plt.xlabel('Test Films')
plt.ylabel('Models')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'heatmap_rankings_horizontal.png'))
plt.close()
print("Saved: heatmap_rankings_horizontal.png")

# 4. Grouped Bar Chart of Rankings
plt.figure(figsize=(14, 8))
x = range(len(rankings_sorted.index))
width = 0.25

plt.bar(x, rankings_sorted['GenAI'], width, label='GenAI', align='center')
plt.bar([i + width for i in x], rankings_sorted['Claude 3.5 Sonnet'], width, label='Claude 3.5 Sonnet', align='center')
plt.bar([i + 2*width for i in x], rankings_sorted['GPT4o'], width, label='GPT4o', align='center')

plt.ylabel('Rank')
plt.xlabel('Test Films')
plt.title('Rankings Grouped by Model')
plt.xticks([i + width for i in x], rankings_sorted.index, rotation=45, ha='right')
plt.legend()
plt.ylim(0, rankings_sorted.max().max() + 1)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'bar_rankings_grouped_by_model.png'))
plt.close()
print("Saved: bar_rankings_grouped_by_model.png")

print(f"All visualizations have been saved in the directory: {output_dir}")