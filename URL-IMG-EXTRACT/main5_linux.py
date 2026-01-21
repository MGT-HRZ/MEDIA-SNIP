from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
from PIL import Image
from io import BytesIO
import os

# -------------------------
# Helper functions
# -------------------------

def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")              # new headless mode
    chrome_options.add_argument("--no-sandbox")                # required in containers
    chrome_options.add_argument("--disable-dev-shm-usage")     # prevents /dev/shm crashes
    chrome_options.add_argument("--disable-gpu")               # disable GPU
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1920,1080")     # necessary for headless
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def extract_href_from_page(url, domain):
    driver = create_chrome_driver()
    urls = set()
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        for a_tag in soup.find_all("a", class_="link link--external", href=True):
            full_url = urljoin(url, a_tag["href"])
            if urlparse(full_url).netloc.endswith(domain):
                urls.add(full_url)

        print(f"Extracted {len(urls)} URLs from {url}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
    finally:
        driver.quit()

    return urls


def is_valid_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))
        width, height = img.size
        file_format = img.format.lower()

        return file_format in ["jpeg", "jpg", "png"] and width > 900 and height > 900
    except Exception:
        return False


def extract_image_urls_from_page(url):
    driver = create_chrome_driver()
    image_urls = set()
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        for img_tag in soup.find_all("img", src=True):
            full_url = urljoin(url, img_tag["src"])
            if is_valid_image(full_url):
                image_urls.add(full_url)

        print(f"Extracted {len(image_urls)} valid image URLs from {url}")
    except Exception as e:
        print(f"Error processing {url}: {e}")
    finally:
        driver.quit()

    return image_urls


def output_to_html(urls, output_file, max_images=0):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Image Gallery</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/css/lightbox.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
.image-container {display:flex;justify-content:center;flex-wrap:wrap;margin-top:20px;}
.card img {object-fit:cover;}
.checkbox-wrapper {text-align:center;margin-top:10px;}
</style>
</head>
<body>
<main class="container">
<div class="row image-container">
""")

        count = 0
        for url in urls:
            if max_images > 0 and count >= max_images:
                break

            file.write(f"""
<div class="col-md-3 mt-4">
  <div class="card" style="width: 18rem;">
    <a href="{url}" data-lightbox="image-gallery" data-title="Image {count}">
      <img src="{url}" class="card-img-top" width="150" height="150">
    </a>
    <div class="checkbox-wrapper">
      <input type="checkbox" checked> Select
    </div>
  </div>
</div>
""")
            count += 1

        file.write(f"""
</div>
<center>
<button class="mt-5 mb-5 btn btn-primary">Download {count}</button>
</center>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox-plus-jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")


def extract_urls_from_html(html_file):
    urls = set()
    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                urls.add(a_tag["href"])
    except Exception as e:
        print(f"Error reading {html_file}: {e}")

    print(f"Extracted {len(urls)} URLs from {html_file}")
    return urls


# -------------------------
# Main program
# -------------------------

def main():
    website_url = ""      # PUT TARGET URL HERE
    domain_filter = ""    # PUT DOMAIN FILTER HERE (example.com)
    max_images = 0        # 0 = unlimited

    # Step 1: extract links from website
    extracted_urls = extract_href_from_page(website_url, domain_filter)

    # Step 2: output initial HTML
    output_file = "images.html"
    output_to_html(extracted_urls, output_file, max_images)

    # Step 3: extract image URLs from HTML
    urls_from_html = extract_urls_from_html(output_file)

    all_image_urls = set()
    for url in urls_from_html:
        if not urlparse(url).scheme:
            continue
        print(f"Processing: {url}")
        all_image_urls.update(extract_image_urls_from_page(url))

    # Step 4: output combined images HTML
    final_output = "combined_images.html"
    output_to_html(all_image_urls, final_output, max_images)

    print("DONE")


if __name__ == "__main__":
    main()
