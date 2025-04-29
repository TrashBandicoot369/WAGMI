from firebase_admin_setup import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_collection(collection_name):
    """Delete all documents in a collection"""
    try:
        # Get all documents in the collection
        docs = db.collection(collection_name).get()
        deleted = 0
        
        # Delete each document
        for doc in docs:
            doc.reference.delete()
            deleted += 1
            logger.info(f"Deleted document {doc.id} from {collection_name}")
        
        logger.info(f"Successfully deleted {deleted} documents from {collection_name}")
        return deleted
    except Exception as e:
        logger.error(f"Error deleting collection {collection_name}: {e}")
        return 0

def main():
    """Clear all specified collections"""
    collections = ['calls', 'tokenCache']
    total_deleted = 0
    
    logger.info("Starting Firebase cleanup...")
    
    for collection in collections:
        count = delete_collection(collection)
        total_deleted += count
        
    logger.info(f"Cleanup complete. Total documents deleted: {total_deleted}")

if __name__ == "__main__":
    main() 