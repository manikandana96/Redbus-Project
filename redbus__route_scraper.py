import time
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- MySQL config ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Redbus@2025',
    'database': 'redbus_data'
}

# --- Chromedriver path ---
CHROMEDRIVER_PATH = r"D:\Project\Redbus scraping\drivers\chromedriver.exe"

# --- State sources ---
state_names = [
    "Kerala", "Andhra Pradesh", "Telangana", "Goa", "Rajasthan",
    "South Bengal", "Himachal Pradesh", "Assam", "Uttar Pradesh", "West Bengal"
]

state_links = [
    "https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/astc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/wbtc-ctc/?utm_source=rtchometile"
]

# --- MySQL Table Setup ---
def init_mysql():
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bus_routes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                state VARCHAR(100),
                route_name TEXT,
                route_link VARCHAR(500) UNIQUE
            )
        """)
    conn.commit()
    conn.close()


# --- Browser Setup ---
def init_driver():
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=service, options=options)

# --- Scrape a single state page ---
def scrape_routes_for_state(driver, state_name, state_url):
    print(f"\n🔎 Scraping routes for {state_name}")
    driver.get(state_url)
    time.sleep(4)

    route_data = set()
    visited_pages = set()

    while True:
        try:
            # Wait for routes to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "route"))
            )

            # Scrape routes on the current page
            route_elements = driver.find_elements(By.CLASS_NAME, "route")
            for elem in route_elements:
                name = elem.text.strip()
                link = elem.get_attribute("href")
                if name and link:
                    route_data.add((state_name, name, link))

            # Get all page number tabs
            page_tabs = driver.find_elements(By.CSS_SELECTOR, "div.DC_117_pageTabs")
            next_page_clicked = False

            for tab in page_tabs:
                page_num = tab.text.strip()
                if page_num and page_num not in visited_pages:
                    visited_pages.add(page_num)
                    driver.execute_script("arguments[0].scrollIntoView();", tab)
                    time.sleep(1)
                    tab.click()
                    time.sleep(3)  # Allow time for new routes to load
                    next_page_clicked = True
                    break  # Go back and scrape new page

            if not next_page_clicked:
                break  # No more new pages to click

        except TimeoutException:
            print("❌ Timeout while loading routes.")
            break
        except Exception as e:
            print(f"❌ Pagination error: {e}")
            break

    print(f"✅ Total {len(route_data)} routes found for {state_name}")
    return list(route_data)


# --- Insert into MySQL ---
def save_routes_to_mysql(route_list):
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cursor:
        for route in route_list:
            try:
                cursor.execute("""
                    INSERT IGNORE INTO bus_routes (state, route_name, route_link)
                    VALUES (%s, %s, %s)
                """, route)
            except Exception as e:
                print(f"❌ DB Insert Error: {e}")
        conn.commit()
    conn.close()


# --- MAIN ---
def main():
    init_mysql()
    driver = init_driver()
    all_routes = []

    for state_name, state_url in zip(state_names, state_links):
        routes = scrape_routes_for_state(driver, state_name, state_url)
        all_routes.extend(routes)

    driver.quit()

    if all_routes:
        save_routes_to_mysql(all_routes)
        print(f"\n✅ Total {len(all_routes)} routes saved to MySQL.")
    else:
        print("⚠️ No route links collected.")

if __name__ == "__main__":
    main()
