import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set the style for the plots
plt.style.use('default')
sns.set_palette("Set2")

def read_csv(file_path):
    df = pd.read_csv(file_path)
    df['version_number'] = df['version_number'].astype(int)
    # Correct the spelling of "Lara Croft: Tomb Raider"
    df['name'] = df['name'].replace('Lara Croft Tomb Raider', 'Lara Croft: Tomb Raider')
    return df


# Read the CSV files
cwd = os.getcwd()
input_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'verify_summary'))
output_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'figures_verify'))
os.makedirs(output_dir, exist_ok=True)

gpt4o_file = os.path.join(input_dir, 'summary_verify_ranking_gpt4o_office-space.csv')
claude_file = os.path.join(input_dir, 'summary_verify_ranking_claude35sonnet_office-space.csv')

gpt4o_df = read_csv(gpt4o_file)
claude_df = read_csv(claude_file)

# Combine the dataframes
combined_df = pd.concat([gpt4o_df, claude_df])

# 1. Box plot of similarity scores for each movie
plt.figure(figsize=(12, 6))
sns.boxplot(x='name', y='similarity', hue='model_name', data=combined_df)
plt.xticks(rotation=45, ha='right')
plt.title('Distribution of Similarity Scores by Movie and Model')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'boxplot_similarity_scores.png'))
plt.close()

# 2. KDE plot of overall similarity distribution
plt.figure(figsize=(10, 6))
sns.kdeplot(data=gpt4o_df, x='similarity', shade=True, label='GPT-4')
sns.kdeplot(data=claude_df, x='similarity', shade=True, label='Claude-3.5')
plt.title('Distribution of Similarity Scores')
plt.xlabel('Similarity Score')
plt.ylabel('Density')
plt.legend()
plt.savefig(os.path.join(output_dir, 'kde_similarity_distribution.png'))
plt.close()

# 3. Scatter plot of average similarity scores
avg_similarity = combined_df.groupby(['model_name', 'name'])['similarity'].mean().reset_index()
plt.figure(figsize=(12, 6))
sns.scatterplot(x='name', y='similarity', hue='model_name', data=avg_similarity, s=100)
plt.xticks(rotation=45, ha='right')
plt.title('Average Similarity Scores by Movie and Model')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'scatter_avg_similarity.png'))
plt.close()

# 4. Heatmap of similarity scores
pivot_df = combined_df.pivot_table(values='similarity', index='name', columns='model_name', aggfunc='mean')
plt.figure(figsize=(10, 8))
sns.heatmap(pivot_df, annot=True, cmap='YlOrRd', fmt='.1f')
plt.title('Heatmap of Average Similarity Scores')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'heatmap_similarity.png'))
plt.close()

# 5. Bar plot of similarity score differences
diff_df = pivot_df.diff(axis=1).iloc[:, -1].reset_index()
diff_df.columns = ['name', 'difference']
diff_df = diff_df.sort_values('difference')

plt.figure(figsize=(12, 6))
sns.barplot(x='Test Film vs Raiders of the Lost Ark (1981)', y='difference', data=diff_df)
plt.xticks(rotation=45, ha='right')
plt.title('Difference in Accuracy Scores (GPT-4 - Claude-3.5)')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'barplot_similarity_difference.png'))
plt.close()

print(f"Visualizations have been saved as PNG files in the directory: {output_dir}")