# LiveUAMap Web Scraper

This project is a web scraper for extracting data from LiveUAMap (liveuamap.com) based on country-specific subdomains. The scraper retrieves event data, including date, source, title, and images, and stores it in a MongoDB database for later analysis or reporting.

## 🚀 Features

- **Dynamic URL generation** from a `countries.txt` list  
- **Robust Selenium setup** with GeckoDriver auto‑installation or custom path  
- **Resilient clicking logic** with retry on intercepted clicks  
- **Structured data extraction**: date, source URL, title, image, location  
- **MongoDB storage** with upsert logic to avoid duplicates  
- **Detailed logging** for easy troubleshooting  

## Prerequisites
1. **Python 3.8+** installed on your system.
2. **GeckoDriver** (or install using `webdriver_manager`).
3. **MongoDB** installed and running locally (or a connection string to a remote MongoDB instance).
4. **Firefox Browser** installed.
5. Required Python packages:
   - selenium
   - pymongo
   - webdriver_manager

## Project Structure
- **main.py**: Contains the main logic for scraping and storing data.
- **countries.txt**: A text file listing the countries to scrape (one country per line).
- **README.md**: Documentation file (this file).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/liveuamap-scraper.git
   cd liveuamap-scraper
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

3. Ensure MongoDB is running locally or modify the connection string in the script to connect to your MongoDB instance.

4. Create a `countries.txt` file in the working directory and list the countries you want to scrape (one per line).

## Configuration
### MongoDB
The MongoDB connection is configured in the script using:
```python
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["liveuamap"]
```
You can modify the connection string or database name if needed.

### Geckodriver Path
Specify the path to `geckodriver` in the script:
```python
geckodriver_path = 'path'
```
Alternatively, the script can automatically download and use GeckoDriver via `webdriver_manager` if the specified path is unavailable.

## Usage

1. Run the scraper:
   ```bash
   python scraper.py
   ```

2. The script will:
   - Read country names from `countries.txt`.
   - Visit each country's LiveUAMap subdomain.
   - Scrape event data and store it in a MongoDB collection named after the country.

3. Check your MongoDB database to view the scraped data.

## Notes
- The script can run into issues with dynamic content loading or missing elements; ensure the CSS selectors used for locating elements are correct.
- If a country-specific subdomain does not exist, the script logs an error but continues with the next query.
- Add error handling for network or timeout issues if required.



Happy scraping!

