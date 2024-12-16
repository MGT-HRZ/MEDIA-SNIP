import os
from rembg import remove
from PIL import Image
import numpy as np
import io
import concurrent.futures
import time
import cv2

def post_process_image(image):
    """
    Post-process the image to remove unwanted white areas like hair without affecting clothes.
    Uses edge detection and color filtering to refine the areas to be made transparent.
    """
    # Convert to RGBA to work with transparency
    image = image.convert("RGBA")
    image_data = np.array(image)

    # Set a threshold for white areas to be transparent (adjust as necessary)
    white_threshold = 500  # Tuning this value helps control the threshold for whites

    # Find pixels that are close to pure white (adjust the range as necessary)
    white_areas = np.all(image_data[:, :, :3] > white_threshold, axis=-1)

    # Apply the threshold to make those pixels transparent (set alpha channel to 0)
    image_data[white_areas] = (255, 255, 255, 0)

    # Convert back to a PIL Image
    image = Image.fromarray(image_data, "RGBA")
    return image

def remove_background(input_path, output_path):
    try:
        # Open the image file and remove the background using rembg
        with open(input_path, 'rb') as input_file:
            input_image = input_file.read()

        # Process the image to remove the background
        output_image = remove(input_image)

        # Convert the output image to a PIL Image for post-processing
        img = Image.open(io.BytesIO(output_image))

        # Post-process the image to remove excess white areas (like hair) without affecting clothes
        img = post_process_image(img)

        # Save the output image with background removed
        img.save(output_path, "PNG")

        print(f"Background removed successfully for {input_path}. Saved to: {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def generate_output_path(input_path, output_dir):
    """
    Generate an output file path with a timestamp to ensure uniqueness and adjusted name.
    """
    # Extract the filename (without extension) and the extension
    base_name = os.path.basename(input_path)
    file_name, file_extension = os.path.splitext(base_name)

    # Add a timestamp to make the output file name unique
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    adjusted_file_name = f"{file_name} NoBg{file_extension}"

    # Join the output directory and the adjusted file name
    output_path = os.path.join(output_dir, adjusted_file_name)

    return output_path

def process_images_in_parallel(input_dir, output_dir):
    # Get a list of all image files in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepare arguments for each image
    tasks = []
    for image_file in image_files:
        input_path = os.path.join(input_dir, image_file)
        
        # Use the generate_output_path function to adjust the output path
        output_path = generate_output_path(input_path, output_dir)
        
        tasks.append((input_path, output_path))

    # Use ThreadPoolExecutor to process images in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use map to apply remove_background function to each task
        executor.map(lambda task: remove_background(*task), tasks)

def main():
    input_dir = " "  # Folder where input images are stored
    output_dir = " "  # Folder to store images with background removed
    
    # Process images in parallel
    process_images_in_parallel(input_dir, output_dir)

if __name__ == "__main__":
    main()
