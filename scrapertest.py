import os
import shutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def parse_categories(filename):
    categories = {}
    with open(filename, 'r') as file:
        current_category = None
        for line in file:
            line = line.strip()
            if line:
                if line.startswith('-'):
                    subcategory = line[1:].strip()
                    if current_category not in categories:
                        categories[current_category] = []
                    categories[current_category].append(subcategory)
                else:
                    current_category = line.rstrip(':')
    return categories

def scrape_images(tag, filter_transparent=False, filter_bw=False):
    scroll_num = 2
    sleep_timer = 10
    url = f'https://www.google.com/search?hl=en&tbm=isch&q={tag}'

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    s = Service('C:\\Users\\Nicholas Surmon\\Documents\\TestPythonAIs\\scraper\\chromedriver.exe')
    driver = webdriver.Chrome(service=s, options=options)

    driver.get(url)

    if filter_transparent or filter_bw:
        try:
            tools_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[contains(text(),"Tools")]'))
            )
            tools_button.click()

            color_filter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[contains(text(),"Color")]'))
            )
            color_filter_button.click()

            if filter_transparent:
                transparent_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Transparent")]'))
                )
                transparent_option.click()
            elif filter_bw:
                bw_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Black and white")]'))
                )
                bw_option.click()

        except Exception as e:
            print("Could not apply filter:", e)


    try:
        os.makedirs(os.path.join(os.getcwd(), 'scraper', 'images'), exist_ok=True)
    except Exception as e:
        print("Error creating directory:", e)

   
    for _ in range(scroll_num):

        try:
            # Wait for the 'Show more results' button to be clickable
            show_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@value="Show more results"]'))
            )

            if show_more_button:
                show_more_button.click()
                time.sleep(sleep_timer)
                
        except Exception as e:
            print("No 'Show more results' button or timed out waiting for it:")
            
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_timer)

    image_links = []
    thumbnails = driver.find_elements(By.CSS_SELECTOR, 'img.rg_i.Q4LuWd')
    for img in thumbnails:
        try:
            src_link = img.get_attribute('src')
            if src_link:
                image_links.append(src_link)
        except Exception as e:
            print("Error retrieving thumbnail link:", e)

    # Remove duplicates by converting the list to a set and back to a list
    image_links = list(set(image_links))

    driver.quit()
    return image_links

def save_image(link, index, sub_category, main_category, saved_urls):
    base_dir = 'C:\\Users\\Nicholas Surmon\\Documents\\TestPythonAIs\\scraper\\images'
    subcategory_dir = os.path.join(base_dir, 'subcategories', sub_category)
    main_category_dir = os.path.join(base_dir, 'main categories', main_category)

    # Ensure both directories exist
    os.makedirs(subcategory_dir, exist_ok=True)
    os.makedirs(main_category_dir, exist_ok=True)

    # Define file paths
    subcategory_file_path = os.path.join(subcategory_dir, f'{index}.png')
    main_category_file_path = os.path.join(main_category_dir, f'{index}_{sub_category}.png')

    try:
        # Check if the URL is already saved
        if link not in saved_urls:
            response = requests.get(link, stream=True)
            with open(subcategory_file_path, 'wb') as out_file:
                out_file.write(response.content)
            # Copy the file to the main category directory
            shutil.copy(subcategory_file_path, main_category_file_path)
            saved_urls.add(link)
            print(f"Saved image {index} in {sub_category} folder and copied to {main_category} folder.")
        else:
            print(f"Skipped duplicate image {index} in {sub_category} folder.")
    except Exception as e:
        print(f'FAILED to save image {index}: {e}')

def process_category(category, subcategories):
    print(f"Processing category: {category}")
    for subcategory in subcategories:
        filter_transparent = subcategory.startswith('*')
        filter_bw = subcategory.startswith('^')
        
        if filter_transparent:
            search_term = subcategory[1:].strip()
            folder_name = search_term + " transparent"
        elif filter_bw:
            search_term = subcategory[1:].strip()
            folder_name = search_term + " black and white"
        else:
            search_term = subcategory.strip()
            folder_name = search_term
        
        print(f"Processing subcategory: {search_term} in category: {category}")
        saved_urls = set()
        image_links = scrape_images(search_term, filter_transparent, filter_bw)
        for idx, link in enumerate(image_links, start=1):
            save_image(link, idx, folder_name, category, saved_urls)
    print(f"Finished processing category: {category}")



categories = parse_categories('C:\\Users\\Nicholas Surmon\\Documents\\TestPythonAIs\\scraper\\tags.txt')

for category, subcategories in categories.items():
    process_category(category, subcategories)