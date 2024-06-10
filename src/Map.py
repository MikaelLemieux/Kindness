import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import ast

def kindness_news_app2():
    

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

kindness_news_app2()
