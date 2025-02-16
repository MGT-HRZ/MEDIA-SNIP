import requests
import os
from zipfile import ZipFile
from tqdm import tqdm  # For progress bar

# Base URL for the images
base_url = "link.../"
# Starting index for the images
index = 1

# Create a directory to save the images
os.makedirs("downloaded_images", exist_ok=True)

downloaded_files = []  # List to keep track of downloaded files

# Define an array of indices to skip
skip_indices = []  # This will skip 001.jpg

while True:
    # Check if the current index should be skipped
    if index in skip_indices:
        print(f"Skipping: {index:03d}.jpg")
        index += 1
        continue  # Skip to the next index

    # Format the image filename
    image_url_jpg = f"{base_url}{index:03d}.jpg"
    image_url_jpg_upper = f"{base_url}{index:03d}.JPG"
    
    try:
        # Try to download the image with .jpg extension first
        response = requests.get(image_url_jpg)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the image to the local directory
            file_path = f"downloaded_images/{index:03d}.jpg"
            with open(file_path, "wb") as file:
                file.write(response.content)
            downloaded_files.append(file_path)  # Add to the list of downloaded files
            print(f"Downloaded: {image_url_jpg}")
        else:
            # If the .jpg download fails, try the .JPG extension
            response = requests.get(image_url_jpg_upper)
            if response.status_code == 200:
                # Save the image to the local directory
                file_path = f"downloaded_images/{index:03d}.JPG"
                with open(file_path, "wb") as file:
                    file.write(response.content)
                downloaded_files.append(file_path)  # Add to the list of downloaded files
                print(f"Downloaded: {image_url_jpg_upper}")
            else:
                print(f"Failed to download: {image_url_jpg} and {image_url_jpg_upper} (Status code: {response.status_code})")
        
        # Increment the index for the next image regardless of success
        index += 1  

    except requests.ConnectionError:
        print(f"Connection error occurred while trying to download: {image_url_jpg}")
        break  # Exit the loop on connection error
    except Exception as e:
        print(f"An error occurred: {e}")
        break  # Exit the loop on any other error

# Step 3: Zip the images
zip_file_name = "downloaded_images.zip"
print("Zipping images...")
with ZipFile(zip_file_name, "w") as zipf:
    for file in downloaded_files:
        zipf.write(file, os.path.basename(file))
print(f"Images zipped into {zip_file_name}")

# Step 4: Corrupt the images by reducing them to 0 bytes
print("Corrupting images...")
for file_path in tqdm(downloaded_files, desc="Corrupting"):  # Add progress bar for corrupting
    try:
        with open(file_path, "wb") as empty_file:
            empty_file.truncate(0)  # Reduce file size to 0 bytes
    except Exception as e:
        print(f"Error corrupting {file_path}: {e}")

# Step 5: Wait for user input to delete corrupted images
user_input = input("Do you want to delete the corrupted images? (y/n): ").strip().lower()
if user_input == "y":
    for file_path in downloaded_files:
        os.remove(file_path)
    print("Corrupted images deleted.")
else:
    print("Corrupted images retained.")