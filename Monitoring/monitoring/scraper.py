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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def scrape_application(app_id, url, app_name):
    """
    Scrape B999 representation letters from application documents page

    Args:
        app_id: Application identifier (birchanger/stansted)
        url: Documents page URL
        app_name: Human-readable application name

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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Objection Monitor - Research Tool)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        response = requests.get(url, headers=headers, timeout=60)
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

    except requests.exceptions.Timeout:
        logger.error(f"Timeout scraping {app_name}")
        return {
            'application_id': app_id,
            'application_name': app_name,
            'letters': [],
            'total_count': 0,
            'scrape_time': datetime.now().isoformat(),
            'success': False,
            'error': 'Timeout'
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error scraping {app_name}: {e}")
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
