import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from PIL import Image
from io import BytesIO

def extract_urls_from_page(url, domain):
    # Set up Selenium WebDriver in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Set up the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set of URLs to store the extracted links
    urls = set()

    try:
        # Open the page
        driver.get(url)
        driver.implicitly_wait(10)  # Allow the page to load
        
        # Get page source after it's fully loaded
        page_source = driver.page_source
        
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Loop through all anchor tags to find links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)  # Resolve relative URLs
            
            # Check if the URL belongs to the specified domain
            if urlparse(full_url).netloc.endswith(domain):
                urls.add(full_url)  # Add to the set if domain matches
                
        print(f"Extracted {len(urls)} URLs from {url}")
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
    finally:
        # Close the browser once done
        driver.quit()

    return urls

def is_valid_image(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for request errors
        
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        file_format = img.format.lower()
        
        # Check file format and dimensions
        if file_format in ['jpeg', 'jpg', 'png'] and width > 900 and height > 900:
            return True, width, height  # Return image dimensions for comparison
    except Exception as e:
        # print(f"An error occurred while checking image {url}: {e}")
        return False, 0, 0
    
    return False, 0, 0

def download_largest_image_from_page(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    largest_image = None
    largest_image_url = None
    largest_image_size = 0

    try:
        # Open the page
        driver.get(url)
        driver.implicitly_wait(10)  # Allow the page to load
        
        # Get page source after it's fully loaded
        page_source = driver.page_source
        
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Loop through all img tags to find the largest image
        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            full_url = urljoin(url, src)  # Resolve relative URLs

            valid, width, height = is_valid_image(full_url)
            if valid:
                image_size = width * height  # Calculate image area (width * height)
                if image_size > largest_image_size:
                    largest_image_size = image_size
                    largest_image_url = full_url
                    largest_image = Image.open(BytesIO(requests.get(largest_image_url).content))
        
        if largest_image:
            # Save the largest image
            filename = os.path.basename(largest_image_url)
            largest_image.save(filename)
            print(f"Downloaded largest image: {filename}")
        else:
            print("No valid image found on the page.")
    
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
    finally:
        # Close the browser once done
        driver.quit()

def save_urls_to_txt(urls, filename="links.txt"):
    with open(filename, "w") as file:
        for url in urls:
            file.write(url + "\n")
    print(f"Saved {len(urls)} URLs to {filename}")

def main():
    website_url = ""
    domain_filter = ""  # Domain to filter
    
    # Extract URLs from the webpage and save to a text file
    extracted_urls = extract_urls_from_page(website_url, domain_filter)
    save_urls_to_txt(extracted_urls)
    
    # Read URLs from the file and download the largest image from each
    with open("links.txt", "r") as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()
        print(f"Processing URL: {url}")
        download_largest_image_from_page(url)

if __name__ == "__main__":
    main()
