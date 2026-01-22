import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from tqdm import tqdm  # Import tqdm for progress bar

import subprocess
import sys


def process_images():
    # Step 1: Parse combined_images.html
    html_file = "combined_images.html"
    download_folder = "downloaded_images"
    zip_file_name = "images.zip"

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Ask user about maintaining original file names (y/n)
    maintain_input = input("Do you want to maintain the original file names? (y/n): ").strip().lower()
    maintain_names = maintain_input == "y"

    # Read the HTML file
    with open(html_file, "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract image URLs
    img_tags = soup.find_all("img")
    img_urls = [img["src"] for img in img_tags if "src" in img.attrs]

    print(f"Found {len(img_urls)} images.")

    # Step 2: Download the images with a progress bar
    downloaded_files = []
    print("Downloading images...")

    for idx, img_url in enumerate(tqdm(img_urls, desc="Downloading", unit="image")):
        try:
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                if maintain_names:
                    file_name = os.path.basename(img_url.split("?")[0])  # Original name
                else:
                    file_name = f"image_{idx + 1}.jpg"  # Sequential name

                file_path = os.path.join(download_folder, file_name)

                tqdm.write(f"Downloading: {file_name}")

                with open(file_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)

                downloaded_files.append(file_path)
            else:
                tqdm.write(f"Failed to download: {img_url}")
        except Exception as e:
            tqdm.write(f"Error downloading {img_url}: {e}")

    print(f"Downloaded {len(downloaded_files)} images.")

    # Step 3: Zip the images
    print("Zipping images...")
    with ZipFile(zip_file_name, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, os.path.basename(file))
    print(f"Images zipped into {zip_file_name}")

    # Step 4: Confirm before corrupting
    corrupt_input = input("Do you want to corrupt the images now? (y/n): ").strip().lower()
    if corrupt_input != "y":
        print("Corruption skipped.")
        return

    # Step 5: Rename to trash_*.jpg and corrupt
    print("Renaming to trash_*.jpg and corrupting images...")
    corrupted_files = []
    for idx, file_path in enumerate(tqdm(downloaded_files, desc="Corrupting")):
        try:
            trash_name = f"trash_{idx + 1}.jpg"
            trash_path = os.path.join(download_folder, trash_name)
            os.rename(file_path, trash_path)

            with open(trash_path, "wb") as empty_file:
                empty_file.truncate(0)

            corrupted_files.append(trash_path)
        except Exception as e:
            tqdm.write(f"Error corrupting {file_path}: {e}")

    # Step 6: Ask user to delete corrupted images
    user_input = input("Do you want to delete the corrupted images? (y/n): ").strip().lower()
    if user_input == "y":
        for file_path in corrupted_files:
            os.remove(file_path)
        print("Corrupted images deleted.")
    else:
        print("Corrupted images retained.")


if __name__ == "__main__":
    process_images()

    # ---------------------------------
    # OPTIONAL: run next script afterward
    # ---------------------------------
    MAIN_SCRIPT = "main5_linux.py"

    run_main = input(
        f"Do you want to run {MAIN_SCRIPT} now? (y/n): "
    ).strip().lower()

    if run_main == "y":
        subprocess.run([sys.executable, MAIN_SCRIPT])
