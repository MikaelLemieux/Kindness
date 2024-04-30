import streamlit as st
import random
import base64

def kindness_challenge_with_background():
    # Function to set background image
    def set_webp_as_page_bg(webp_file, width, height):
        bin_str = base64.b64encode(open(webp_file, 'rb').read()).decode()
        page_bg_img = f'''
            <style>
                .stApp {{
                    background-image: url("data:image/webp;base64,{bin_str}");
                    background-size: cover;
                }}
            </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

    # Set background image
    set_webp_as_page_bg('./Imagery/Daily_Challenge.webp', 1000, 600)

    # Function to generate a random kindness challenge
    def generate_kindness_challenge():
        challenges = [
            "Smile at a stranger and say hello.",
            "Send a thank you note to someone who has helped you.",
            "Pay for the coffee of the person behind you in line.",
            "Give someone a compliment.",
            "Donate clothes or items you no longer need.",
            "Help a neighbor with a task or errand.",
            "Leave a positive review for a local business.",
            "Offer to listen to someone who needs to talk.",
            "Send an encouraging message to a friend or family member.",
            "Volunteer your time at a local charity or organization.",
            "Buy a meal for someone in need.",
            "Hold the door open for someone.",
            "Leave a generous tip for a server or delivery person.",
            "Give someone a hug (with their consent).",
            "Leave a kind note on a coworker's desk.",
            "Compliment a stranger's pet.",
            "Offer to help someone carry their groceries.",
            "Say 'thank you' to someone who provides you a service today.",
            "Write a positive message on a public chalkboard or whiteboard.",
            "Share a motivational quote on social media."
        ]
        return random.choice(challenges)

    # Display daily kindness challenge
    st.write("# Daily Kindness Challenge")
    st.write("Ready for today's challenge?")

    # Large button to engage the challenge
    if st.button("Get Today's Challenge", key="challenge_button"):
        challenge = generate_kindness_challenge()
        st.write(f"Your challenge for today is:")
        st.write(f"## {challenge}")

    # Explanation and motivation
    st.write("""
        Completing small acts of kindness can have a big impact on both the giver and the receiver. 
        Take on today's challenge and spread some kindness in the world!
    """)

if __name__ == "__main__":
    kindness_challenge_with_background()
