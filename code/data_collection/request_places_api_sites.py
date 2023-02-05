# Google Maps Places API - Nearby Search Documentation: https://developers.google.com/maps/documentation/places/web-service/search-nearby

import os
import googlemaps # module for accessing Google Maps API
import pandas as pd # data manipulation library
import time # for adding sleep between API calls

# Function to convert miles to meters
def miles_to_meters(miles):
    try:
        # Multiply by conversion factor to get meters
        return miles * 1_609.344 
    except:
        # Return 0 if there's an error
        return 0 

# Function to extract location data from site object
def extract_location_data(site):
    # Extract latitude
    site['lat'] = site['geometry']['location']['lat'] 
    # Extract longitude
    site['lon'] = site['geometry']['location']['lng'] 
    # Create URL
    site['url'] = 'https://www.google.com/maps/place/?q=place_id:' + site['place_id'] 
    return site

# Function to fetch places nearby a given location, within a given distance, with a given search term
def fetch_places_nearby(map_client, location, distance, search_term):
    # List to store nearby sites
    sites = [] 
    # Call Places API to get sites nearby location, with given radius and search term
    response = map_client.places_nearby(location=location, radius=distance, keyword=search_term)
    # Add results to sites list
    sites.extend(response.get('results')) 
    # Get next page token, if there is one
    next_page_token = response.get('next_page_token') 

    # If there's another page, repeat the API call with next_page_token
    while next_page_token:
        # Sleep for 2 seconds between API calls
        time.sleep(2) 
        # Call Places API to get sites nearby location, with given radius, search term, and next page token
        response = map_client.places_nearby(
            location=location, radius=distance, keyword=search_term, page_token=next_page_token)
        # Add results to sites list
        sites.extend(response.get('results')) 
        # Get next page token, if there is one
        next_page_token = response.get('next_page_token') 
    return sites

# Function to collect nearby site data for all islands, using search terms in search_list
def collect_nearby_sites_data(islands, map_client, search_list):
    # List to store all sites
    all_sites = [] 
    # Loop through all islands
    for island in islands:
        # Get island coordinates
        location = island["location"] 
        # Get island search distance
        distance = island["distance"] 
        # Loop through search terms in search_list
        for search_term in search_list:
            # Get nearby sites
            sites = fetch_places_nearby(map_client, location, distance, search_term) 
            # Loop through nearby sites and add island and search term information
            for site in sites:
                # Add island name column
                site['island'] = island['island'] 
                # Add classification column
                site['classification'] = search_term 
                all_sites.append(site)
            # Completed iteration statement
            print(f"Completed coastal site search in {island['island']} for search term: {search_term}")
    return all_sites

# Function to create a dataframe from all_sites
def create_nearby_sites_dataframe(all_sites):
    # Create a Pandas dataframe from the all_sites list
    df = pd.DataFrame(all_sites) 
    # Apply the extract_location_data function on each row of the dataframe
    df = df.apply(extract_location_data, axis=1)
    # Select only the columns we need for our analysis and store in df
    df = df[['name', 'island', 'classification', 'vicinity', 'types', 'user_ratings_total', 'rating', 'place_id', 'url', 'lat', 'lon']]
    return df

# Function to save the dataframe to a csv file
def save_nearby_sites_to_csv(df, file_path):
    # Write the dataframe to a csv file
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

# Main function that performs data collection and export
def main(api_key, islands, search_list):
    # Create a directory to store the raw data if it doesn't already exist
    os.makedirs('../../data/raw', exist_ok=True)
    # Initialize the Google Maps API client with the API key
    map_client = googlemaps.Client(api_key)
    # Collect data on nearby sites using the Google Maps API
    all_sites = collect_nearby_sites_data(islands, map_client, search_list)
    # Create a dataframe from the collected data
    df = create_nearby_sites_dataframe(all_sites)
    # Save the dataframe to a csv file
    save_nearby_sites_to_csv(df, '../../data/raw/places_api_nearby_search_sites.csv')
    # Print a message indicating that the data collection and export is complete
    print('Data collection and export complete')

# Check if the code is run as a standalone script
if __name__ == '__main__':

    # Open the API key file located at the specified path and read its contents
    api_key = open('../places_api_apikey.txt', 'r').read()

    # Define a list of dictionaries representing Hawaiian islands, with island name, location (latitude and longitude), and distance in meters
    islands = [
        {
            "island": "Niihau", 
            "location": (21.895764744451487, -160.1545237357703), 
            "distance": miles_to_meters(10)
        },
        {
            "island": "Kauai", 
            "location": (22.05598022193704, -159.5293056706187), 
            "distance": miles_to_meters(20)
        },
        {
            "island": "Oahu", 
            "location": (21.479203973491433, -157.97577324414377), 
            "distance": miles_to_meters(25)
        },
        {
            "island": "Molokai", 
            "location": (21.133759434812383, -157.02545585613984), 
            "distance": miles_to_meters(20)
        },
        {
            "island": "Lanai", 
            "location": (20.83115403114689, -156.92932548168125), 
            "distance": miles_to_meters(11)
        },
        {
            "island": "Kahoolawe", 
            "location": (20.551087156437852, -156.61346855866293), 
            "distance": miles_to_meters(7)
        },
        {
            "island": "Hawaii", 
            "location": (19.604300849330407, -155.48414172341288), 
            "distance": miles_to_meters(55)
        }
    ]

    # Define a list of search terms to be used
    search_list = ['Bay', 'Beach', 'Beach Park', 'Harbor']

    # Call the main function with the API key, island list, and search terms
    main(api_key, islands, search_list)

# Resources:
# https://www.youtube.com/watch?v=YwIu2Rd0VKM
# https://stackoverflow.com/questions/60536764/how-to-loop-a-list-of-queries-via-restful-api
# https://googlemaps.github.io/google-maps-services-python/docs/

# To fix:
# Filter 'types' to include only: natural_feature, establishment, point_of_interest, park, tourist_attraction to get rid of unwanted sites -- Don't want: store, car_repair, campground, lodging, travel_agency, school, restaurant, food, transit_station, bus_station, local_government_office, convenience_store, cafe, bar