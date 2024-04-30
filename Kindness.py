import streamlit as st
import base64
import pandas as pd
import bcrypt
from src.Daily_Kindness_Challenge import kindness_challenge_with_background
from src.Welcome import KindnessToolbox
from src.Affirmations import *
from src.Grattitude_Journal import * 
from src.Daily_Quotes import *
from src.Story import main as ST


# Set page config for wide layout and hide Streamlit menu and footer
st.set_page_config(
    page_title="Daily Kindness App",
    layout="wide",
    initial_sidebar_state="collapsed"
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

st.title("Daily Kindness App")

# Function to load user credentials from a .csv file
def load_user_credentials(filename):
    try:
        df = pd.read_csv(filename, sep=',', index_col=False)
        # Convert the dataframe to a dictionary {username: password_hash}
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

# Login Form
if not st.session_state['authentication_status']:
    st.warning('Please enter your email and password')
    username = st.text_input("Email", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        # Here we check the password against the hashed password
        if username in user_credentials and bcrypt.checkpw(password.encode('utf-8'), user_credentials[username].encode('utf-8')):
            st.session_state['authentication_status'] = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# Button to toggle registration form
if not st.session_state['authentication_status']:
    if st.button("New User? Register Here"):
        st.session_state['show_registration_form'] = True

# Registration Form
if st.session_state.get('show_registration_form', False):
    st.info("New user? Register here:")
    new_username = st.text_input("Email", key="register_username")
    new_password = st.text_input("New Password", type="password", key="register_password")
    if st.button("Register"):
        if new_username in user_credentials:
            st.error("Username already exists. Please choose a different one.")
        else:
            # Here we hash the new user's password before saving
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_credentials[new_username] = hashed_new_password
            save_user_credentials(credentials_file, user_credentials)
            st.success("Registration successful! You can now login.")

if st.session_state['authentication_status']:
    # Logout button
    if st.button('Logout'):
        st.session_state['authentication_status'] = None
        st.rerun()

    # App categories and functions setup
    app_categories = {
        "Welcome":["Welcome"],
        "Daily Affirmations": ["Affirmation of the Day", "Gratitude Journal"],
        "Kindness Challenges": ["Random Acts of Kindness", "Kindness Quotes"],
        "Community": ["Share Your Kindness Story"],
    }

    app_functions = {
        "Welcome": KindnessToolbox,
        "Random Acts of Kindness": kindness_challenge_with_background,
        "Affirmation of the Day": affirmations_of_the_day,
        "Gratitude Journal" : gratitude_journal_app,
        "Kindness Quotes" : daily_kindness_quotes,
        "Share Your Kindness Story" : ST
    }

    # Tabs for app categories
    tab_labels = list(app_categories.keys())
    tabs = st.tabs(tab_labels)

    for tab_label in tab_labels:
        with tabs[tab_labels.index(tab_label)]:
            app_selection = st.radio(f"{tab_label}:", app_categories[tab_label])
            if app_selection in app_functions:
                app_functions[app_selection]()
