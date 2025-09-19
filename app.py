# app.py

import streamlit as st
from pathlib import Path
from scraping import scrape_instagram,cookie_file
import shutil

# --- Page Configuration ---
st.set_page_config(
    page_title="Instagram Scraper",
    page_icon="📸",
    layout="wide"
)

# --- App UI ---
st.title("📸 Instagram Profile & Activity Scraper")
st.info("Enter your Instagram credentials to generate screenshots of profile and activity of the account you want. The process may take several seconds.")

# --- User Input Form ---
with st.form("credentials_form"):
    st.subheader("Enter Your Instagram Credentials")
    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Start Scraping")

if st.button("Delete Cookies"):
    if cookie_file.exists():
        cookie_file.unlink()
        st.success("Cookies file deleted ✅")
    else:
        st.warning("No cookies file found.")

# --- Scraper Execution ---
if submitted:
    if not username or not password:
        st.error("Please provide both a username and a password.")
    else:
        # Create a unique directory for the user's screenshots
        output_dir = Path(username)
        output_dir.mkdir(exist_ok=True)

        status_placeholder = st.empty()

        def update_status(message):
            """This function is passed to the scraper to update the UI in real-time."""
            status_placeholder.info(f"⏳ {message}")

        try:
            with st.spinner("Scraping in progress... This may take several minutes."):
                # ❗️ IMPORTANT: Pass the new 'output_dir' to your scraper function
                screenshot_paths = scrape_instagram(username, password, status_callback=update_status, output_dir=output_dir)
            
            status_placeholder.empty()
            st.success("✅ Scraping complete!")

            if screenshot_paths:
                # --- Section 1: Display Screenshots in the App ---
                st.subheader("🖼️ Generated Screenshots Preview")
                cols = st.columns(3)  # Use 3 columns for the grid
                for i, path_str in enumerate(screenshot_paths):
                    path = Path(path_str)
                    if path.exists():
                        with cols[i % 3]:  # Cycle through columns
                            st.image(str(path), caption=path.name, use_container_width=True)
                
                st.markdown("---") # Add a visual separator

                # --- Section 2: Zip and Download ---
                st.subheader("📥 Download All Screenshots")
                
                # Create a zip file from the user's screenshot directory
                zip_path_str = f"{username}_instagram_screenshots"
                shutil.make_archive(zip_path_str, 'zip', output_dir)
                zip_file_path = Path(f"{zip_path_str}.zip")

                st.info(f"All screenshots have also been bundled into a single zip file for you.")

                # Provide the zip file for download
                with open(zip_file_path, "rb") as fp:
                    st.download_button(
                        label=f"Download {zip_file_path.name}",
                        data=fp,
                        file_name=zip_file_path.name,
                        mime="application/zip"
                    )
            else:
                st.warning("No screenshots were generated. The process finished, but no files were created.")

        except Exception as e:
            status_placeholder.empty()
            st.error(f"A critical error occurred during scraping:")
            st.exception(e)