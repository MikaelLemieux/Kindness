# feedback_script.py
import streamlit as st
import csv
import os

# Define the directory path within the container
feedback_dir = "./feedback_data"
os.makedirs(feedback_dir, exist_ok=True)
feedback_file_path = os.path.join(feedback_dir, "feedback.csv")

def save_feedback_to_csv(feedback_list):
    try:
        with open(feedback_file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            for feedback in feedback_list:
                writer.writerow([feedback["Type"], feedback["Feedback"]])
    except Exception as e:
        st.error(f"Failed to save feedback: {e}")

def feedback_form():
    with st.container():
        st.header("Feedback")
        user_feedback = st.text_area("Enter your feedback here:", key="feedback_field")
        feedback_type = st.selectbox("Select feedback type:", ["Bug Report", "Feature Request", "General Feedback"])

        if st.button("Submit Feedback"):
            feedback_entry = {"Type": feedback_type, "Feedback": user_feedback}
            save_feedback_to_csv([feedback_entry])  # Save the new feedback entry to CSV
            st.success("Feedback submitted successfully!")
            st.text_area("Enter your feedback here:", value="", key="feedback_field")  # Resetting the feedback form

if __name__ == '__main__':
    feedback_form()
