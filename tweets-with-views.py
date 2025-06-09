import subprocess
import re
import csv
import os
import time
import pickle
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def save_cookies_for_accounts(csv_file):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            username = row['username']
            password = row['password']
            cookies_file = f"twitter_{username}_cookies.pkl"

            if os.path.exists(cookies_file):
                try:
                    cookies = pickle.load(open(cookies_file, "rb"))
                    if cookies and len(cookies) > 3:
                        print(f"Valid cookies already exist for {username}")
                        continue
                except:
                    pass

            print(f"\nSaving cookies for {username}...")
            try:
                result = subprocess.run(
                    ['python', 'save_cookies.py', username, password],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    if os.path.exists(cookies_file):
                        print(f"Successfully saved cookies for {username}")
                    else:
                        print(f"Cookie file not created for {username}")
                else:
                    print(f"Failed to save cookies for {username}:")
                    print(result.stderr)
            except subprocess.TimeoutExpired:
                print(f"Timeout expired for {username}")
            except Exception as e:
                print(f"Unexpected error for {username}: {str(e)}")

def login_with_cookies(account_name):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://twitter.com")
        time.sleep(2)

        cookies_file = f"twitter_{account_name}_cookies.pkl"
        if not os.path.exists(cookies_file):
            print(f"\nNo cookies found for {account_name}")
            return None

        try:
            cookies = pickle.load(open(cookies_file, "rb"))
            if not cookies:
                raise ValueError("Empty cookies file")
        except Exception as e:
            print(f"Invalid cookies for {account_name}: {str(e)}")
            return None

        for cookie in cookies:
            try:
                if 'sameSite' in cookie:
                    cookie['sameSite'] = 'None'
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Warning: Couldn't add cookie for {account_name}: {str(e)}")

        driver.get("https://twitter.com/home")
        time.sleep(3)

        verification_success = False
        verification_selectors = [
            ('//div[@data-testid="tweet"]', "Tweet element"),
            ('//div[@aria-label="Home timeline"]', "Home timeline"),
            ('//a[@aria-label="Profile"]', "Profile link"),
            ('//span[contains(text(), "Home")]', "Home text")
        ]

        for selector, description in verification_selectors:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print(f"Verified login via {description}")
                verification_success = True
                break
            except:
                continue

        if verification_success:
            print(f"\nSuccessfully logged in to {account_name}")
            return driver
        else:
            print(f"\nLogin verification failed for {account_name}")
            driver.save_screenshot(f"login_failed_{account_name}.png")
            return None

    except Exception as e:
        print(f"\nError logging in {account_name}: {str(e)}")
        if driver:
            driver.save_screenshot(f"error_{account_name}.png")
        return None

def extract_like_count(tweet):
    spans = tweet.find_elements(By.XPATH, './/div[@data-testid="like"]//span')
    for span in spans[::-1]:  # Check last span first (most likely to have number)
        try:
            text = span.text.strip()
            if text:
                if 'K' in text:
                    return int(float(text.replace('K', '')) * 1000)
                elif 'M' in text:
                    return int(float(text.replace('M', '')) * 1000000)
                else:
                    return int(text.replace(',', ''))
        except:
            continue
    return 0

def extract_view_count(tweet):
    spans = tweet.find_elements(By.TAG_NAME, "span")

    min_views = 1000
    for span in spans:
        text = span.text.strip()
        if re.match(r'^\d+(\.\d+)?[KkMm]?$|^\d+$', text):  # Matches 1.2K, 500, 3.4M
            # Convert to number
            multiplier = 1
            if 'K' in text or 'k' in text:
                multiplier = 1000
            elif 'M' in text or 'm' in text:
                multiplier = 1000000
            try:
                num = float(text.replace('K', '').replace('k', '').replace('M', '').replace('m', '')) * multiplier
                return int(num)
            except:
                continue
    return 0



def scrape_tweets_with_views(driver, username, min_views=1000, max_scrolls=15, output_file="viewed_tweets.csv"):
    print(f"\nScraping tweets for {username} (min {min_views} views)...")

    driver.get("https://twitter.com/home")
    time.sleep(3)

    tweets_data = set()
    scroll_pause = 3

    for scroll in range(max_scrolls):
        print(f"Scroll {scroll+1} of {max_scrolls}")
        time.sleep(scroll_pause)

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"Found {len(tweets)} tweets on scroll {scroll+1}")

        for tweet in tweets:
            try:
                view_count = extract_view_count(tweet)

                if view_count >= min_views:
                    tweet_text_elem = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                    tweet_text = tweet_text_elem.text.strip()
                    tweet_data = (username, int(view_count), tweet_text)

                    if tweet_data not in tweets_data:
                        print(f"✅ Found tweet with {int(view_count)} views: {tweet_text[:50]}...")
                        tweets_data.add(tweet_data)

            except Exception as e:
                continue

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Save to CSV
    if tweets_data:
        with open(output_file, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            if os.stat(output_file).st_size == 0:
                writer.writerow(["username", "view_count", "tweet_text"])
            for row in tweets_data:
                writer.writerow(row)

        print(f"✅ Saved {len(tweets_data)} tweets to {output_file}")
    else:
        print("❌ No tweets found with the required views.")

def manage_multiple_accounts(csv_file):
    print("\nStarting Twitter Account Manager...")
    print(f"Using accounts from: {csv_file}")

    save_cookies_for_accounts(csv_file)

    drivers = []
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            username = row['username']
            print(f"\nProcessing account: {username}")

            driver = login_with_cookies(username)
            if driver:
                drivers.append((username, driver))

                if len(drivers) > 1:
                    driver.set_window_position(
                        (len(drivers)-1) * 400 % 1600,
                        ((len(drivers)-1) * 400 // 1600) * 400
                    )

    return drivers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Twitter Account Cookie Manager and Tweet Scraper')
    parser.add_argument('--csv', type=str, default='accounts.csv',
                        help='Path to CSV file containing account credentials')
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"\nError: CSV file not found at {args.csv}")
        print("Please create a CSV file with 'username,password' format")
        exit(1)

    active_drivers = manage_multiple_accounts(args.csv)

    if active_drivers:
        print("\n\nActive Twitter Sessions:")
        for idx, (username, driver) in enumerate(active_drivers, 1):
            print(f"{idx}. {username}")
            scrape_tweets_with_views(driver, username, min_views=1000)

        print("\nKeep these browser windows open for interaction...")
        input("Press Enter when you want to close ALL sessions...")

        print("\nClosing all browser sessions...")
        for _, driver in active_drivers:
            try:
                driver.quit()
            except:
                pass
        print("All sessions closed.")
    else:
        print("\nNo active sessions were established.")
        print("Possible issues:")
        print("- Invalid or expired cookies")
        print("- Twitter login requirements changed")
        print("- Account requires additional verification")
        print("Check the error screenshots for more details.")
