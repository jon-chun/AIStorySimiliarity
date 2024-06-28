import os

def list_files_with_status(directory):
    print("\nListing all files and their statuses:")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            absolute_path = os.path.abspath(file_path)
            print(f"File: {filename}")
            print(f"  Absolute Path: {absolute_path}")
            print(f"  Exists: {os.path.exists(absolute_path)}")
            print(f"  Is File: {os.path.isfile(absolute_path)}")
            print(f"  Is Dir: {os.path.isdir(absolute_path)}")

def check_file_existence(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            absolute_path = os.path.abspath(file_path)
            print(f"Checking file: {absolute_path}")
            print(f"  Exists: {os.path.exists(absolute_path)}")
            print(f"  Is File: {os.path.isfile(absolute_path)}")
            print(f"  Is Dir: {os.path.isdir(absolute_path)}")
            print("")

def remove_prefix_from_filenames(directory, prefix_delete):
    try:
        # List all files in the directory with their statuses
        list_files_with_status(directory)
        
        # Check existence of files independently
        check_file_existence(directory)
        
        # Proceed with the renaming
        print("\nStarting the renaming process:")
        for root, dirs, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                absolute_path = os.path.abspath(file_path)
                
                # Print debug information about the file path and its type
                print(f"Checking: {file_path}")
                print(f"Absolute Path: {absolute_path}")
                print(f"Is file: {os.path.isfile(absolute_path)}")
                print(f"Exists: {os.path.exists(absolute_path)}")
                
                # Check if it is a file and starts with the prefix
                if os.path.isfile(absolute_path):
                    print(f"Processing file: {filename}")
                    if filename.startswith(prefix_delete):
                        # New filename after removing the prefix
                        new_filename = filename[len(prefix_delete):]
                        new_file_path = os.path.join(root, new_filename)
                        
                        # Handle potential long path issues on Windows
                        try:
                            os.rename(file_path, new_file_path)
                            print(f'Renamed: {file_path} -> {new_file_path}')
                        except Exception as rename_error:
                            print(f"Failed to rename {file_path} to {new_file_path}: {rename_error}")
                    else:
                        print(f"Skipped (does not start with prefix): {filename}")
                else:
                    print(f"Skipped (not a file): {filename} - Type: {type(file_path)}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Get the current working directory
    current_directory = os.getcwd()
    print(f"Current directory: {current_directory}")

    # Define the prefix to delete
    PREFIX_DELETE = "similarity-by-score_"
    
    # Call the function to remove the prefix
    remove_prefix_from_filenames(current_directory, PREFIX_DELETE)
