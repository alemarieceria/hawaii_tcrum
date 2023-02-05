import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def extract_coastal_site_data(driver, wait):
    """
    Extracts name, description, facilities, and activities for a single coastal site page
    """
    # Find and extract name of coastal site
    name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div.midpanel > div > h1 > span"))).text
    # Find all the p elements within div.new-custom and join their text into a single string.
    description_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div.midpanel > div > div.new-custom > div")))
    description = "".join([p.text for p in description_element.find_elements_by_css_selector("p")])
    # Click on facilities button and extract text from list
    driver.find_element_by_css_selector("#menu3 > a").click()
    facilities = [item.text for item in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#contenttab3 > ul > li")))]
    # Click on activities button and extract text from list
    driver.find_element_by_css_selector("#menu4 > a").click()
    activities = [item.text for item in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#contenttab4 > ul > li")))]
    return {"Name": name, "Description": description, "Facilities": facilities, "Activities": activities}

def scrape_island_coastal_site(driver, wait, island):
    """Scrapes data for each coastal site listed for a given island on the website: https://www.to-hawaii.com/{island}/beaches

    Parameters:
    island (str): The name of the island to scrape beach data for. Should match the name used in the URL, e.g. 'big_island'

    Returns:
    list of dictionaries: A list of dictionaries, where each dictionary contains data for a single beach
    """
    # Open the website using a webdriver
    driver.get(f"https://www.to-hawaii.com/{island}/beaches")

    # Wait for the page to load
    wait = WebDriverWait(driver, 7)

    # Initialize a list to store scraped data
    coastal_sites = []

    # Find the list of coastal sites
    coastal_site_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#wrapper > div.midpanel > div > div.new-custom > div > div:nth-child(6) > div > div.images_tabbox_content > div > div > div.image_with_caption > a")))

    # Loop through each beach in the list
    for i, coastal_site in enumerate(coastal_site_list):
        # Click on the coastal site to navigate to its page
        coastal_site.click()
        # Wait for the page to load
        time.sleep(2)  
        # Scrape the data for the current coastal site
        try:
            data = extract_coastal_site_data(driver, wait)
            coastal_sites.append(data)
        except (StaleElementReferenceException, NoSuchElementException) as e:
            print(f"Error scraping data for beach {i + 1}: {e}")
            continue    
        # Navigate back to the list of beaches
        driver.back()

    return coastal_sites

def main():
    islands = ["oahu", "maui", "kauai", "big_island", "lanai", "molokai"]
    os.environ['PATH'] += r"C:/webdrivers"
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 7)

    all_coastal_sites = []
    
    for island in islands:
        coastal_sites = scrape_island_coastal_site(driver, wait, island)
        all_coastal_sites.extend(coastal_sites)

    # Close the driver when finished
    driver.quit()

    df = pd.DataFrame(all_coastal_sites)
    df.to_csv('../../data/raw/to_hawaii_sties.csv', index = False, encoding = 'utf-8-sig')

# Run the main function if the script is run as the main module
if __name__ == "__main__":
    main()