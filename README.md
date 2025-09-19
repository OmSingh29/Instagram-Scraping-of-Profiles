## 📸 Instagram Profile & Activity Scraper

This project is a **Streamlit web app** that automates the process of scraping profile and activity data from Instagram using **Selenium + undetected-chromedriver**.  

It logs into Instagram (via cookies or credentials), navigates through the profile, followers, following, recent posts, and "Your Activity" sections, and captures screenshots for analysis.  

---

## 🚀 Features
- **Streamlit Web UI** – Easy-to-use interface for entering Instagram credentials.  
- **Cookie Persistence** – Avoids repeated logins by saving & reusing session cookies.  
- **Profile Data Scraping** – Captures profile ID, stats (posts, followers, following).  
- **Screenshots** – Saves screenshots of profile page, followers, following, posts, and activity pages.  
- **Activity History** – Captures likes, comments, story replies, reviews, and account history.  
- **Download Support** – View & download screenshots directly from the Streamlit app.  
- **One-click Cookie Reset** – Delete cookies easily if login fails.  

---

## 📂 Project Structure
```
instagram-scraping-of-profiles/
│── app.py              # Streamlit app entry point
│── scraping.py         # Core scraper logic (Selenium + undetected-chromedriver)
│── requirements.txt    # Dependencies
│── README.md           # Documentation
│── instagram_cookies.pkl   # (Generated) Saved cookies for login persistence
│── instagram_screenshots/  # (Generated) Screenshots saved here
│── instagram_data.json     # (Generated) Profile & posts metadata
```

---

## ⚙️ Installation

### 1. Clone the repository
```
git clone https://github.com/your-username/instagram-scraping-of-profiles.git
```
```
cd instagram-scraping-of-profiles
```

### 2. Create Virtual Environment (Recommended)
```
conda create -n scraping python=3.11
```
```
conda activate scraping
```

Or

```
py -3.11 -m venv scraping
```
```
scraping\Scripts\activate
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Run the Streamlit app
```
streamlit run app.py
```

---

## 🛠️ Requirements
- Python 3.11+  
- Google Chrome or Chromium (installed on your system version 140+) 
- ChromeDriver (handled automatically by **undetected-chromedriver**)  

---

## 🔑 Usage
1. Run the app with `streamlit run app.py`.  
2. Enter your **Instagram username & password**.  
3. The scraper will:
   - Use cookies if available (faster login).  
   - Otherwise, log in with credentials and save cookies.  
4. Screenshots and scraped data will be saved locally:
   - `instagram_screenshots/` – Screenshots of profile, followers, posts, etc.  
   - `instagram_data.json` – Extracted metadata (posts, followers, following).  
5. View and download screenshots directly in the Streamlit UI.  

---

---

## ❓ Troubleshooting
- **Blocked Login / Challenge Required**  
  Instagram may detect automated logins. Try deleting cookies (via the "Delete Cookies" button) and logging in again.  

---

## ⚠️ Disclaimer
This project is for **educational purposes only**. 
Scraping Instagram or automating logins may violate Instagram’s [Terms of Service](https://help.instagram.com/581066165581870).  
Use responsibly and at your own risk.  

---

## 📜 License
MIT License © 2025
