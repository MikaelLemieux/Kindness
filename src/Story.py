import streamlit as st
import pandas as pd

def main():
    st.title('Share Your Kindness Story')

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
                st.session_state['kindness_stories'] = st.session_state['kindness_stories'].append(
                    {'Name': name, 'Kindness Story': kindness_story}, ignore_index=True)
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
    main()
