import os

def rewrite_files_and_rename(directory):
    counter = 1

    for foldername, subfolders, filenames in os.walk(directory, topdown=False):
        # Process files in the current directory
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            try:
                with open(file_path, 'wb') as f:
                    pass  # Truncate the file to 0 bytes

                new_file_name = f"temp_{counter}"
                new_file_path = os.path.join(foldername, new_file_name)
                os.rename(file_path, new_file_path)

                counter += 1
                print(f"Renamed and cleared file: {file_path} -> {new_file_path}")

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        # Process and rename the folder itself
        try:
            new_folder_name = f"temp_{counter}"
            new_folder_path = os.path.join(os.path.dirname(foldername), new_folder_name)

            original_new_folder_path = new_folder_path
            suffix = 1
            while os.path.exists(new_folder_path):
                new_folder_path = f"{original_new_folder_path}_{suffix}"
                suffix += 1

            os.rename(foldername, new_folder_path)

            counter += 1
            print(f"Renamed folder: {foldername} -> {new_folder_path}")

        except Exception as e:
            print(f"Error renaming folder {foldername}: {e}")

# Hardcoded fallback path (edit this as needed)
default_directory = r"C:\Path\To\Your\Folder"

# Prompt user for path, or use hardcoded one
user_input = input(f"Enter the path to the directory you want to process (or press Enter to use default):\n[{default_directory}]: ").strip()
target_directory = user_input if user_input else default_directory

# Run the function
rewrite_files_and_rename(target_directory)

# Pause at the end
input("Processing complete. Press Enter to exit...")
