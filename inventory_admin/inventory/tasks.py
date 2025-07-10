from celery import shared_task
from django.core.management import call_command
import traceback
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_fetch_inventory():
    logging.info("Running fetch inventory task...")
    try:
        print("Running fetch_inventory command via Celery…")
        call_command("fetch_inventory")
        print("Task completed successfully.")
        return "Inventory fetch task completed."
    except Exception as e:
        print("Exception during task execution:")
        traceback.print_exc()
        logger.exception("Task failed.")
        raise e
