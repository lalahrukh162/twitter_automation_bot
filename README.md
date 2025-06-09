# twitter_automation_bot
Python-based Twitter automation tool that manages multiple accounts via cookies and scrapes tweets with view counts. Supports automated login, multi-account handling, and saves high-view tweets to CSV. Built with Selenium, cookies, and browser session verification.

## 🐦 Twitter Multi-Account Automation Bot with View-Based Tweet Scraper

This Python-based automation tool allows you to manage multiple Twitter accounts using cookie-based login and scrape tweets based on their view count. It is designed for users who want to track viral or high-engagement tweets efficiently across multiple accounts.

### ✨ Features

* 🔐 **Cookie-Based Login**
  Automatically saves and reuses cookies to avoid repeated manual login and bypass bot detection mechanisms.

* 👥 **Multi-Account Management**
  Handles login and tweet scraping for multiple Twitter accounts from a single CSV input.

* 📊 **Tweet View Count Scraper**
  Scrapes tweets from the home timeline that meet a minimum view threshold (e.g., 1000+ views), and exports them to a CSV file.

* 💻 **Session Verification**
  Checks if login was successful using multiple UI element verifications (tweet box, profile link, etc.)

* 🪟 **Multiple Browser Sessions**
  Opens multiple Chrome sessions with distinct windows for each account to simulate human activity.

* 🧠 **View Count Parsing**
  Parses views displayed as raw numbers or shorthand formats like "1.2K", "3.5M", etc.

* 📁 **CSV Export**
  All scraped tweets are stored in a structured CSV file with columns for username, view count, and tweet text.


### 🛠 Tech Stack

* Python 3
* Selenium WebDriver
* ChromeDriver (undetected)
* CSV, Pickle
* Subprocess for external cookie-saving script

---

### 📂 Input Format

Requires a CSV file (`accounts.csv`) with the following format:

username,password
your_username1,your_password1
your_username2,your_password2

### ⚠️ Disclaimer

This tool is intended for **educational and research purposes only**. Use responsibly and ensure compliance with Twitter’s Terms of Service and privacy policies.

