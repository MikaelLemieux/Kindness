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
import pandas as pd
import folium
from streamlit_folium import folium_static

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
@st.cache_data(ttl=600)  # Cache for 10 minutes
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
@st.cache_data(ttl=600)  # Cache for 10 minutes
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
        response = session.get(link, timeout=5)  # Increased timeout to 5 seconds
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
        response = session.get(link, timeout=5)
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

def CN():
    st.title("Latest Stories of Kindness from the Past 14 Days")
    st.write("Click the button below to fetch the latest news articles about kindness.")

    if st.button("Fetch News"):
        with st.spinner("Fetching news..."):
            google_news = fetch_news_from_google("kindness")
            goodnews_network = fetch_news_from_goodnews()
            news_items = google_news + goodnews_network
        if news_items:
            st.success("News fetched successfully!")
            locations = []
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
            
            if locations:
                # Create a folium map
                m = folium.Map(location=[0, 0], zoom_start=2)
                for loc in locations:
                    color = 'red' if loc['source'] == 'Google News' else 'blue'
                    icon = folium.Icon(color=color, icon='heart')
                    folium.Marker(
                        location=[loc['lat'], loc['lon']],
                        tooltip=f"{loc['title']}<br>{loc['published']}<br><a href='{loc['link']}' target='_blank'>Read more</a>",
                        popup=folium.Popup(loc['summary'], max_width=300),
                        icon=icon
                    ).add_to(m)
                folium_static(m)
            else:
                st.write("No locations to display on the map.")
        else:
            st.warning("No news found for the past 14 days.")

    # Section for sharing kindness stories
    st.header("Share Your Kindness Story")

    # Create or load the kindness stories DataFrame
    if 'kindness_stories' not in st.session_state:
        st.session_state['kindness_stories'] = pd.DataFrame(columns=['Name', 'Kindness Story'])

    # Create a collapsible expander for sharing stories
    with st.expander("Share Your Story", expanded=True):
        # Input fields for name and kindness story
        name = st.text_input('Your Name')
        kindness_story = st.text_area('Your Kindness Story')

        # Button to submit the kindness story
        if st.button('Share'):
            if name.strip() and kindness_story.strip():
                new_story = pd.DataFrame({'Name': [name], 'Kindness Story': [kindness_story]})
                st.session_state['kindness_stories'] = pd.concat([st.session_state['kindness_stories'], new_story], ignore_index=True)
                st.success('Your kindness story has been shared!')
            else:
                st.error('Please enter your name and kindness story before sharing.')

    # Display kindness stories
    st.header('Kindness Stories Shared By Others')
    if not st.session_state['kindness_stories'].empty:
        st.dataframe(st.session_state['kindness_stories'])
    else:
        st.write('No kindness stories shared yet.')

if __name__ == "__main__":
    CN()
