from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from time import sleep
import pickle
import json
#status_callback("")


def scrape_instagram(username: str, password: str, status_callback=print):
    screenshot_files = []
    scraped_data = {}

    platform = 'instagram'
    url = f'https://www.{platform}.com/'
    cookie_file = Path(f"{platform}_cookies.pkl")

    login_url = 'accounts/login/'
    username_field = 'username'
    password_field = 'password'
    login_button_xpath = '//*[@id="loginForm"]/div/div[3]'

    profile_link_xpath = "//span[text()='Profile']/ancestor::a"
    post_elements_xpath = "//main//div/div/a"

    screenshots_dir = Path(f"{platform}_screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1280,1024")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    status_callback("Initialising browser")
    
    #driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome(service=Service(executable_path="/usr/bin/chromedriver"), options=options)

    status_callback("Browser initialised")

    try:
        # --- Login Logic ---
        if cookie_file.exists():
            status_callback("Cookie file exists")
            driver.get(url)
            for cookie in pickle.load(open(cookie_file, "rb")):
                driver.add_cookie(cookie)
            driver.refresh()
            status_callback("✅ Logged in using saved cookies")
        else:
            status_callback("No cookies found")
            driver.get(url + login_url)
            status_callback("URL is opened")
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, username_field))).send_keys(username)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, password_field))).send_keys(password)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, login_button_xpath))).click()
            except Exception as e:
                status_callback("Error occurred: {e}")
            status_callback("Waiting for login to complete...")
            sleep(6)
            pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))
            status_callback("✅ Logged in and cookies saved")

        status_callback("Handle pop-ups")

        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Not Now']"))).click()
        except TimeoutException:
            pass

        # ## Step 1: Navigate to Profile ##
        status_callback("🔎 Navigating to profile page...")
        profile_link = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, profile_link_xpath)))
        profile_link.click()
        sleep(2)
        profile_id = driver.current_url.split('/')[-2]
        scraped_data['profile_id'] = profile_id
        status_callback(f"✅ Profile: {profile_id}")

        # ## Step 2: Scrape Stats ##
        posts_count = followers_count = following_count = "N/A"
        try:
            wait = WebDriverWait(driver, 15)
            header_xpath = "//header//ul"
            wait.until(EC.presence_of_element_located((By.XPATH, header_xpath)))
            stats_list = driver.find_elements(By.XPATH, f"{header_xpath}/li")
            if len(stats_list) >= 3:
                posts_count = stats_list[0].text.split(' ')[0]
                followers_count = stats_list[1].text.split(' ')[0]
                following_count = stats_list[2].text.split(' ')[0]
        except Exception as e:
            status_callback(f"⚠️ Could not fetch profile stats: {e}")
        scraped_data.update({'posts': posts_count, 'followers': followers_count, 'following': following_count})
        status_callback(f"✅ Stats -> Posts: {posts_count}, Followers: {followers_count}, Following: {following_count}")

        # Profile Picture
        try:
            profile_pic_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//main//header//img")))
            profile_pic_ss = screenshots_dir / "profile_picture.png"
            profile_pic_element.screenshot(str(profile_pic_ss))
            screenshot_files.append(profile_pic_ss)
            status_callback("Profile picture captured")
        except Exception:
            pass

        # Followers & Following
        try:
            followers_link_xpath = "//a[contains(@href, '/followers/')]"
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, followers_link_xpath))).click()
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//a[@role='link']")))
            sleep(1)
            followers_modal = driver.find_element(By.XPATH, "//div[@role='dialog']")
            followers_ss = screenshots_dir / "followers_page_1.png"
            followers_modal.screenshot(str(followers_ss))
            screenshot_files.append(followers_ss)
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
            status_callback("Succesfully fetched followers")

            following_link_xpath = "//a[contains(@href, '/following/')]"
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, following_link_xpath))).click()
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//a[@role='link']")))
            sleep(1)
            following_modal = driver.find_element(By.XPATH, "//div[@role='dialog']")
            following_ss = screenshots_dir / "following_page_1.png"
            following_modal.screenshot(str(following_ss))
            screenshot_files.append(following_ss)
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            status_callback("Succesfully fetched following")
        except Exception as e:
            status_callback(f"⚠️ Could not take followers/following screenshots: {e}")

        # ## Step 3: Posts ##
        try:
            post_elements = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, post_elements_xpath)))
            num_posts_to_capture = min(5, int(posts_count)) if posts_count.isdigit() else 0
            scraped_data['recent_posts_data'] = []
            for i in range(num_posts_to_capture):
                try:
                    current_posts = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, post_elements_xpath)))
                    post = current_posts[i+6]
                    post_id = f"post_{i+1}"
                    # try:
                    #     post_id = post.get_attribute('href').split('/')[-2]
                    # except Exception:
                    #     pass
                    screenshot_filename = screenshots_dir / f"{post_id}.png"
                    post.screenshot(str(screenshot_filename))
                    screenshot_files.append(screenshot_filename)
                    scraped_data['recent_posts_data'].append({'post_id': post_id, 'screenshot_path': str(screenshot_filename)})
                except StaleElementReferenceException:
                    continue
            status_callback("Succesfully fetched posts")
        except Exception:
            pass

        # ## Step 4: Your Activity ##
        activity_screenshots_dir = Path("your_activity_scroll_screenshots")
        activity_screenshots_dir.mkdir(exist_ok=True)
        driver.get(url + "your_activity/")
        your_activity_header_xpath = "//*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'your activity']"
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, your_activity_header_xpath)))

        pages_to_process = ["Likes", "Comments", "Story Replies", "Reviews"]
        for page in pages_to_process:
            try:
                page_link_xpath = f"//span[translate(text(), '{page.upper()}', '{page.lower()}') = '{page.lower()}']"
                WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, page_link_xpath))).click()
                page_header_xpath = f"//*[translate(text(), '{page.upper()}', '{page.lower()}') = '{page.lower()}']"
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, page_header_xpath)))
                spinner_xpath = "//*[name()='svg' and @aria-label='Loading...']"
                WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.XPATH, spinner_xpath)))
                sleep(1)
                for i in range(3):
                    screenshot_path = activity_screenshots_dir / f"{page.lower().replace(' ', '_')}_page_{i+1}.png"
                    driver.save_screenshot(str(screenshot_path))
                    screenshot_files.append(screenshot_path)
                    if i == 2:
                        break
                    last_height = driver.execute_script("return document.body.scrollHeight")
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    try:
                        WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.body.scrollHeight") > last_height)
                    except TimeoutException:
                        break
                driver.back()
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, your_activity_header_xpath)))
                status_callback(f"Succesfully fetched {page}")
            except TimeoutException:
                driver.get(url + "your_activity/")
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, your_activity_header_xpath)))

        # Account History
        try:
            history_link_xpath = "//span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'account history']"
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, history_link_xpath))).click()
            history_header_xpath = "//*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'account history']"
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, history_header_xpath)))
            spinner_xpath = "//*[name()='svg' and @aria-label='Loading...']"
            WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.XPATH, spinner_xpath)))
            sleep(1)
            screenshot_path = activity_screenshots_dir / "account_history.png"
            driver.save_screenshot(str(screenshot_path))
            screenshot_files.append(screenshot_path)
            status_callback("Succesfully fetched account history")
        except Exception:
            pass

    except Exception as e:
        status_callback(f"❌ An error occurred: {e}")
        sleep(5)
    finally:
        output_file = Path(f"{platform}_data.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        status_callback(f"💾 Data saved to {output_file}")
        driver.quit()


    return screenshot_files
