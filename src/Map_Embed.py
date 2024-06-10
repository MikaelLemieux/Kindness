import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import ast

# Load city coordinates from the uploaded CSV file
def load_city_coordinates():
    cities_df = pd.read_csv('./cities.csv')
    city_to_coords = {row['city']: (row['lat'], row['lng']) for _, row in cities_df.iterrows()}
    return city_to_coords

city_to_coords = load_city_coordinates()

def kindness_news_app():
    with st.expander("Submit your own kindness story"):
        with st.form("kindness_form"):
            title = st.text_input("Title")
            details = st.text_area("Details")
            city = st.text_input("City")
            submitted = st.form_submit_button("Submit")

            if submitted:
                if title and details and city:
                    if city in city_to_coords:
                        latitude, longitude = city_to_coords[city]
                        new_story = {
                            "title": title,
                            "details": details,
                            "latitude": latitude,
                            "longitude": longitude,
                            "color": "purple"
                        }

                        try:
                            submission_path = './story_submission.csv'
                            new_story_df = pd.DataFrame([new_story])

                            if os.path.exists(submission_path):
                                existing_df = pd.read_csv(submission_path, encoding='latin1', on_bad_lines='skip')
                                updated_df = pd.concat([existing_df, new_story_df], ignore_index=True)
                            else:
                                updated_df = new_story_df

                            updated_df.to_csv(submission_path, index=False, encoding='latin1')
                            st.success("Your story has been added successfully!")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"An error occurred while saving your story: {e}")
                    else:
                        st.error("City not found. Please enter a valid city name.")
                else:
                    st.error("Please fill in all fields.")

    def load_csv(file_path, color, source):
        try:
            df = pd.read_csv(file_path, encoding='latin1', on_bad_lines='skip')
            if source == 'news':
                df[['latitude', 'longitude']] = df['location'].apply(lambda x: pd.Series(ast.literal_eval(x) if pd.notnull(x) else (None, None)))
                df['content'] = df['title']
                df['details'] = df['summary']
            df['color'] = color
            return df
        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
            return None

    csv_paths = [
        ('./kindness_stories.csv', 'blue', 'kindness'),
        ('./news_data.csv', 'red', 'news'),
        ('./story_submission.csv', 'purple', 'submission')
    ]

    dfs = [load_csv(path, color, source) for path, color, source in csv_paths]

    if all(df is not None for df in dfs):
        combined_df = pd.concat(dfs, ignore_index=True)

        stories_map = folium.Map(location=[20, 0], zoom_start=2)

        for idx, row in combined_df.iterrows():
            if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"Story: {row['content']}<br>Details: {row['details']}",
                    icon=folium.Icon(icon='heart', prefix='fa', color=row['color'])
                ).add_to(stories_map)

        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st_folium(stories_map, width='100%', height=500)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("No stories found or an error occurred.")

kindness_news_app()
