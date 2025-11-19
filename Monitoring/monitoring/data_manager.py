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

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def save_scrape_results(results):
    """
    Save scrape results to both CSV timeseries and JSON snapshot

    Args:
        results: Dict from scraper.scrape_all_applications()
    """
    timestamp = datetime.now().isoformat()

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
