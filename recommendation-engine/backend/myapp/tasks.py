from celery import shared_task
from celery.utils.log import get_task_logger
from .langchain import process_query, process_bulk_csv

logger = get_task_logger(__name__)

@shared_task(name='myapp.tasks.process_query_async', bind=True)
def process_query_async(self, source: str, dest: str) -> dict:
    """
    Asynchronous task to process travel queries
    """
    logger.info(f"Starting query processing for {source} to {dest}")
    try:
        result = process_query(source, dest)
        logger.info(f"Query processing completed for {source} to {dest}")
        return {
            'status': 'SUCCESS',
            'result': result
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e)
        }

@shared_task(name='myapp.tasks.process_bulk_csv_async', bind=True)
def process_bulk_csv_async(self, routes):
    """
    Asynchronous task to process bulk CSV data
    """
    logger.info("Starting bulk CSV processing")
    try:
        result = process_bulk_csv(routes)
        logger.info("Bulk CSV processing completed")
        return {
            'status': 'SUCCESS',
            'result': result
        }
    except Exception as e:
        logger.error(f"Error processing bulk CSV: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e)
        }