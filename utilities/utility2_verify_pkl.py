import os
import pickle
import json
import sys
import pandas as pd


"""
I see the issue now. The pickle file contains a pandas DataFrame, which is not directly JSON serializable. We need to modify the script to handle DataFrame objects. Here's an updated version of the script that should work with pandas DataFrames:

This script now includes the following changes:

1. Added an import for pandas: `import pandas as pd`
2. Created a new function `dataframe_to_dict` that converts a DataFrame to a JSON-serializable dictionary.
3. In the `read_and_verify_pkl` function, we now check if the loaded data is a DataFrame and convert it if necessary.

With these modifications, the script should be able to handle both regular dictionaries and pandas DataFrames stored in pickle files. It will convert the DataFrame to a dictionary representation that includes the column names, data, and index.

Try running the script again with your pickle file. It should now be able to read and display the contents of the DataFrame in a JSON-like format.

""";

def dataframe_to_dict(df):
    """Convert DataFrame to a dictionary that's JSON serializable"""
    return {
        'columns': df.columns.tolist(),
        'data': df.values.tolist(),
        'index': df.index.tolist()
    }

def read_and_verify_pkl(input_file_path):
    # Read the pickle file
    with open(input_file_path, 'rb') as f:
        data = pickle.load(f)
    
    # Check if the data is a DataFrame
    if isinstance(data, pd.DataFrame):
        data = dataframe_to_dict(data)
    
    # Convert the data to a JSON formatted string
    json_data = json.dumps(data, indent=4)
    
    # Print the JSON formatted string to the screen
    print(json_data)

def main():
    # Check if a filename was provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <pickle_file_name>")
        sys.exit(1)
    
    # Get the pickle file name from command-line argument
    pickle_file_name = sys.argv[1]
    
    # Construct the full path to the pickle file
    # This will be relative to the current working directory
    input_file_path = os.path.join(os.getcwd(), pickle_file_name)
    
    # Check if the file exists
    if not os.path.exists(input_file_path):
        print(f"Error: File '{pickle_file_name}' not found in the current directory.")
        sys.exit(1)
    
    # Read and verify the pickle file
    read_and_verify_pkl(input_file_path)

if __name__ == '__main__':
    main()