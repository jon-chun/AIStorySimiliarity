import os
import re
import pandas as pd
import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from collections import Counter
import readability
import string

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

# Function to calculate basic text statistics
def text_stats(text):
    # Tokenize text
    tokens = word_tokenize(text)
    
    # Filter out punctuation tokens
    tokens = [t for t in tokens if t not in string.punctuation]
    
    # Character count
    char_count = len(text)
    
    # Word count
    word_count = len(tokens)
    
    # Sentence count
    sentence_count = len(nltk.sent_tokenize(text))
    
    # Vocabulary size
    vocabulary = set(tokens)
    vocab_size = len(vocabulary)
    
    # Vocabulary reading level (using readability package)
    reading_level = readability.getmeasures(text, lang='en')['readability grades']['FleschReadingEase']
    
    return {
        'char_count': char_count,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'vocab_size': vocab_size,
        'reading_level': reading_level
    }

def generate_latex_table(df):
    # Ensure the columns exist in the DataFrame before generating LaTeX
    if 'stat' not in df.columns or 'value' not in df.columns:
        raise ValueError("The DataFrame passed to the LaTeX table function must contain 'stat' and 'value' columns.")

    latex_str = "\\begin{table}[ht]\n\\centering\n\\begin{tabular}{lll}\n\\hline\n"
    latex_str += "filename & stat & value \\\\\n\\hline\n"
    
    for index, row in df.iterrows():
        latex_str += f"{row['filename']} & {row['stat']} & {row['value']} \\\\\n"
    
    latex_str += "\\hline\n\\end{tabular}\n\\caption{Scripts Dataset Statistics}\n\\end{table}"
    return latex_str

# Function to generate a simplified Markdown table
def generate_simplified_markdown_table(df, output_path):
    # Extract only the columns we care about for the simplified table
    simplified_df = df[['filename', 'char_count', 'word_count', 'sentence_count', 'vocab_size', 'reading_level']].copy()

    # Start building the Markdown content
    markdown_str = "# Simplified Scripts Dataset Statistics\n\n"
    markdown_str += "| Film Name | Characters | Words | Sentences | Vocabulary Size | Reading Level |\n"
    markdown_str += "|-----------|------------|-------|-----------|-----------------|---------------|\n"

    # Iterate through the DataFrame and add each film's data to the table
    for index, row in simplified_df.iterrows():
        markdown_str += f"| {row['filename']} | {row['char_count']:.2f} | {row['word_count']:.2f} | {row['sentence_count']:.2f} | {row['vocab_size']:.2f} | {row['reading_level']:.2f} |\n"

    # Save the Markdown table to a file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_str)

    print(f'Successfully saved simplified statistics to {output_path}')

def main():
    # Define the relative path to the film scripts directory
    relpath_scripts = os.path.join('..', 'data', 'film_scripts_txt')
    
    # Regular expression for matching script files
    script_pattern = re.compile(r'script_.*\.txt')
    
    # Initialize a list to store the data for each script
    data = []
    
    # Iterate over the files in the directory
    for filename in os.listdir(relpath_scripts):
        if script_pattern.match(filename):
            filepath = os.path.join(relpath_scripts, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
                # Compute stats for the script
                stats = text_stats(text)
                # Add the filename and stats to the data list
                stats['filename'] = filename
                data.append(stats)
    
    # Create a DataFrame from the data for individual films
    df = pd.DataFrame(data)
    
    # Generate and save the simplified Markdown table
    markdown_output_filepath = os.path.join(relpath_scripts, 'scripts_dataset_stats.md')
    generate_simplified_markdown_table(df, markdown_output_filepath)
    
    # Add the necessary columns to the DataFrame before passing to the LaTeX generator
    df_long_format = df.melt(id_vars=['filename'], var_name='stat', value_name='value')
    
    # Generate LaTeX markup
    latex_output_filepath = os.path.join(relpath_scripts, 'scripts_dataset_stats_latex.txt')
    latex_table = generate_latex_table(df_long_format)
    with open(latex_output_filepath, 'w', encoding='utf-8') as f:
        f.write(latex_table)
    
    print(f'Successfully saved script statistics to {markdown_output_filepath}')
    print(f'Successfully saved LaTeX table to {latex_output_filepath}')

if __name__ == '__main__':
    main()
