from bucket import bucket
from celery import shared_task
import logging


logger = logging.getLogger(__name__)

@shared_task
def bucket_objects_task():
    try:
        return bucket.get_bucket_objects()
    except Exception as e:
        logger.error(f'Error getting bucket objects: {e}')
        return []

@shared_task
def delete_object_task(key):
    try:
        return bucket.delete_bucket_object(key)
    except Exception as e:
        logger.error(f'Error deleting object {key}: {e}')
        return False

@shared_task
def download_object_task(key):
    try:
        return bucket.download_bucket_object(key)
    except Exception as e:
        logger.error(f'Error downloading object {key}: {e}', exc_info=True)
        return False


@shared_task
def update_object_task(key, local_path):
    try:
        return bucket.update_bucket_object(key, local_path)
    except Exception as e:
        logger.error(f'Error updating object {key}: {e}')
        return False
    