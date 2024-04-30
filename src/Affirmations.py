import streamlit as st
import random

def affirmations_of_the_day():
    # List of affirmations
    affirmations = [
        "I am worthy of love and respect.",
        "I am capable of achieving my goals.",
        "I believe in myself and my abilities.",
        "I radiate confidence and positivity.",
        "I attract abundance and success into my life.",
        "I am grateful for all that I have.",
        "I am becoming the best version of myself.",
        "I am surrounded by love and support.",
        "I trust the journey of life.",
        "I am deserving of happiness and fulfillment.",
        "I am enough, just as I am.",
        "I embrace change and growth.",
        "I forgive myself and others, and release negativity.",
        "I am courageous and resilient in the face of challenges.",
        "I am creating a life filled with joy and purpose.",
        "I am worthy of all the good things life has to offer.",
        "I am in control of my thoughts and emotions.",
        "I choose to focus on the present moment.",
        "I am a magnet for miracles and blessings.",
        "I am connected to the wisdom of the universe.",
    ]

    # Function to get a random affirmation
    def get_random_affirmation():
        return random.choice(affirmations)

    # Display title
    st.markdown("<h1 style='text-align: center;'>Affirmations of the Day</h1>", unsafe_allow_html=True)

    # Display affirmation
    st.write("Ready for today's affirmation?")

    # Large button to get affirmation
    if st.button("Get Affirmation", key="affirmation_button"):
        affirmation = get_random_affirmation()
        st.write(f"Your affirmation for today is:")
        st.write(f"## {affirmation}")

    # Explanation and motivation
    st.write("""
        Daily affirmations are positive statements that can help you challenge and overcome negative thoughts. 
        By repeating affirmations daily, you can reprogram your subconscious mind to focus on the positive 
        aspects of life and boost your self-esteem and confidence. Take a moment to embrace today's affirmation 
        and let it guide you towards a more positive and fulfilling day.
    """)

if __name__ == "__main__":
    affirmations_of_the_day()
