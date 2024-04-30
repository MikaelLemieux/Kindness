import streamlit as st
import pandas as pd
import datetime

def gratitude_journal_app():
    # Function to load gratitude journal entries from a CSV file
    def load_gratitude_journal(filename):
        try:
            df = pd.read_csv(filename, encoding='utf-8')
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=['Date', 'Entry'])

    # Function to save gratitude journal entries to a CSV file
    def save_gratitude_entry(filename, date, entry):
        try:
            with open(filename, 'a') as file:
                file.write(f"{date},{entry}\n")
            return True
        except Exception as e:
            st.error(f"Error saving entry: {e}")
            return False

    # Path to the CSV file where gratitude journal entries are stored
    gratitude_journal_file = './gratitude_journal.csv'

    # Function to display the Gratitude Journal interface
    def gratitude_journal():
        st.header("Gratitude Journal")
        
        # Load existing journal entries
        journal_df = load_gratitude_journal(gratitude_journal_file)
        
        # Display existing journal entries in a collapsible expander
        with st.expander("Previous Entries"):
            if not journal_df.empty:
                st.write(journal_df)
            else:
                st.write("No previous entries.")

        # Add new entry
        st.subheader("Add New Entry:")
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        entry = st.text_area("Today, I am grateful for...", key="gratitude_entry")
        if st.button("Add Entry"):
            if entry.strip() == "":
                st.warning("Please enter something you are grateful for.")
            else:
                if save_gratitude_entry(gratitude_journal_file, today_date, entry):
                    st.success("Entry added successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Failed to add entry. Please try again later.")

    gratitude_journal()

if __name__ == "__main__":
    gratitude_journal_app()
