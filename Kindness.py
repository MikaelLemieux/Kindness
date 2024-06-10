import streamlit as st
import base64
import pandas as pd
from streamlit_option_menu import option_menu
from src.Daily_Kindness_Challenge import kindness_challenge_with_background
from src.Welcome import KindnessToolbox
from src.Affirmations import *
from src.Grattitude_Journal import * 
from src.Daily_Quotes import *
#from src.Story import main as ST
from src.Map import *
from src.feedback_script import *
from src.Kindness_Log import *
from src.Map_Embed import *

# Set page config for wide layout and hide Streamlit menu and footer
st.set_page_config(
    page_title="The Kindness Movement",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="❤️"  # Using a heart emoji as the icon
)

# Custom CSS to remove top margin
st.markdown("""
<style>
    /* Main content area */
    .block-container {
        padding-top: 0 !important;
    }

    /* Streamlit's top bar */
    header {
        visibility: hidden;
    }

    /* Sidebar */
    .sidebar .sidebar-content {
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Hide Streamlit footer and hamburger menu
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Define function to set background image
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
set_webp_as_page_bg('./Imagery/Background.webp', 1000, 600)

col1, col2, col3, col4 = st.columns([4, 1, 4, 4])
with col2:
    st.image("./Imagery/logo.png", use_column_width=True)
with col3:
    st.markdown("<h2 style='text-align: center;'>The Kindness Movement</h2>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center;'>Be the Reason Someone Smiles</h5>", unsafe_allow_html=True)

# Function to load user credentials from a .csv file
def load_user_credentials(filename):
    try:
        df = pd.read_csv(filename, sep=',', index_col=False)
        # Convert the dataframe to a dictionary {username: password}
        return pd.Series(df.password.values, index=df.username).to_dict()
    except Exception as e:
        st.error(f"An error occurred while loading user credentials: {e}")
        return {}

# Function to save user credentials to a .csv file
def save_user_credentials(filename, user_credentials):
    # Load the existing credentials into a DataFrame, if the file exists
    try:
        df_existing = pd.read_csv(filename)
    except FileNotFoundError:
        df_existing = pd.DataFrame(columns=['username', 'password'])
    
    # Convert the updated user_credentials dictionary to a DataFrame
    df_new = pd.DataFrame(list(user_credentials.items()), columns=['username', 'password'])
    
    # Merge the new credentials with the existing ones
    df_merged = pd.concat([df_existing, df_new]).drop_duplicates(subset=['username'], keep='last')
    
    # Save the merged DataFrame back to the CSV file
    df_merged.to_csv(filename, index=False)

# Path to the .csv file where user credentials are stored
credentials_file = './credentials.csv'

# Load user credentials from the .csv file
user_credentials = load_user_credentials(credentials_file)

# Authentication check
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

# Login Form in an Expander
if not st.session_state['authentication_status']:
    st.title("The Kindness Movement - Be the Reason Someone Smiles")
    st.write("Our platform offers a range of tools designed to promote kindness in your daily life. From simple acts of gratitude to random acts of kindness, Kindness Toolbox is here to inspire and empower you to make the world a better place. Dive in and start spreading kindness today!")
    with st.expander("Login"):
        st.warning('Please enter your email and password')
        username = st.text_input("Email", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if username in user_credentials and user_credentials[username] == password:
                st.session_state['authentication_status'] = True
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    
# Button to toggle registration form

        if st.button("New User? Register Here"):
            st.session_state['show_registration_form'] = True
    kindness_news_app2()
# Registration Form
if st.session_state.get('show_registration_form', False):
    st.info("New user? Register here:")
    new_username = st.text_input("Email", key="register_username")
    new_password = st.text_input("New Password", type="password", key="register_password")
    if st.button("Register"):
        if new_username in user_credentials:
            st.error("Username already exists. Please choose a different one.")
        else:
            user_credentials[new_username] = new_password
            save_user_credentials(credentials_file, user_credentials)
            st.success("Registration successful! You can now login.")

    kindness_news_app2()

if st.session_state['authentication_status']:
    # Logout button
    if st.button('Logout'):
        st.session_state['authentication_status'] = None
        st.experimental_rerun()

    # App categories and functions setup
    app_categories = {
        "Welcome": "Welcome",
        "Map": "Kindness Map",
        "Kindness Log": "Kindness Log",
        "Affirmations": "Affirmation of the Day",
        "Gratitude": "Gratitude Journal",
        "Challenges": "Random Acts of Kindness",
        "Quotes": "Kindness Quotes",
#        "Community": "Share Your Kindness Story",
        "Feedback": "Feedback",
    }

    app_functions = {
        "Welcome": KindnessToolbox,
        "Kindness Map": kindness_news_app,
        "Kindness Log": display_kindness_and_news_stories,
        "Random Acts of Kindness": kindness_challenge_with_background,
        "Affirmation of the Day": affirmations_of_the_day,
        "Gratitude Journal" : gratitude_journal_app,
        "Kindness Quotes" : daily_kindness_quotes,
        "Feedback": feedback_form,
#        "Share Your Kindness Story" : ST
    }

    # Option menu for app categories
    selected_category = option_menu(
        menu_title=None, 
        options=list(app_categories.keys()),
        icons=['house', 'bi-globe-americas', 'clipboard-heart', 'book', 'journal-text', 'heart', 'quote', 'chat'],
        menu_icon="cast", 
        default_index=0,
        orientation="horizontal"
    )

    app_selection = app_categories[selected_category]
    if app_selection in app_functions:
        app_functions[app_selection]()
