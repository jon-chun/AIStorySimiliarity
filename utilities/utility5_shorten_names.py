import os

def shorten_filenames(root_dir, prefix_delete='similarity-by-score_', suffix_delete=''):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename files
        for filename in filenames:
            new_filename = filename
            if filename.startswith(prefix_delete):
                new_filename = filename[len(prefix_delete):]
            if new_filename.endswith(suffix_delete) and suffix_delete:
                new_filename = new_filename[:-len(suffix_delete)]
            if new_filename != filename:
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_filename)
                os.rename(old_path, new_path)
                print(f'Renamed file: {old_path} -> {new_path}')

        # Rename directories
        for dirname in dirnames:
            new_dirname = dirname
            if dirname.startswith(prefix_delete):
                new_dirname = dirname[len(prefix_delete):]
            if new_dirname.endswith(suffix_delete) and suffix_delete:
                new_dirname = new_dirname[:-len(suffix_delete)]
            if new_dirname != dirname:
                old_path = os.path.join(dirpath, dirname)
                new_path = os.path.join(dirpath, new_dirname)
                os.rename(old_path, new_path)
                print(f'Renamed directory: {old_path} -> {new_path}')

if __name__ == '__main__':
    ROOT_DIR = os.path.join('..', 'data', 'film_similarity_by_score_scripts', 'similarity-by-score_scripts_raiders-of-the-lost-ark_indiana-jones-and-the-dial-of-destiny')
    PREFIX_DELETE = 'similarity-by-score_'
    SUFFIX_DELETE = ''

    shorten_filenames(ROOT_DIR, PREFIX_DELETE, SUFFIX_DELETE)
