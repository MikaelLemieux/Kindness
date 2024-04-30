import streamlit as st
import datetime
import random

def daily_kindness_quotes():
    # Function to get today's date
    def get_today_date():
        return datetime.datetime.now().date()

    # Function to generate a random kindness quote
    def generate_quote():
        kindness_quotes = [
            "Kindness is the language which the deaf can hear and the blind can see. - Mark Twain",
            "No act of kindness, no matter how small, is ever wasted. - Aesop",
            "Kindness is a gift everyone can afford to give. - Unknown",
            "Wherever there is a human in need, there is an opportunity for kindness and to make a difference. - Kevin Heath",
            "Kindness is the sunshine in which virtue grows. - Robert Green Ingersoll",
            "Kindness in words creates confidence. Kindness in thinking creates profoundness. Kindness in giving creates love. - Lao Tzu",
            "Unexpected kindness is the most powerful, least costly, and most underrated agent of human change. - Bob Kerrey",
            "The smallest act of kindness is worth more than the grandest intention. - Oscar Wilde"
        ]
        return random.choice(kindness_quotes)

    # Function to check if it's a new day
    def is_new_day():
        today = get_today_date()
        last_date = st.session_state.get('last_date')
        st.session_state['last_date'] = today
        return today != last_date

    st.title('Daily Kindness Quotes')

    if is_new_day():
        st.session_state['quote'] = generate_quote()

    st.write("Here's your daily kindness quote:")
    st.write(st.session_state.get('quote'))

# Run the function
if __name__ == "__main__":
    daily_kindness_quotes()
