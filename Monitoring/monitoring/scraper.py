#!/usr/bin/env python3.9
"""
Planning Objection Letter Scraper
Monitors Uttlesford planning applications for B999 representation letters
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging
from pathlib import Path
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a session to maintain cookies
session = requests.Session()

# Application URLs
APPLICATIONS = {
    'birchanger': {
        'name': 'Birchanger (UTT/25/3011/OP)',
        'url': 'https://publicaccess.uttlesford.gov.uk/online-applications/applicationDetails.do?activeTab=documents&keyVal=T5CHIEQNG2G00'
    },
    'stansted': {
        'name': 'Stansted (UTT/25/3012/OP)',
        'url': 'https://publicaccess.uttlesford.gov.uk/online-applications/applicationDetails.do?activeTab=documents&keyVal=T5CHIWQNG2J00'
    }
}

def parse_date(date_str):
    """
    Parse date string from planning portal format
    Format: "DD MMM YYYY" (e.g., "18 Nov 2025")
    """
    try:
        return datetime.strptime(date_str.strip(), "%d %b %Y").strftime("%Y-%m-%d")
    except ValueError as e:
        logger.warning(f"Failed to parse date '{date_str}': {e}")
        return None

def scrape_application(app_id, url, app_name, max_retries=3, base_timeout=90):
    """
    Scrape B999 representation letters from application documents page

    Args:
        app_id: Application identifier (birchanger/stansted)
        url: Documents page URL
        app_name: Human-readable application name
        max_retries: Maximum number of retry attempts
        base_timeout: Base timeout in seconds (will increase with retries)

    Returns:
        dict: {
            'application_id': str,
            'application_name': str,
            'letters': list of dicts with 'date' and 'description'
            'total_count': int,
            'scrape_time': str (ISO format)
        }
    """
    logger.info(f"Scraping {app_name}...")

    # More realistic browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            # Add small random delay to appear more human-like
            if attempt > 0:
                delay = (2 ** attempt) + random.uniform(0, 1)
                logger.info(f"Retry attempt {attempt + 1}/{max_retries} after {delay:.1f}s delay...")
                time.sleep(delay)

            # Increase timeout with each retry
            timeout = base_timeout + (attempt * 30)
            logger.info(f"Requesting with {timeout}s timeout...")

            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find document table rows
            table = soup.find('table', {'id': 'Documents'})
            if not table:
                # Try without ID
                table = soup.find('table')

            if not table:
                logger.warning("Could not find document table")
                return {
                    'application_id': app_id,
                    'application_name': app_name,
                    'letters': [],
                    'total_count': 0,
                    'scrape_time': datetime.now().isoformat(),
                    'success': False,
                    'error': 'Document table not found'
                }

            # Get all tr elements from table (includes tbody if present)
            rows = table.find_all('tr')
            logger.info(f"Found {len(rows)} total document rows")

            b999_letters = []
            for row in rows:
                cells = row.find_all('td')

                # Skip header rows (have th elements) and rows with insufficient cells
                if len(cells) < 4 or row.find('th'):
                    continue

                # Cell structure:
                # 0: Checkbox
                # 1: Date Published
                # 2: Document Type
                # 3: Description
                # 4: View/Download link (optional)

                doc_type = cells[2].get_text(strip=True)

                if 'B999' in doc_type and 'Representation Letter' in doc_type:
                        date_str = cells[1].get_text(strip=True)
                        description = cells[3].get_text(strip=True)

                        parsed_date = parse_date(date_str)
                        if parsed_date:
                            b999_letters.append({
                                'date': parsed_date,
                                'date_display': date_str,
                                'description': description
                            })

            logger.info(f"Found {len(b999_letters)} B999 representation letters")

            return {
                'application_id': app_id,
                'application_name': app_name,
                'letters': b999_letters,
                'total_count': len(b999_letters),
                'scrape_time': datetime.now().isoformat(),
                'success': True,
                'error': None
            }

        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries} for {app_name}")
                continue  # Retry
            else:
                logger.error(f"All {max_retries} attempts timed out for {app_name}")
                return {
                    'application_id': app_id,
                    'application_name': app_name,
                    'letters': [],
                    'total_count': 0,
                    'scrape_time': datetime.now().isoformat(),
                    'success': False,
                    'error': f'Timeout after {max_retries} attempts'
                }
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                logger.warning(f"Request error on attempt {attempt + 1}/{max_retries} for {app_name}: {e}")
                continue  # Retry
            else:
                logger.error(f"Request failed after {max_retries} attempts for {app_name}: {e}")
                return {
                    'application_id': app_id,
                    'application_name': app_name,
                    'letters': [],
                    'total_count': 0,
                    'scrape_time': datetime.now().isoformat(),
                    'success': False,
                    'error': str(e)
                }
        except Exception as e:
            logger.error(f"Unexpected error scraping {app_name}: {e}")
            return {
                'application_id': app_id,
                'application_name': app_name,
                'letters': [],
                'total_count': 0,
                'scrape_time': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }

    # If we get here, all retries failed (shouldn't happen, but just in case)
    return {
        'application_id': app_id,
        'application_name': app_name,
        'letters': [],
        'total_count': 0,
        'scrape_time': datetime.now().isoformat(),
        'success': False,
        'error': 'All retry attempts exhausted'
    }

def scrape_all_applications():
    """
    Scrape all configured applications with rate limiting

    Returns:
        dict: Results keyed by application ID
    """
    logger.info("Starting scrape of all applications...")
    results = {}

    for app_id, config in APPLICATIONS.items():
        result = scrape_application(app_id, config['url'], config['name'])
        results[app_id] = result

        # Rate limiting: 5 second delay between requests
        if app_id != list(APPLICATIONS.keys())[-1]:  # Don't delay after last app
            logger.info("Rate limiting: waiting 5 seconds...")
            time.sleep(5)

    logger.info("Scrape complete")
    return results

def print_summary(results):
    """Print human-readable summary of scrape results"""
    print("\n" + "="*80)
    print("PLANNING OBJECTION LETTER MONITOR - SCRAPE RESULTS")
    print("="*80 + "\n")

    for app_id, data in results.items():
        print(f"📋 {data['application_name']}")
        if data['success']:
            print(f"   ✅ Total B999 Letters: {data['total_count']}")

            # Count by date
            if data['letters']:
                date_counts = {}
                for letter in data['letters']:
                    date = letter['date']
                    date_counts[date] = date_counts.get(date, 0) + 1

                print(f"   📅 Letters by date:")
                for date in sorted(date_counts.keys(), reverse=True):
                    print(f"      {date}: {date_counts[date]} letters")
        else:
            print(f"   ❌ Error: {data['error']}")
        print()

    print("="*80)
    print(f"Scrape completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

if __name__ == "__main__":
    import sys

    results = scrape_all_applications()
    print_summary(results)

    # Save results to data files
    try:
        from data_manager import save_scrape_results
        saved = save_scrape_results(results)
        if saved:
            logger.info("Results saved successfully")
            sys.exit(0)
        else:
            logger.error("Results validation failed - data not saved")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        sys.exit(1)
