#!/usr/bin/env python3.9
"""
Data Management for Planning Objection Monitor
Handles CSV timeseries and JSON snapshot storage
"""

import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data paths
BASE_DIR = Path(__file__).parent.parent.parent  # Go to project root
DATA_DIR = BASE_DIR / 'monitoring_data'
CSV_PATH = DATA_DIR / 'timeseries.csv'
JSON_PATH = DATA_DIR / 'latest.json'
METADATA_PATH = DATA_DIR / 'metadata.json'
LETTERS_PATH = DATA_DIR / 'letters.json'

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

import hashlib

def generate_letter_id(application, date, description):
    """Generate a unique ID for a letter based on its content"""
    content = f"{application}:{date}:{description}"
    return hashlib.md5(content.encode()).hexdigest()[:12]

def load_letters():
    """Load existing letters from JSON file"""
    if LETTERS_PATH.exists():
        try:
            with open(LETTERS_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load letters.json: {e}")
    return {"letters": [], "last_updated": None}

def save_letters(letters_data):
    """Save letters to JSON file"""
    try:
        with open(LETTERS_PATH, 'w') as f:
            json.dump(letters_data, f, indent=2)
        logger.info(f"Saved {len(letters_data['letters'])} letters to {LETTERS_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error saving letters: {e}")
        return False

def save_individual_letters(results):
    """
    Save individual letter records with descriptions for geocoding

    Args:
        results: Dict from scraper.scrape_all_applications()

    Returns:
        int: Number of new letters added
    """
    letters_data = load_letters()
    existing_ids = {letter['id'] for letter in letters_data['letters']}

    new_count = 0
    for app_id, data in results.items():
        if data['success'] and data['letters']:
            for letter in data['letters']:
                letter_id = generate_letter_id(app_id, letter['date'], letter['description'])

                if letter_id not in existing_ids:
                    letters_data['letters'].append({
                        'id': letter_id,
                        'application': app_id,
                        'date': letter['date'],
                        'description': letter['description'],
                        'lat': None,
                        'lng': None,
                        'geocoded': False,
                        'geocode_error': None
                    })
                    existing_ids.add(letter_id)
                    new_count += 1

    if new_count > 0:
        letters_data['last_updated'] = datetime.now().isoformat()
        save_letters(letters_data)
        logger.info(f"Added {new_count} new letters to letters.json")

    return new_count

def validate_scrape_results(results):
    """
    Validate scrape results before saving

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if all scrapes failed
    all_failed = all(not data['success'] for data in results.values())
    if all_failed:
        return False, "All scrapes failed - refusing to save zero counts"

    # Check against previous data if it exists
    if JSON_PATH.exists():
        try:
            with open(JSON_PATH, 'r') as f:
                prev_data = json.load(f)

            for app_id, data in results.items():
                if data['success']:
                    prev_app = prev_data.get('applications', {}).get(app_id, {})
                    prev_total = prev_app.get('total', 0)
                    new_total = data['total_count']

                    # Objection counts should never decrease
                    if prev_total > 0 and new_total < prev_total:
                        return False, f"Objection count for {app_id} decreased from {prev_total} to {new_total} - data integrity check failed"

                    # Warn if count is zero when previous had data
                    if prev_total > 0 and new_total == 0:
                        return False, f"Objection count for {app_id} is zero but was previously {prev_total} - refusing to overwrite"

        except Exception as e:
            logger.warning(f"Could not validate against previous data: {e}")
            # Continue anyway if we can't read previous data

    return True, None

def save_scrape_results(results):
    """
    Save scrape results to both CSV timeseries and JSON snapshot

    Args:
        results: Dict from scraper.scrape_all_applications()

    Returns:
        bool: True if saved successfully, False otherwise
    """
    # Validate before saving
    is_valid, error_msg = validate_scrape_results(results)
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        return False

    timestamp = datetime.now().isoformat()

    # Save individual letters for geocoding/heatmap
    new_letters = save_individual_letters(results)
    if new_letters > 0:
        logger.info(f"Saved {new_letters} new individual letters for geocoding")

    try:
        # Prepare CSV rows
        csv_rows = []
        for app_id, data in results.items():
            if data['success'] and data['letters']:
                # Group letters by date
                date_counts = defaultdict(int)
                for letter in data['letters']:
                    date_counts[letter['date']] += 1

                # Create rows for each date
                for date, count in date_counts.items():
                    csv_rows.append({
                        'timestamp': timestamp,
                        'application': app_id,
                        'date_published': date,
                        'count': count
                    })

        # Append to CSV (or create if doesn't exist)
        if csv_rows:
            df = pd.DataFrame(csv_rows)
            if CSV_PATH.exists():
                df.to_csv(CSV_PATH, mode='a', header=False, index=False)
                logger.info(f"Appended {len(csv_rows)} rows to {CSV_PATH}")
            else:
                df.to_csv(CSV_PATH, index=False)
                logger.info(f"Created {CSV_PATH} with {len(csv_rows)} rows")

        # Create JSON snapshot
        snapshot = {
            'last_updated': timestamp,
            'applications': {}
        }

        for app_id, data in results.items():
            if data['success']:
                # Group by date
                by_date = defaultdict(int)
                for letter in data['letters']:
                    by_date[letter['date']] += 1

                snapshot['applications'][app_id] = {
                    'name': data['application_name'],
                    'total': data['total_count'],
                    'by_date': dict(sorted(by_date.items(), reverse=True)),
                    'success': True
                }
            else:
                snapshot['applications'][app_id] = {
                    'name': data['application_name'],
                    'total': 0,
                    'by_date': {},
                    'success': False,
                    'error': data['error']
                }

        # Write JSON snapshot
        with open(JSON_PATH, 'w') as f:
            json.dump(snapshot, f, indent=2)
        logger.info(f"Updated JSON snapshot at {JSON_PATH}")

        # Update metadata
        metadata = {
            'last_update': timestamp,
            'last_success': all(d['success'] for d in results.values()),
            'total_scrapes': get_total_scrapes() + 1,
            'errors': [
                {'app': app_id, 'error': data['error']}
                for app_id, data in results.items()
                if not data['success']
            ]
        }

        with open(METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Updated metadata at {METADATA_PATH}")

        return True

    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

def get_total_scrapes():
    """Get total number of scrapes performed"""
    try:
        if METADATA_PATH.exists():
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
                return metadata.get('total_scrapes', 0)
    except Exception:
        pass
    return 0

def get_chart_data():
    """
    Get data formatted for Chart.js visualization

    Returns:
        dict: {
            'dates': list of date strings,
            'birchanger_counts': list of counts,
            'stansted_counts': list of counts
        }
    """
    try:
        if not CSV_PATH.exists():
            return {'dates': [], 'birchanger_counts': [], 'stansted_counts': []}

        df = pd.read_csv(CSV_PATH)

        # Get most recent data point (latest timestamp)
        latest_timestamp = df['timestamp'].max()
        latest_data = df[df['timestamp'] == latest_timestamp]

        # Get all unique dates
        all_dates = sorted(latest_data['date_published'].unique())

        # Prepare data by application
        birchanger_data = latest_data[latest_data['application'] == 'birchanger']
        stansted_data = latest_data[latest_data['application'] == 'stansted']

        # Create count arrays (0 if no data for that date)
        birchanger_counts = []
        stansted_counts = []

        for date in all_dates:
            b_count = birchanger_data[birchanger_data['date_published'] == date]['count'].sum()
            s_count = stansted_data[stansted_data['date_published'] == date]['count'].sum()
            birchanger_counts.append(int(b_count))
            stansted_counts.append(int(s_count))

        return {
            'dates': all_dates,
            'birchanger_counts': birchanger_counts,
            'stansted_counts': stansted_counts
        }

    except Exception as e:
        logger.error(f"Error generating chart data: {e}")
        return {'dates': [], 'birchanger_counts': [], 'stansted_counts': []}

def get_summary():
    """Get human-readable summary of latest data"""
    try:
        if JSON_PATH.exists():
            with open(JSON_PATH, 'r') as f:
                data = json.load(f)
                return data
    except Exception as e:
        logger.error(f"Error reading summary: {e}")

    return None

if __name__ == "__main__":
    # Test: load and display current data
    summary = get_summary()
    if summary:
        print("\n" + "="*80)
        print("CURRENT MONITORING DATA")
        print("="*80 + "\n")
        print(f"Last updated: {summary['last_updated']}\n")

        for app_id, app_data in summary['applications'].items():
            print(f"📋 {app_data['name']}")
            if app_data['success']:
                print(f"   Total letters: {app_data['total']}")
                print(f"   By date:")
                for date, count in list(app_data['by_date'].items())[:5]:
                    print(f"      {date}: {count}")
            else:
                print(f"   ❌ Error: {app_data['error']}")
            print()
    else:
        print("No data available. Run scraper first.")

    # Test: get chart data
    chart_data = get_chart_data()
    if chart_data['dates']:
        print("\n" + "="*80)
        print("CHART DATA")
        print("="*80 + "\n")
        print(f"Dates: {len(chart_data['dates'])}")
        print(f"Birchanger data points: {len(chart_data['birchanger_counts'])}")
        print(f"Stansted data points: {len(chart_data['stansted_counts'])}")
