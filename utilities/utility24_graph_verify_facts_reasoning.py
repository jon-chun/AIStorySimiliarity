import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Set the style for the plots
plt.style.use('default')
sns.set_palette("Set2")

def read_csv(file_path):
    df = pd.read_csv(file_path)
    df['version_number'] = df['version_number'].astype(int)
    
    # Count non-empty entries as errors
    df['num_factual_errors'] = df['factual_errors'].notna().astype(int)
    df['num_reasoning_errors'] = df['reasoning_errors'].notna().astype(int)
    
    return df

# Update file paths
cwd = os.getcwd()
input_dir = os.path.join(cwd, '..', 'data', 'verify_summary')
output_dir = os.path.join(cwd, '..', 'data', 'figures_verify')
os.makedirs(output_dir, exist_ok=True)

gpt4o_file = os.path.join(input_dir, 'summary_verify_facts-reasoning_gpt4o_office-space.csv')
claude_file = os.path.join(input_dir, 'summary_verify_facts-reasoning_claude35sonnet_office-space.csv')

gpt4o_df = read_csv(gpt4o_file)
claude_df = read_csv(claude_file)

# Combine the dataframes
combined_df = pd.concat([gpt4o_df, claude_df])

# Create visualizations

# 1. Box plot of accuracy scores for each category
plt.figure(figsize=(14, 8))
accuracy_columns = ['accuracy_overall_score', 'accuracy_characters_score', 'accuracy_plot_score', 
                    'accuracy_setting_score', 'accuracy_themes_score']
melted_df = pd.melt(combined_df, id_vars=['model_name'], value_vars=accuracy_columns, 
                    var_name='Category', value_name='Score')
sns.boxplot(x='Category', y='Score', hue='model_name', data=melted_df)
plt.xticks(rotation=45, ha='right')
plt.title('Distribution of Accuracy Scores by Category and Model')
plt.ylabel('Accuracy Score')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'boxplot_accuracy_scores_facts-reasoning.png'))
plt.close()

# 2. Bar plot of average number of errors
error_df = combined_df.groupby('model_name')[['num_factual_errors', 'num_reasoning_errors']].mean().reset_index()
error_df_melted = pd.melt(error_df, id_vars=['model_name'], var_name='Error Type', value_name='Average Number')

plt.figure(figsize=(10, 6))
sns.barplot(x='model_name', y='Average Number', hue='Error Type', data=error_df_melted)
plt.title('Average Number of Errors by Model')
plt.ylabel('Average Number of Errors')
plt.xlabel('Model')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'barplot_avg_errors_facts-reasoning.png'))
plt.close()

# 3. Heatmap of average accuracy scores
pivot_df = combined_df.groupby('model_name')[accuracy_columns].mean()
plt.figure(figsize=(12, 6))
sns.heatmap(pivot_df, annot=True, cmap='YlOrRd', fmt='.1f')
plt.title('Heatmap of Average Accuracy Scores')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'heatmap_avg_accuracy_facts-reasoning.png'))
plt.close()

# 4. Bar plot of error occurrence
error_occurrence = combined_df[['model_name', 'num_factual_errors', 'num_reasoning_errors']].melt(id_vars=['model_name'], var_name='Error Type', value_name='Has Error')
error_occurrence['Has Error'] = error_occurrence['Has Error'].astype(bool)
plt.figure(figsize=(10, 6))
sns.barplot(x='model_name', y='Has Error', hue='Error Type', data=error_occurrence, estimator=lambda x: sum(x) / len(x))
plt.title('Proportion of Responses with Errors')
plt.ylabel('Proportion')
plt.xlabel('Model')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'barplot_error_occurrence_facts-reasoning.png'))
plt.close()

# 5. Distribution of overall accuracy scores
plt.figure(figsize=(10, 6))
sns.histplot(data=combined_df, x='accuracy_overall_score', hue='model_name', element='step', stat='density', common_norm=False)
plt.title('Distribution of Overall Accuracy Scores')
plt.xlabel('Overall Accuracy Score')
plt.ylabel('Density')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'histogram_overall_accuracy_facts-reasoning.png'))
plt.close()

print(f"Visualizations have been saved as PNG files in the directory: {output_dir}")