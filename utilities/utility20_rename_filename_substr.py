import os


# Configuration
cwd = os.getcwd()
input_root_dir = os.path.abspath(os.path.join(cwd, '..', 'data', 'score_diff_genai'))
substr_old = '.csv.'
substr_new = '.'

def rename_files(input_root_dir, substr_old, substr_new):
    # Iterate over all files in the directory
    for filename in os.listdir(input_root_dir):
        # Check if the old substring is in the filename
        if substr_old in filename:
            # Create the new filename by replacing the old substring with the new one
            new_filename = filename.replace(substr_old, substr_new)
            # Construct full file paths
            old_file_path = os.path.join(input_root_dir, filename)
            new_file_path = os.path.join(input_root_dir, new_filename)
            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_filename}")

def main():
    # Call the rename function
    rename_files(input_root_dir, substr_old, substr_new)

if __name__ == "__main__":
    main()
