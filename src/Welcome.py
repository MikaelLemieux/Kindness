import streamlit as st
import csv
import os

def featured_tools():
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([2,1,2,1,2])
        
        with col1:
            st.header("Kindness Map")
            st.image("./Imagery/Map.png", use_column_width=True)

        with col3:
            st.header("Gratitude Journal")
            st.image("./Imagery/Gratitude_Journal.png", use_column_width=True)

        with col5:
            st.header("Kindness Challenges")
            st.image("./Imagery/Kindness_Challenge.png", use_column_width=True)


def KindnessToolbox():

    # Using HTML and Markdown to center the title
    st.markdown("<h1 style='text-align: center;'>Welcome to Kindness Movement Toolbox, your one-stop solution for spreading kindness!</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>  Our platform offers a range of tools designed to promote kindness in your daily life. From simple acts of gratitude to random acts of kindness, Kindness Toolbox is here to inspire and empower you to make the world a better place. Dive in and start spreading kindness today!</h6>", unsafe_allow_html=True)
    featured_tools()


if __name__ == '__main__':
    KindnessToolbox()
