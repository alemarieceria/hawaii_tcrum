"""

This script scrapes data from coastal sites in Hawaii and saves it in a CSV file. It uses Selenium and ChromeDriver to navigate to the website and extract information from various elements using XPATH expressions. The setup_driver() function creates a new Chrome webdriver instance. The get_site_data(site_url) function navigates to a given site URL, waits for elements to appear, and extracts the name, description, facilities, and activities of the site. The get_coastal_site_links(island) function navigates to a URL that lists all coastal sites on a given Hawaiian island and extracts the links to those sites. The main() function loops through all islands and all coastal sites, checks if a given site's data has already been scraped and saved to a CSV file, and if not, calls get_site_data() to scrape and save the data. The function also loads any previously saved data from the file, appends new site data to it, and saves it back to the file after each iteration.

Created on Sun Feb 12 01:00:00 2023

Project: Expanding the Fezzi et al. Travel-Cost RUM to Hawaii
Author: Alemarie Ceria
Affiliation: Oleson Lab, Department of Natural Resources and Environmental Management, University of Hawaii at Manoa

"""

import os
import csv
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    # Returns a Chrome webdriver instance using ChromeDriverManager to install the appropriate version of the driver
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def get_site_data(site_url):
    # Uses a webdriver to navigate to a site url and scrape data 
    driver = setup_driver()
    driver.get(site_url)

    # Waits up to 5 seconds for the presence of an element with the given XPATH expression
    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.XPATH, "//h1[@class='title']//span[@itemprop='name']")))

    # Stores site data in a dictionary
    data = {}
    try:
        data["name"] = driver.find_element(By.XPATH, "//h1[@class='title']//span[@itemprop='name']").text
    except NoSuchElementException:
        data["name"] = None

    # Joins text of all elements with the given XPATH expression, storing the result in the 'description' key of the data dictionary
    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='midpanel_row']//p")))
    try:
        data["description"] = " ".join([e.text for e in driver.find_elements(By.XPATH, "//div[@class='midpanel_row']//p") if not e.text.startswith("$")])
    except NoSuchElementException:
        data["description"] = None

    # Clicks an element, waits for the presence of another element, finds that element, and stores its text in the 'facilities' key of the data dictionary
    try:
        facilities_button = driver.find_element(By.XPATH, "//*[@id='menu0.5']/a")
        facilities_button.send_keys(Keys.RETURN)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='contenttab0.5']/ul")))
        facilities_element = driver.find_element(By.XPATH, "//*[@id='contenttab0.5']/ul")
        data["facilities"] = facilities_element.text.lower().replace("\n", ", ")
    except NoSuchElementException:
        data["facilities"] = None

    # Clicks an element, waits for the presence of another element, finds that element, and stores its text in the 'activities' key of the data dictionary
    try:
        activities_button = driver.find_element(By.XPATH, "//*[@id='menu4']/a")
        activities_button.send_keys(Keys.RETURN)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='contenttab4']/ul")))
        activities_element = driver.find_element(By.XPATH, "//*[@id='contenttab4']/ul")
        data["activities"] = activities_element.text.lower().replace("\n", ", ")
    except NoSuchElementException:
        data["activities"] = None

    # Closes the driver and returns the data dictionary
    driver.quit()
    return data

def get_coastal_site_links(island):
    # Uses a webdriver to navigate to a URL and find all coastal site links on the page, then stores their href attributes in a list
    driver = setup_driver()
    
    # Navigates to a URL that lists all the coastal sites on an island
    driver.get(f"https://www.to-hawaii.com/{island}/beaches/")

    # Finds all elements that match the given XPATH expression, which should correspond to links to individual coastal sites
    coastal_site_links = driver.find_elements(By.XPATH, "//span[@itemprop='name']//a[@href]")

    # Extracts the 'href' attribute from each link element and stores the result in a list
    links = [link.get_attribute("href") for link in coastal_site_links]

    # Closes the webdriver
    driver.quit()

    # Returns the list of coastal site links
    return links


def main():
    # Define the file path for the CSV file that will store the scraped data
    file_path = '../../data/raw/to_hawaii_sites.csv'
    
    # Create an empty list to store the scraped data
    all_coastal_sites_data = []
    
    # Check if the file already exists
    if os.path.exists(file_path):
        # If the file exists, read the existing data into the `all_coastal_sites_data` list
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            all_coastal_sites_data = list(reader)
    
    # Create a set of site links that already have data collected
    site_links = {row['site_link'] for row in all_coastal_sites_data}
    
    # Define the list of islands to search
    islands = ['oahu', 'kauai', 'big-island', 'lanai', 'molokai']
    
    # Loop through each island and scrape data for its coastal sites
    for island in islands:
        for site_link in get_coastal_site_links(island):
            # Skip this site if data has already been collected for it
            if site_link in site_links:
                continue
            try:
                # Collect data for the site using the `get_site_data` function
                site_data = get_site_data(site_link)
                
                # Add the island name and site link to the data dictionary
                site_data["island"] = island.capitalize() if island != "big-island" else "Hawaii"
                site_data["site_link"] = site_link
                
                # Add the collected data to the `all_coastal_sites_data` list
                all_coastal_sites_data.append(site_data)
                site_links.add(site_link)
                
                # Append the data to the CSV file
                with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
                    # Seek to the end of the file before writing
                    f.seek(0, os.SEEK_END)
                    
                    # Get the field names from the first row of data, or an empty list if there is no data
                    fieldnames = all_coastal_sites_data[0].keys() if all_coastal_sites_data else []
                    
                    # Create a DictWriter object to write the data to the CSV file
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    # Write the header row to the file if the file is empty
                    if os.path.getsize(file_path) == 0:
                        writer.writeheader()
                    
                    # Write the current row of data to the file
                    writer.writerow(site_data)
            except Exception as e:
                # Print an error message if there was a problem collecting data for this site
                print(f'Error processing {site_link}: {e}')

    # check that new data was added to the file
    print(f"Number of rows in file: {len(all_coastal_sites_data)}")

if __name__ == "__main__":
    main()
