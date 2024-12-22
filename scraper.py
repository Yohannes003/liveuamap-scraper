import os
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.firefox import GeckoDriverManager
from pymongo import MongoClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

geckodriver_path = '/home/yohannes/Documents/python/geckodriver'

# MongoDB configuration
mongo_client = MongoClient("mongodb://localhost:27017/")  
db = mongo_client["liveuamap"]

def setup_firefox_service():
    try:
        if os.path.exists(geckodriver_path):
            return FirefoxService(geckodriver_path)
        else:
            return GeckoDriverManager().install()
    except WebDriverException as e:
        logger.error("Error setting up Firefox service: %s", e)
        raise

def initialize_driver():
    try:
        firefox_service = setup_firefox_service()
        firefox_options = webdriver.FirefoxOptions()
        # firefox_options.add_argument('--headless')  # Uncomment for headless mode
        firefox_options.add_argument('--disable-notifications')
        driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
        logger.info("Firefox driver initialized successfully.")
        return driver
    except WebDriverException as e:
        logger.error("Driver initialization failed: %s", e)
        raise

def store_data_in_mongo(event_data_list, collection_name):
    try:
        # Create a unique identifier (e.g., using source_url or any other unique field)
        scrape_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get the collection based on the dynamic collection_name
        collection = db[collection_name]
        
        # Check if the document already exists (based on a field like scrape_time or source_url)
        existing_document = collection.find_one({"scrape_time": scrape_time})
        
        if existing_document:
            # If the document already exists, append the new events to the existing array
            collection.update_one(
                {"scrape_time": scrape_time},
                {"$push": {"events": {"$each": event_data_list}}}
            )
            logger.info(f"Updated existing document with scrape time {scrape_time}.")
        else:
            # If it's a new document, insert it with an array of events
            collection.insert_one({
                "scrape_time": scrape_time,
                "events": event_data_list
            })
            logger.info(f"Inserted new document with scrape time {scrape_time}.")
    except Exception as e:
        logger.error(f"Error storing data in MongoDB: {e}")

def get_queries_from_file(file_name="countries.txt"):
    try:
        with open(file_name, "r") as file:
            queries = [line.strip() for line in file if line.strip()]
        logger.info(f"Loaded {len(queries)} queries from {file_name}.")
        return queries
    except FileNotFoundError:
        logger.error(f"File {file_name} not found in the working directory.")
        return []

def visit_liveumap(query):
    url = f"https://{query}.liveuamap.com/"
    logger.info(f"Visiting {url}")
    driver = None  # Initialize driver variable

    try:
        # Initialize WebDriver for each query
        driver = initialize_driver()

        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("Page loaded successfully.")
        
        # Wait for the div with class 'scroller' to be present
        scroller_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scroller"))
        )
        logger.info("Found the div with class 'scroller'.")
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        event_data_list = []  # List to store the scraped event data
        
        while True:
            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the page to load new content

            # Find all divs whose class starts with 'event cat'
            event_cat_divs = driver.find_elements(By.CSS_SELECTOR, "div[class^='event cat']")
            logger.info(f"Found {len(event_cat_divs)} divs with class starting with 'event cat'.")
            
            # Iterate through the found divs and extract the required data
            for i, event_div in enumerate(event_cat_divs, 1):
                logger.info(f"Extracting data from Event {i} div.")
                
                # Extract date
                try:
                    date = event_div.find_element(By.CSS_SELECTOR, "span.date_add").text
                except NoSuchElementException:
                    date = "Date not found"
                
                # Extract source
                try:
                    source_url = event_div.find_element(By.CSS_SELECTOR, "a.source-link").get_attribute("href")
                except NoSuchElementException:
                    source_url = "Source not found"
                
                # Extract data (title)
                try:
                    data = event_div.find_element(By.CSS_SELECTOR, "div.title").text
                except NoSuchElementException:
                    data = "Data not found"
                
                # Extract image source if present
                try:
                    img_src = event_div.find_element(By.CSS_SELECTOR, "label img").get_attribute("src")
                except NoSuchElementException:
                    img_src = "Image not found"
                
                event_data = {
                    "date": date,
                    "source_url": source_url,
                    "data": data,
                    "img_src": img_src
                }
                
                # Append the event data to the list
                event_data_list.append(event_data)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  
                logger.info("Reached the bottom of the page.")
                break
            last_height = new_height 

        # Store the scraped data in MongoDB (collection named after query)
        store_data_in_mongo(event_data_list, query.lower())

    except Exception as e:
        logger.error(f"Error while scraping {url}: {e}")
        # You can handle specific errors for better diagnostics, e.g., connection issues, page errors, etc.
    finally:
        if driver:
            driver.quit()  # Close the driver for each query
            logger.info("Driver closed.")

def main():
    try:
        queries = get_queries_from_file()
        for query in queries:
            visit_liveumap(query)  # No need to pass driver anymore, it's handled in visit_liveumap
    except Exception as e:
        logger.error(f"Scraper encountered an error: {e}")

if __name__ == "__main__":
    main()
