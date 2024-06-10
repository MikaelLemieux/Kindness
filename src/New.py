import streamlit as st
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
import logging
from urllib.parse import urlparse
import spacy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import pandas as pd
import folium
from streamlit_folium import folium_static
import re
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

geolocator = Nominatim(user_agent="news_geolocator")

# Function to check if a date is within the last 14 days
def is_within_last_14_days(published_date):
    return datetime.now() - published_date <= timedelta(days=14)

# Function to fetch news from Google News RSS feed
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_news_from_google(query):
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    news = []
    for entry in feed.entries:
        published_datetime = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
        if is_within_last_14_days(published_datetime):
            thumbnail = extract_thumbnail(entry.link)
            location = extract_location_from_text(entry.link)
            news.append({
                'title': entry.title,
                'link': entry.link,
                'published': published_datetime,
                'thumbnail': thumbnail,
                'location': location,
                'summary': entry.summary,  # Assuming summary is available
                'source': 'Google News'
            })
    return news

# Function to fetch news from Good News Network
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_news_from_goodnews():
    url = "https://www.goodnewsnetwork.org/?s=kindness"
    session = requests.Session()
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')
    news = []
    for article in articles:
        title = article.find('h3').get_text()
        link = article.find('a')['href']
        summary = article.find('div', class_='entry-content').get_text().strip()
        published_date = article.find('time')['datetime']
        published_datetime = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
        if is_within_last_14_days(published_datetime):
            thumbnail = extract_thumbnail(link)
            location = extract_location_from_text(link)
            news.append({
                'title': title,
                'link': link,
                'published': published_datetime,
                'thumbnail': thumbnail,
                'location': location,
                'summary': summary,
                'source': 'Good News Network'
            })
    return news

def extract_thumbnail(link):
    try:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=0)  # No retries
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(link, timeout=3)  # Reduced timeout to 3 seconds
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image['content']:
            return og_image['content']
    except requests.exceptions.Timeout:
        logging.error(f"Timeout error fetching thumbnail for {link}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching thumbnail for {link}: {e}")
    return "C:/Users/Mikael Lemieux/Documents/Scripts/Curling_Scripts/Imagery/Curling News.png"

def extract_location_from_text(link):
    try:
        session = requests.Session()
        response = session.get(link, timeout=3)  # Reduced timeout to 3 seconds
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            doc = nlp(paragraph.get_text())
            for ent in doc.ents:
                if ent.label_ == "GPE":  # GPE stands for Geopolitical Entity
                    location = geolocator.geocode(ent.text)
                    if location:
                        logging.info(f"Found location: {location} for entity: {ent.text}")
                        return (location.latitude, location.longitude)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error extracting location from {link}: {e}")
    return None

def fetch_stories(page):
    base_url = 'https://www.kindness-map.com/storyList/'
    url = f"{base_url}{page}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

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

def get_coordinates(city, retries=3, timeout=10):
    for _ in range(retries):
        try:
            location = geolocator.geocode(city, timeout=timeout)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError):
            time.sleep(2)
    return None, None

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

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_all_data():
    google_news = fetch_news_from_google("kindness")
    goodnews_network = fetch_news_from_goodnews()
    news_items = google_news + goodnews_network
    
    all_stories, total_pages = get_all_stories()
    
    return news_items, all_stories

def get_all_stories():
    all_stories = []
    total_pages = get_total_pages()
    
    for page in range(1, total_pages + 1):
        html_content = fetch_stories(page)
        if html_content:
            stories = parse_stories(html_content)
            all_stories.extend(stories)
        else:
            st.write(f"Failed to fetch stories from page {page}.")
    return all_stories, total_pages

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

st.title("Kindness Stories and News Map")

if st.button("Fetch News and Stories"):
    with st.spinner("Fetching news and stories..."):
        news_items, all_stories = get_all_data()

    if news_items or all_stories:
        st.success("Data fetched successfully!")
        locations = []
        
        # Add news items to the locations list
        for item in news_items:
            if item['location']:
                locations.append({
                    'lat': item['location'][0], 
                    'lon': item['location'][1],
                    'title': item['title'],
                    'link': item['link'],
                    'published': item['published'],
                    'summary': item['summary'],
                    'source': item['source']
                })
        
        # Add kindness stories to the locations list
        for story in all_stories:
            if story['city']:
                lat, lon = get_coordinates(story['city'])
                if lat and lon:
                    locations.append({
                        'lat': lat,
                        'lon': lon,
                        'title': story['content'],
                        'link': None,
                        'published': None,
                        'summary': story['details'],
                        'source': 'Kindness Story'
                    })
        
        if locations:
            m = folium.Map(location=[20, 0], zoom_start=2, width='100%', height='100%')
            for loc in locations:
                color = 'red' if loc['source'] == 'Google News' else 'blue' if loc['source'] == 'Good News Network' else 'green'
                icon = folium.Icon(color=color, icon='heart')
                folium.Marker(
                    location=[loc['lat'], loc['lon']],
                    tooltip=f"{loc['title']}<br>{loc['published']}<br><a href='{loc['link']}' target='_blank'>Read more</a>" if loc['link'] else loc['title'],
                    popup=folium.Popup(loc['summary'], max_width=300),
                    icon=icon
                ).add_to(m)
            folium_static(m, width=1600, height=800)
            
            # Display data in dataframes
            news_df = pd.DataFrame(news_items)
            stories_df = pd.DataFrame(all_stories)
            
            st.header("News Data")
            st.dataframe(news_df)
            
            st.header("Kindness Stories Data")
            st.dataframe(stories_df)
            
            # Save data to CSV files
            save_to_csv(news_df, 'news_data.csv')
            save_to_csv(stories_df, 'kindness_stories.csv')
            
            st.success("Data saved to CSV files: 'news_data.csv' and 'kindness_stories.csv'")
        else:
            st.write("No locations to display on the map.")
    else:
        st.warning("No news or stories found for the past 14 days.")
else:
    st.write("Click the button above to fetch the latest news and kindness stories.")
