import os
from zipfile import ZipFile
from tqdm import tqdm  # For progress bar

def process_images(directory):
    # Step 1: Scan the directory for image files
    downloaded_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):  # Add other extensions if needed
            downloaded_files.append(os.path.join(directory, filename))

    if not downloaded_files:
        print("No image files found in the specified directory.")
        return

    # Step 2: Zip the images
    zip_file_name = "downloaded_images.zip"
    print("Zipping images...")
    with ZipFile(zip_file_name, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, os.path.basename(file))
    print(f"Images zipped into {zip_file_name}")

    # Step 3: Corrupt the images by reducing them to 0 bytes
    print("Corrupting images...")
    for file_path in tqdm(downloaded_files, desc="Corrupting"):  # Add progress bar for corrupting
        try:
            with open(file_path, "wb") as empty_file:
                empty_file.truncate(0)  # Reduce file size to 0 bytes
        except Exception as e:
            print(f"Error corrupting {file_path}: {e}")

    # Step 4: Wait for user input to delete corrupted images
    user_input = input("Do you want to delete the corrupted images? (y/n): ").strip().lower()
    if user_input == "y":
        for file_path in downloaded_files:
            os.remove(file_path)
        print("Corrupted images deleted.")
    else:
        print("Corrupted images retained.")

# Example usage
if __name__ == "__main__":
    # Specify the directory to scan for images
    directory_to_scan = "C:/Users/Mr. 8.1/Desktop/URL-IMG-EXTRACT/downloaded_images"  # Replace with your actual directory
    process_images(directory_to_scan)