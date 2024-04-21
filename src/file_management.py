import os
import subprocess
import tempfile


def write_string_array_to_text_file(input_string_array, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for string in input_string_array:
            file.writelines(string)


def generate_file_path_with_other_extension(input_epub_file_path, extension='.txt'):
    base_name, ext = os.path.splitext(input_epub_file_path)
    file_path = base_name + extension
    return file_path


def file_exists(file_path):
    """
    Check if a file exists given its path.

    Args:
    - file_path (str): The path to the file to check.

    Returns:
    - bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)


def create_temp_text_file(content):
    temp_dir = tempfile.mkdtemp()

    file_path = os.path.normpath(os.path.join(temp_dir, "temp_file.txt"))

    with open(file_path, "w", encoding='utf-8') as file:
        file.write(content)

    return file_path


def delete_temp_file(file_path):
    try:
        os.remove(file_path)
        print(f"Temporary file '{file_path}' deleted successfully.")
    except OSError as e:
        print(f"Error deleting temporary file '{file_path}': {e}")


def extract_file_name(file_path):
    # Use os.path.basename() to extract the file name
    file_name = os.path.basename(file_path)

    # Split the file name by the dot to remove the extension
    file_name_without_extension = file_name.split('.')[0]

    return file_name_without_extension


def open_directory_in_explorer(directory_path):
    # Check if the directory path exists
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return

    # Use subprocess to open the directory in the default file explorer
    try:
        subprocess.Popen(f'explorer "{directory_path}"')
    except Exception as e:
        print(f"Error: {e}")


def delete_files_in_directory(directory):
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
