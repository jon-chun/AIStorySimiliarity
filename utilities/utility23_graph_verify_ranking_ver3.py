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

# 1. Box plot of accuracy scores for each movie
plt.figure(figsize=(14, 8))
sns.boxplot(x='name', y='similarity', hue='model_name', data=combined_df)
plt.xticks(rotation=45, ha='right')
plt.title('Distribution of Accuracy Scores by Movie and Model')
plt.ylabel('Accuracy Score')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'boxplot_accuracy_scores_ranking.png'))
plt.close()

# 2. Bar plot with error bars for average accuracy and standard deviation
avg_accuracy = combined_df.groupby(['model_name', 'name'])['similarity'].agg(['mean', 'std']).reset_index()
plt.figure(figsize=(12, 8))  # Reduced width from 14 to 12

sns.barplot(x='name', y='mean', hue='model_name', data=avg_accuracy)

plt.errorbar(x=avg_accuracy[avg_accuracy['model_name'] == 'gpt4o'].index, 
             y=avg_accuracy[avg_accuracy['model_name'] == 'gpt4o']['mean'], 
             yerr=avg_accuracy[avg_accuracy['model_name'] == 'gpt4o']['std'], 
             fmt='none', c='black', capsize=5)
plt.errorbar(x=avg_accuracy[avg_accuracy['model_name'] == 'claude35sonnet'].index + 0.4, 
             y=avg_accuracy[avg_accuracy['model_name'] == 'claude35sonnet']['mean'], 
             yerr=avg_accuracy[avg_accuracy['model_name'] == 'claude35sonnet']['std'], 
             fmt='none', c='black', capsize=5)

plt.xticks(rotation=90, ha='center')  # Vertical labels
plt.title('Average Accuracy Scores with Standard Deviation')
plt.ylabel('Accuracy Score')
plt.xlabel('')  # Remove x-axis label as it's redundant
plt.legend(title='Model Name')

plt.tight_layout()  # Adjust layout to use space efficiently
plt.savefig(os.path.join(output_dir, 'barplot_avg_accuracy_with_std_ranking.png'), bbox_inches='tight')
plt.close()

# 3. Heatmap of average accuracy scores
pivot_df = combined_df.pivot_table(values='similarity', index='name', columns='model_name', aggfunc='mean')
plt.figure(figsize=(12, 10))
sns.heatmap(pivot_df, annot=True, cmap='YlOrRd', fmt='.1f')
plt.title('Heatmap of Average Accuracy Scores')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'heatmap_avg_accuracy.png'))
plt.close()

# 4. Violin plot for distribution comparison
plt.figure(figsize=(14, 8))
sns.violinplot(x='name', y='similarity', hue='model_name', data=combined_df, split=True)
plt.xticks(rotation=45, ha='right')
plt.title('Distribution of Accuracy Scores by Movie and Model')
plt.ylabel('Accuracy Score')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'violinplot_accuracy_distribution_ranking.png'))
plt.close()

# 5. Scatter plot of average accuracy scores with error bars
avg_accuracy = combined_df.groupby(['model_name', 'name'])['similarity'].agg(['mean', 'std']).reset_index()
plt.figure(figsize=(14, 8))
for model in ['gpt4o', 'claude35sonnet']:
    data = avg_accuracy[avg_accuracy['model_name'] == model]
    plt.errorbar(x=data['name'], y=data['mean'], yerr=data['std'], 
                 fmt='o', capsize=5, label=model)
plt.xticks(rotation=45, ha='right')
plt.title('Average Accuracy Scores with Standard Deviation')
plt.ylabel('Accuracy Score')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'scatterplot_avg_accuracy_with_std_ranking.png'))
plt.close()

print(f"Visualizations have been saved as PNG files in the directory: {output_dir}")


def create_bar_plot(data, x, y, hue, title, filename, yerr=None, plot_type='standard'):
    plt.figure(figsize=(12, 6))
    
    if plot_type == 'standard':
        ax = sns.barplot(x=x, y=y, hue=hue, data=data)
    elif plot_type == 'grouped':
        ax = sns.barplot(x=x, y=y, hue=hue, data=data, dodge=True)
    elif plot_type == 'stacked':
        ax = data.pivot(index=x, columns=hue, values=y).plot(kind='bar', stacked=True)
    
    if yerr is not None:
        x_coords = np.arange(len(data[x].unique()))
        for i, model in enumerate(data[hue].unique()):
            model_data = data[data[hue] == model]
            plt.errorbar(x_coords + i*0.4 - 0.2, model_data[y], yerr=model_data[yerr], 
                         fmt='none', c='black', capsize=5)
    
    plt.title(title)
    plt.xlabel('')
    plt.ylabel('Accuracy Score')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Model')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()

# 1. Standard bar plot with error bars
create_bar_plot(avg_accuracy, 'name', 'mean', 'model_name', 
                'Average Accuracy Scores with Standard Deviation',
                'barplot_avg_accuracy_standard_ranking.png', yerr='std')

# 2. Grouped bar plot with error bars
create_bar_plot(avg_accuracy, 'name', 'mean', 'model_name', 
                'Average Accuracy Scores (Grouped) with Standard Deviation',
                'barplot_avg_accuracy_grouped_ranking.png', yerr='std', plot_type='grouped')

# 3. Stacked bar plot (no error bars for this type)
create_bar_plot(avg_accuracy, 'name', 'mean', 'model_name', 
                'Average Accuracy Scores (Stacked)',
                'barplot_avg_accuracy_stacked_ranking.png', plot_type='stacked')

# 4. Horizontal bar plot
plt.figure(figsize=(8, 10))
sns.barplot(y='name', x='mean', hue='model_name', data=avg_accuracy, orient='h')
plt.title('Average Accuracy Scores (Horizontal)')
plt.xlabel('Accuracy Score')
plt.ylabel('')
plt.legend(title='Model')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'barplot_avg_accuracy_horizontal_ranking.png'))
plt.close()

# 5. Diverging bar plot (difference between models)
diff_df = avg_accuracy.pivot(index='name', columns='model_name', values='mean').reset_index()
diff_df['difference'] = diff_df['gpt4o'] - diff_df['claude35sonnet']
diff_df = diff_df.sort_values('difference')

plt.figure(figsize=(10, 8))
sns.barplot(y='name', x='difference', data=diff_df, orient='h')
plt.title('Difference in Average Accuracy Scores (GPT-4 - Claude-3.5)')
plt.xlabel('Difference in Accuracy Score')
plt.ylabel('')
plt.axvline(x=0, color='black', linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'barplot_accuracy_difference_ranking.png'))
plt.close()

print(f"Bar plot visualizations have been saved in the directory: {output_dir}")