# Goal: I want to web scrape data for all beaches for each island, specifically the description (for later text analysis), facilities and activities. 

# Following tutorials: 
# https://www.youtube.com/watch?v=j7VZsCCnptM&t=7221s
# https://www.youtube.com/watch?v=OxbvFiYxEzI

# For modifying the env. var. `PATH` and adding new directory path
import os

# For nytnyt function
import random
import time

# For web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# For dataset
import pandas as pd
import csv

# To access chromedriver.exe and run an interactive Chrome browser
os.environ['PATH'] += r"C:/webdrivers"

# Initialize web driver
driver = webdriver.Chrome()

# Create an empty dataframe to store the information
df = pd.DataFrame(columns=['name', 'description', 'facilities', 'activities'])

# List of islands To-Hawaii.com provides data on , 'kauai', 'big-island', 'lanai', 'molokai'
islands = ['oahu', 'maui']

for island in islands:
    # Go to the island's beaches page
    driver.get(f'https://www.to-hawaii.com/{island}/beaches')
    
    # Wait for the page to load
    wait = WebDriverWait(driver, 7)

    # Use the CSS selector to locate the links for each beach
    beach_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".images_tabbox .images_tabbox_heading a[href]")))
    
    # Iterate through each beach link
    for link in beach_links:
        # Click on the link
        link.click()

        # Wait for the beach page to load
        wait.until(EC.presence_of_element_located((By.ID, "content")))

        # Extract the name of the beach
        try:
            name = driver.find_element_by_css_selector("h1.title span[itemprop='name']").text
        except NoSuchElementException:
            name = driver.find_element_by_css_selector("h2.small").text

        # Extract the HTML of the description element
        html_descriptions = driver.find_elements_by_css_selector("div.midpanel_row p")
        description_text = ""

        for html_description in html_descriptions:
            # Use BeautifulSoup to parse the HTML and extract the text of the span
            soup = BeautifulSoup(html_description.get_attribute('innerHTML'), 'html.parser')
            description_text += soup.get_text()

        # Click on the "Facilities" tab
        driver.find_element_by_css_selector("#menu3 a").click()
        # Wait for the facilities tab to load
        wait.until(EC.presence_of_element_located((By.ID, "contenttab3")))
        # Extract the text from the facilities list
        facilities = driver.find_element_by_css_selector("#contenttab4 .mylist").text

        # Click on the "Activities" tab
        driver.find_element_by_css_selector("#menu4 a").click()
        # Wait for the activities tab to load
        wait.until(EC.presence_of_element_located((By.ID, "contenttab4")))
        # Extract the text from the activities list
        activities = driver.find_element_by_css_selector("#contenttab4 .mylist").text

        # Append the information to the dataframe
        df = df.append({'name': name, 'description': description_text, 'facilities': facilities, 'activities': activities}, ignore_index=True)

        # Go back to the previous page
        driver.back()
        # Wait for the page to load
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".images_tabbox .images_tabbox_heading a[href]")))
        beach_links = driver.find_elements_by_css_selector(".images_tabbox .images_tabbox_heading a[href]")

        

# Description: Parking and/or access fees for residents and non-residents, mantas, dolphins, whales, turtles, seals, sand type

# Facilities: Lifeguard, paved parking, showers, restrooms

# Activities: Surfing, snorkeling

# driver.quit()
