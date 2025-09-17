# app.py

import streamlit as st
from pathlib import Path
from scraping import scrape_instagram,cookie_file # Import your main function

# --- Page Configuration ---
st.set_page_config(
    page_title="Instagram Scraper",
    page_icon="📸",
    layout="wide"
)

# --- App UI ---
st.title("📸 Instagram Profile & Activity Scraper")
st.info("Enter your Instagram credentials to generate screenshots of your profile and activity. The process may take several minutes.")

# --- User Input Form ---
with st.form("credentials_form"):
    st.subheader("Enter Your Instagram Credentials")
    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Start Scraping")

if st.button("Delete Cookies"):
    if cookies_file.exists():
        cookies_file.unlink()
        st.success("Cookies file deleted ✅")
    else:
        st.warning("No cookies file found.")

# --- Scraper Execution ---
if submitted:
    if not username or not password:
        st.error("Please provide both a username and a password.")
    else:
        # Placeholder for live status updates from the scraper
        status_placeholder = st.empty()

        def update_status(message):
            """This function is passed to the scraper to update the UI in real-time."""
            status_placeholder.info(f"⏳ {message}")

        try:
            # Show a spinner while the main function is running
            with st.spinner("Scraping in progress... Please wait."):
                screenshot_paths = scrape_instagram(username, password, update_status)
            
            status_placeholder.empty() # Clear the last status message
            st.success("✅ Scraping complete!")

            if screenshot_paths:
                st.subheader("Generated Screenshots")
                # Display images in a grid layout
                cols = st.columns(3)
                for i, path_str in enumerate(screenshot_paths):
                    path = Path(path_str)
                    if path.exists():
                        with cols[i % 3]:
                            st.image(str(path), caption=path.name, use_container_width=True)
                            with open(path, "rb") as file:
                                st.download_button(
                                    label=f"Download {path.name}",
                                    data=file,
                                    file_name=path.name,
                                    mime="image/png"
                                )
                    else:
                        st.warning(f"File not found: {path.name}")
            else:
                st.warning("No screenshots were generated. Check the logs for more details.")

        except Exception as e:
            status_placeholder.empty()
            st.error(f"A critical error occurred during scraping:")
            st.exception(e)