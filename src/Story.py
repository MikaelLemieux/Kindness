import streamlit as st
import requests
from bs4 import BeautifulSoup
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re
import time
import pandas as pd
import os

# Function to fetch stories from a specific page
@st.cache_data
def fetch_stories(page):
    base_url = 'https://www.kindness-map.com/storyList/'
    url = f"{base_url}{page}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

# Function to parse stories from the HTML content
@st.cache_data
def parse_stories(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    stories = []
    for story_div in soup.find_all('div', class_='card testimonial-card rowid'):
        story = {
            'content': story_div.find('p').text.strip(),
            'details': story_div.find('p', class_='small').text.strip()
        }

        # Extract country and city/state from details
        match = re.search(r',\s*([A-Za-z\s]+),\s*([A-Za-z\s]+)', story['details'])
        if match:
            location = match.group(1).strip()
            country = match.group(2).strip()
            story['city'] = f"{location}, {country}"
        else:
            story['city'] = None
        
        stories.append(story)
    return stories

# Function to get latitude and longitude from city name
@st.cache_data
def get_coordinates(city, retries=3, timeout=10):
    geolocator = Nominatim(user_agent="kindness_stories")
    for _ in range(retries):
        try:
            location = geolocator.geocode(city, timeout=timeout)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError):
            time.sleep(2)
    return None, None

# Function to get the total number of pages
@st.cache_data
def get_total_pages():
    base_url = 'https://www.kindness-map.com/storyList/1'
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        pagination = soup.find('ul', class_='pagination')
        if pagination:
            total_pages = 38
            return total_pages
    except requests.RequestException:
        pass
    return 38  # Default value if unable to fetch the pages

# Streamlit app
st.title("Kindness Stories Map")

@st.cache_data
def get_all_stories():
    all_stories = []
    total_pages = get_total_pages()
    
    for page in range(1, total_pages + 1):
        html_content = fetch_stories(page)
        if html_content:
            stories = parse_stories(html_content)
            all_stories.extend(stories)
            st.write(f"Scraped {len(stories)} stories from page {page}.")  # Debug statement
        else:
            st.write(f"Failed to fetch stories from page {page}.")
    return all_stories, total_pages

all_stories, total_pages = get_all_stories()

if all_stories:
    st.write(f"Scraped {len(all_stories)} stories from {total_pages} pages.")
    
    # Create a DataFrame
    df = pd.DataFrame(all_stories)
    
    # Get coordinates for each story
    df['latitude'] = None
    df['longitude'] = None

    for idx, row in df.iterrows():
        if row['city']:
            lat, lon = get_coordinates(row['city'])
            if lat and lon:
                df.at[idx, 'latitude'] = lat
                df.at[idx, 'longitude'] = lon
            else:
                st.write(f"Could not geocode city: {row['city']}")
        else:
            st.write("No city found in details:", row['details'])

    # Save to CSV in the same directory as the script
    csv_path = os.path.join(os.path.dirname(__file__), 'kindness_stories.csv')
    df.to_csv(csv_path, index=False)
    
    # Provide download link
    with open(csv_path, "rb") as file:
        btn = st.download_button(
            label="Download data as CSV",
            data=file,
            file_name='kindness_stories.csv',
            mime='text/csv',
        )

    # Create a map centered on a default location
    kindness_map = folium.Map(location=[20, 0], zoom_start=2)
    
    for idx, row in df.iterrows():
        if row['latitude'] and row['longitude']:
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Story: {row['content']}<br>Details: {row['details']}"
            ).add_to(kindness_map)

    # Display the map using st_folium
    st_folium(kindness_map, width=700, height=500)
else:
    st.write("No stories found or an error occurred.")
