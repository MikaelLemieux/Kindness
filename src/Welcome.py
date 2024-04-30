import streamlit as st
import csv
import os

def KindnessToolbox():

    feedback_dir = "./feedback_data"  # Define the directory path within the container
    os.makedirs(feedback_dir, exist_ok=True)

    feedback_list = []

    # Define the path to the feedback data file within the container
    feedback_file_path = os.path.join(feedback_dir, "feedback.csv")

    def save_feedback_to_csv(feedback_list):
        with open(feedback_file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            for feedback in feedback_list:
                writer.writerow([feedback["Type"], feedback["Feedback"]])

    # Using HTML and Markdown to center the title
    st.markdown("<h1 style='text-align: center;'>Welcome to Kindness Toolbox, your one-stop solution for spreading kindness!</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>  Our platform offers a range of tools designed to promote kindness in your daily life. From simple acts of gratitude to random acts of kindness, Kindness Toolbox is here to inspire and empower you to make the world a better place. Dive in and start spreading kindness today!</h6>", unsafe_allow_html=True)

    if st.button("Help"):
            readme = """
            # Welcome to our Help Section! 

            ### This section is here to guide you on your journey to spreading kindness. Remember, even the smallest acts of kindness can make a big difference!
            """
            st.markdown(readme, unsafe_allow_html=True)

    # Feedback collection form
    st.header("Feedback")

    # Create a text area for users to enter feedback
    user_feedback = st.text_area("Enter your feedback here:")

    # Create a selectbox to choose feedback type
    feedback_type = st.selectbox("Select feedback type:", ["Bug Report", "Feature Request", "General Feedback"])

    # Create a button to submit feedback
    if st.button("Submit Feedback"):
        feedback_entry = {
            "Type": feedback_type,
            "Feedback": user_feedback
        }
        feedback_list.append(feedback_entry)
        save_feedback_to_csv([feedback_entry])  # Save the new feedback entry to CSV
        st.success("Feedback submitted successfully!")

if __name__ == '__main__':
    KindnessToolbox()
