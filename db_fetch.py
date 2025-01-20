import logging
from pymongo import MongoClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB configuration
mongo_client = MongoClient("mongodb://localhost:27017/") 
db = mongo_client["liveuamap"]
collection = db["ethiopia"]

def fetch_all_data_from_mongo():
    try:
        # Retrieve all documents from the collection
        documents = collection.find() 
        if documents:
            logger.info(f"Found {documents.count()} documents.")
            for document in documents:
                logger.info(f"Document ID: {document['_id']}, Scrape Time: {document['scrape_time']}")
                
                # Access the events array
                events = document.get("events", [])
                
                if events:
                    logger.info(f"Found {len(events)} events in document.")
                    for i, event in enumerate(events, 1):
                        # Display each event's details
                        logger.info(f"Event {i}:")
                        logger.info(f"  Date: {event['date']}")
                        logger.info(f"  Source: {event['source_url']}")
                        logger.info(f"  Data: {event['data']}")
                        logger.info(f"  Image Source: {event['img_src']}")
                else:
                    logger.warning("No events found in this document.")
        else:
            logger.warning("No documents found in the collection.")
    except Exception as e:
        logger.error(f"Error fetching data from MongoDB: {e}")

def main():
    fetch_all_data_from_mongo()

if __name__ == "__main__":
    main()
