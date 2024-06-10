import streamlit as st
import pandas as pd
import os
import ast

def display_kindness_and_news_stories():
    # Function to load the CSV file and add a color column
    def load_csv(file_path, color, source):
        try:
            df = pd.read_csv(file_path)
            if source == 'news':
                # Extract latitude and longitude from the location field
                df[['latitude', 'longitude']] = df['location'].apply(lambda x: pd.Series(ast.literal_eval(x) if pd.notnull(x) else (None, None)))
                df['content'] = df['title']
                df['details'] = df['summary']
            df['color'] = color
            return df
        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
            return None

    # Specify the paths to the CSV files
    csv_paths = [
        ('./kindness_stories.csv', 'blue', 'kindness'),
        ('./news_data.csv', 'red', 'news')
    ]

    # Load the CSV files
    dfs = [load_csv(path, color, source) for path, color, source in csv_paths]

    # Combine dataframes if both are loaded
    if all(df is not None for df in dfs):
        combined_df = pd.concat(dfs, ignore_index=True)
        st.write(f"Loaded {len(combined_df)} stories from CSV files.")

        # Add custom CSS for expander background color
        st.markdown("""
            <style>
            .stExpander {
                background-color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)

        # Create a list of stories with expanders
        for idx, row in combined_df.iterrows():
            with st.expander(f"Story: {row['content']}"):
                st.write(f"Details: {row['details']}")
                if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                    st.write(f"Location: {row['latitude']}, {row['longitude']}")
    else:
        st.write("No stories found or an error occurred.")

# Call the function to display the list of stories
display_kindness_and_news_stories()
