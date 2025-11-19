#!/usr/bin/env python3.9
"""
Automated Scheduler for Planning Objection Monitor
Runs scraper every 6 hours and saves data
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring import scraper, data_manager

# Configure logging
LOG_DIR = Path(__file__).parent.parent / 'monitoring_data'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'scraper.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_scrape_job():
    """Execute scraping and data saving job"""
    logger.info("="*80)
    logger.info("SCHEDULED SCRAPE STARTING")
    logger.info("="*80)

    try:
        # Run scraper
        results = scraper.scrape_all_applications()

        # Save results
        success = data_manager.save_scrape_results(results)

        if success:
            logger.info("✅ Scrape completed successfully")
            logger.info(f"   Birchanger: {results['birchanger']['total_count']} letters")
            logger.info(f"   Stansted: {results['stansted']['total_count']} letters")
        else:
            logger.error("❌ Failed to save scrape results")

        logger.info("="*80 + "\n")
        return success

    except Exception as e:
        logger.error(f"❌ Fatal error in scrape job: {e}")
        logger.info("="*80 + "\n")
        return False

def job_listener(event):
    """Listen to job execution events"""
    if event.exception:
        logger.error(f"Job failed with exception: {event.exception}")
    else:
        logger.info(f"Job executed successfully at {datetime.now()}")

def main():
    """Start the scheduler"""
    logger.info("\n" + "="*80)
    logger.info("PLANNING OBJECTION MONITOR - SCHEDULER STARTING")
    logger.info("="*80)
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Schedule: Every 6 hours")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80 + "\n")

    # Create scheduler
    scheduler = BlockingScheduler()

    # Add job: run every 6 hours
    scheduler.add_job(
        run_scrape_job,
        'interval',
        hours=6,
        id='scrape_job',
        name='Scrape planning applications',
        max_instances=1,
        coalesce=True
    )

    # Add listener
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Run initial scrape immediately
    logger.info("Running initial scrape...")
    run_scrape_job()

    # Start scheduler
    try:
        logger.info("Scheduler started. Press Ctrl+C to stop.\n")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n\nScheduler stopped by user.")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
