import time
import pymysql
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException

CHROMEDRIVER_PATH = r"D:\\Project\\Redbus scraping\\drivers\\chromedriver.exe"


SCROLL_PAUSE_SEC = 2

# MySQL connection
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Redbus@2025',
    database='redbus_data'
)
cursor = connection.cursor()
def fetch_route_links():
    cursor.execute("SELECT route_link FROM bus_routes")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def scroll_to_load_all_buses(driver, label="Private", end_of_list_class=None):
    prev_count = 0
    same_count_repeat = 0
    max_same_repeat = 3
    start_time = time.time()

    while True:
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(SCROLL_PAUSE_SEC + 1)

        if end_of_list_class:
            try:
                end_elem = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, end_of_list_class))
                )
                if "End of list" in end_elem.text:
                    print(f"✅ Detected end of {label.lower()} bus list on page.")
                    break
            except TimeoutException:
                pass

        bus_cards = driver.find_elements(By.XPATH, "//li[contains(@class, 'tupleWrapper')]")
        current_count = len(bus_cards)
        print(f"↪ Scroll ({label}): Found {current_count} buses.")

        if current_count == prev_count:
            same_count_repeat += 1
            if same_count_repeat >= max_same_repeat:
                print(f"✅ Reached end of {label.lower()} bus list by stable count.")
                break
        else:
            same_count_repeat = 0
            prev_count = current_count

        if time.time() - start_time > 60:
            print(f"⏱ Timeout reached for {label.lower()} bus scroll.")
            break

def scroll_to_top(driver):
    print("🔼 Scrolling to top...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def extract_bus_data(bus, route_url):
    def safe_text(by, selector):
        try:
            return bus.find_element(by, selector).text.strip()
        except NoSuchElementException:
            return "N/A"

    busname = safe_text(By.CLASS_NAME, "travelsName___495898")
    bustype = safe_text(By.CLASS_NAME, "busType___13ff4b")
    departing_time = safe_text(By.CLASS_NAME, "boardingTime___aced27")
    reaching_time = safe_text(By.CLASS_NAME, "droppingTime___616c2f")
    duration = safe_text(By.CLASS_NAME, "duration___5b44b1")
    star_rating = safe_text(By.CLASS_NAME, "rating___7724f1")
    price = safe_text(By.CLASS_NAME, "finalFare___898bb7").replace("₹", "").replace(",", "").strip()
    seats = safe_text(By.CLASS_NAME, "totalSeats___ba48cf").split()[0]

    # Debug print
    #print(f"📝 Bus: {busname} | Type: {bustype} | Time: {departing_time}-{reaching_time} | ₹{price or 'N/A'} | Rating: {star_rating} | Seats: {seats}")

    try:
        cursor.execute('''
            INSERT IGNORE INTO bus_details (
                route_link, busname, bustype, departing_time,
                duration, reaching_time, star_rating, price, seats_available, scraped_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            route_url,
            busname,
            bustype,
            departing_time if departing_time != "N/A" else None,
            duration if duration != "N/A" else None,
            reaching_time if reaching_time != "N/A" else None,
            float(star_rating) if star_rating.replace('.', '', 1).isdigit() else None,
            float(price) if price.replace('.', '', 1).isdigit() else None,
            int(seats) if seats.isdigit() else None,
            datetime.today().date()
        ))
        connection.commit()
    except Exception as e:
        print(f"❌ DB Insert Error: {e}")


def scrape_buses(driver, route_url):
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'tupleWrapper')]"))
    )
    bus_cards = driver.find_elements(By.XPATH, "//li[contains(@class, 'tupleWrapper')]")
    print(f"🚌 Found {len(bus_cards)} buses on: {route_url}")
    for bus in bus_cards:
        extract_bus_data(bus, route_url)

def click_show_buses(driver):
    try:
        print("🔍 Looking for government 'Show Buses' card...")
        card = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rtcTuple___f04ba3"))
        )
        button = card.find_element(By.CLASS_NAME, "primaryButton___93b44e")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)

        WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "primaryButton___93b44e"))
        )
        try:
            button.click()
        except ElementClickInterceptedException:
            print("⚠️ Button click intercepted — using JS click.")
            driver.execute_script("arguments[0].click();", button)

        time.sleep(4)
        print("✅ Clicked 'Show Buses' successfully.")
        return True
    except Exception as e:
        print(f"❌ Could not find/click government 'Show Buses': {e}")
        return False

def main():
    print("📅 Starting Redbus scraper for:", datetime.today().date())
    route_links = fetch_route_links()
    print(f"🔗 Total routes to process: {len(route_links)}")

    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    for idx, route_url in enumerate(route_links, start=1):
        print(f"\n📍 [{idx}/{len(route_links)}] Scraping route: {route_url}")
        try:
            driver.get(route_url)
            print(f"➡️ Opening route: {route_url}")
            time.sleep(6)

            print("🔽 Scrolling to load private buses...")
            scroll_to_load_all_buses(driver, label="Private", end_of_list_class="endText__ind-search-styles-module-scss-a5VZc")
            scrape_buses(driver, route_url)

            scroll_to_top(driver)

            if click_show_buses(driver):
                print("🔽 Scrolling to load government buses...")
                scroll_to_load_all_buses(driver, label="Government", end_of_list_class="endText__ind-search-groupExpanded-module-scss-B4EeT")
                scrape_buses(driver, route_url)

        except Exception as e:
            print(f"⚠️ Error scraping {route_url}: {e}")

    driver.quit()
    connection.close()
    print("\n✅ Scraping completed.")

if __name__ == "__main__":
    main()
