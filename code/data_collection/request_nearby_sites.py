import os
if not os.path.exists("./data/raw"):
    os.makedirs("./data/raw")
# Google Maps - Places API
import googlemaps
# For data manipulation
import pandas as pd
# For time delay when running loop
import time

# Function to convert miles to meters
def miles_to_meters(miles):
    try:
        return miles * 1_609.344
    except:
        return 0

api_key = open('/c/Users/4p0nc/OneDrive - hawaii.edu/Desktop/hawaii_tcrum/code/data_collection/googlemaps_apikey.txt', 'r').read()
map_client = googlemaps.Client(api_key)

# Define location and distance for each island

islands = [
{"name": "Niihau", "location": (21.895764744451487, -160.1545237357703), "distance": miles_to_meters(10)},
{"name": "Kauai", "location": (22.05598022193704, -159.5293056706187), "distance": miles_to_meters(20)},
{"name": "Oahu", "location": (21.479203973491433, -157.97577324414377), "distance": miles_to_meters(25)},
{"name": "Molokai", "location": (21.133759434812383, -157.02545585613984), "distance": miles_to_meters(20)},
{"name": "Lanai", "location": (20.83115403114689, -156.92932548168125), "distance": miles_to_meters(11)},
{"name": "Kahoolawe", "location": (20.551087156437852, -156.61346855866293), "distance": miles_to_meters(7)},
{"name": "Hawaii", "location": (19.604300849330407, -155.48414172341288), "distance": miles_to_meters(55)}
]

# Loop over each island location and distance
for island in island_data:
    location = island["location"]
    distance = island["distance"]

    sites = []

    # Loop over each search term
    for search_term in search_list:
        # Requesting first page
        response = map_client.places_nearby(
            location = island["location"],
            radius = island["distance"],
            keyword = search_term
        )

        sites.extend(response.get('results'))
        next_page_token = response.get('next_page_token')

        # If available, requesting next pages
        while next_page_token:
            time.sleep(2)

            response = map_client.places_nearby(
                location = island["location"],
                radius = island["distance"],
                keyword = search_term,
                page_token = next_page_token
            )

            sites.extend(response.get('results'))
            next_page_token = response.get('next_page_token')
    
    print(f'Search complete for {island["island"]} for search term: {search_term}')

# Creating dataset
df = pd.DataFrame(sites)

# Creating new variables and subsetting data
df['url'] = 'https://www.google.com/maps/place/?q=place_id:' + df['place_id']
df = df[['name', 'island', 'vicinity', 'types', 'user_ratings_total', 'rating', 'place_id', 'url', 'geometry']]

# Outputing dataframe to csv file in "data/raw" folder
df.to_csv("data/raw/nearby_sites_places_api.csv", index = False)

print('Data collection and export complete')


# Notes:
# Tried filtering results by including parameter 'type' and specifying 'natural_feature' only, but it limited my search results -- can just filter later to ensure I get a more accurate list of sites

# Resources:
# https://www.youtube.com/watch?v=YwIu2Rd0VKM
# https://stackoverflow.com/questions/60536764/how-to-loop-a-list-of-queries-via-restful-api
# https://googlemaps.github.io/google-maps-services-python/docs/

# To fix:
# Filter 'types' to include only: natural_feature, establishment, point_of_interest, park, tourist_attraction to get rid of unwanted sites -- Don't want: store, car_repair, campground, lodging, travel_agency, school, restaurant, food, transit_station, bus_station, local_government_office, convenience_store, cafe, bar