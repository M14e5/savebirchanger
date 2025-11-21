#!/usr/bin/env python3.9
"""
Geocoder for Planning Objection Letters
Uses Nominatim (OpenStreetMap) to convert addresses to coordinates
"""

import json
import time
import logging
import re
import requests
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'monitoring_data'
LETTERS_PATH = DATA_DIR / 'letters.json'

# Nominatim API configuration
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "SaveBirchangerCampaign/1.0 (objection-heatmap)"

# Bias search toward Essex/Hertfordshire area
SEARCH_VIEWBOX = "-0.5,52.1,0.5,51.7"  # lon1,lat1,lon2,lat2 bounding box
SEARCH_BOUNDED = "1"

# Rate limiting (Nominatim requires max 1 request per second)
REQUEST_DELAY = 1.1  # seconds between requests

# Towns to try in order for fallback geocoding
FALLBACK_TOWNS = [
    'Birchanger',
    'Stansted Mountfitchet',
    "Bishop's Stortford",
    'Stansted',
    None  # Try with just "Essex, UK"
]

# Approximate village center coordinates for named houses
VILLAGE_CENTERS = {
    'birchanger': (51.8825, 0.1900),
    'stansted': (51.8980, 0.1970),
}

def load_letters():
    """Load letters from JSON file"""
    if LETTERS_PATH.exists():
        with open(LETTERS_PATH, 'r') as f:
            return json.load(f)
    return {"letters": [], "last_updated": None}

def save_letters(letters_data):
    """Save letters to JSON file"""
    letters_data['last_updated'] = datetime.now().isoformat()
    with open(LETTERS_PATH, 'w') as f:
        json.dump(letters_data, f, indent=2)
    logger.info(f"Saved {len(letters_data['letters'])} letters")

def clean_address_text(description):
    """
    Clean and normalize address text from description.

    Returns:
        str: Cleaned address text (without town/county)
    """
    if not description:
        return None

    text = description.strip().upper()

    # Remove common suffixes like "- COMMENT", "- COMMENTS", "- 1 COMMENTS"
    text = re.sub(r'\s*-\s*\d*\s*(COMMENTS?|OBJECTION|SUPPORT|REPRESENTATION).*$', '', text, flags=re.IGNORECASE)
    text = text.strip()

    if not text:
        return None

    # Handle compound addresses like "HERNE HOUSE, 68 BIRCHANGER LANE"
    # Extract the street address part if there's a house name followed by street
    if ',' in text:
        parts = [p.strip() for p in text.split(',')]
        # Check if second part looks like a street address
        for part in parts[1:]:
            if re.match(r'^\d+', part):  # Starts with number
                text = part
                break

    return text

def generate_address_variations(address_text):
    """
    Generate variations of an address to try for geocoding.

    Returns:
        list: List of address variations to try
    """
    variations = [address_text]

    # Try without house number (just street name)
    no_number = re.sub(r'^\d+[A-Z]?\s+', '', address_text)
    if no_number != address_text:
        variations.append(no_number)

    # Handle "ST JOHNS" -> "ST JOHN'S" -> "SAINT JOHN'S"
    if 'ST ' in address_text:
        # Add apostrophe version
        apostrophe_version = re.sub(r'\bST (\w+)S\b', r"ST \1'S", address_text)
        if apostrophe_version != address_text:
            variations.append(apostrophe_version)
        # Add SAINT version
        saint_version = re.sub(r'\bST\b', 'SAINT', address_text)
        variations.append(saint_version)

    return variations

def extract_location_from_description(description, application=None):
    """
    Extract location/address from description text.
    Now returns just the cleaned address without town - town is added during geocoding.

    Args:
        description: The description text from the planning portal
        application: 'birchanger' or 'stansted' to help infer town

    Returns:
        str: Cleaned address text (without town suffix)
    """
    if not description:
        return None

    text = clean_address_text(description)
    if not text:
        return None

    # Try to extract UK postcode first (most reliable for geocoding)
    postcode_pattern = r'[A-Z]{1,2}[0-9][0-9A-Z]?\s*[0-9][A-Z]{2}'
    postcode_match = re.search(postcode_pattern, text, re.IGNORECASE)
    if postcode_match:
        return postcode_match.group(0).upper()

    return text

def is_named_house(address_text):
    """Check if address is just a named house (no street info)"""
    street_types = ['road', 'street', 'lane', 'way', 'close', 'drive', 'avenue',
                    'gardens', 'place', 'terrace', 'court', 'crescent', 'row',
                    'fields', 'view', 'green', 'walk', 'rise', 'hill', 'meadow',
                    'common', 'end', 'corner', 'stow', 'side']

    text_lower = address_text.lower()
    has_number = bool(re.match(r'^\d+', address_text))
    has_street_type = any(st in text_lower for st in street_types)

    # Named house if no number and no street type word
    return not has_number and not has_street_type

def geocode_location(location_text, bounded=True):
    """
    Geocode a location string using Nominatim

    Args:
        location_text: Address or place name to geocode
        bounded: If True, restrict to viewbox area; if False, search wider

    Returns:
        tuple: (lat, lng) or (None, None) if geocoding fails
    """
    if not location_text:
        return None, None

    params = {
        'q': location_text,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'gb',
        'viewbox': SEARCH_VIEWBOX,
    }

    if bounded:
        params['bounded'] = '1'

    headers = {
        'User-Agent': USER_AGENT
    }

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        results = response.json()
        if results:
            lat = float(results[0]['lat'])
            lng = float(results[0]['lon'])
            return lat, lng
        else:
            return None, None

    except requests.exceptions.RequestException as e:
        logger.error(f"Geocoding request failed for '{location_text}': {e}")
        return None, None
    except (KeyError, ValueError, IndexError) as e:
        logger.error(f"Failed to parse geocoding response for '{location_text}': {e}")
        return None, None

def geocode_with_fallbacks(address_text, application=None):
    """
    Try to geocode an address using multiple strategies:
    1. Try with each town in FALLBACK_TOWNS
    2. Try address variations (without number, ST -> SAINT, etc.)
    3. Try unbounded search as last resort
    4. For named houses, use village center as approximation

    Args:
        address_text: Cleaned address text (without town)
        application: 'birchanger' or 'stansted'

    Returns:
        tuple: (lat, lng, matched_location) or (None, None, None)
    """
    if not address_text:
        return None, None, None

    # Check if this is just a named house
    if is_named_house(address_text):
        # Use village center as approximate location
        if application in VILLAGE_CENTERS:
            lat, lng = VILLAGE_CENTERS[application]
            logger.info(f"Using village center for named house '{address_text}' -> ({lat:.4f}, {lng:.4f})")
            return lat, lng, f"{address_text} (approx: {application} village)"
        return None, None, None

    # Generate address variations to try
    variations = generate_address_variations(address_text)

    # Order towns to try - prioritize based on application
    towns_to_try = list(FALLBACK_TOWNS)
    if application == 'birchanger':
        # Birchanger first, then others
        pass  # Already in right order
    elif application == 'stansted':
        # Stansted first
        towns_to_try = ['Stansted Mountfitchet', 'Birchanger', "Bishop's Stortford", 'Stansted', None]

    # Try each variation with each town
    for variation in variations:
        for town in towns_to_try:
            if town:
                full_address = f"{variation}, {town}, Essex, UK"
            else:
                full_address = f"{variation}, Essex, UK"

            lat, lng = geocode_location(full_address, bounded=True)
            if lat is not None:
                logger.info(f"Geocoded '{address_text}' via '{full_address}' -> ({lat:.4f}, {lng:.4f})")
                return lat, lng, full_address

            time.sleep(REQUEST_DELAY)

    # Last resort: try unbounded search with just Essex
    for variation in variations[:2]:  # Only try first 2 variations unbounded
        full_address = f"{variation}, Essex, UK"
        lat, lng = geocode_location(full_address, bounded=False)
        if lat is not None:
            logger.info(f"Geocoded '{address_text}' (unbounded) via '{full_address}' -> ({lat:.4f}, {lng:.4f})")
            return lat, lng, full_address
        time.sleep(REQUEST_DELAY)

    return None, None, None

def geocode_all_letters(force=False, retry_failed=False):
    """
    Geocode all letters that haven't been geocoded yet

    Args:
        force: If True, re-geocode ALL letters (including successful ones)
        retry_failed: If True, retry previously failed letters with new strategy

    Returns:
        dict: Statistics about geocoding results
    """
    letters_data = load_letters()

    stats = {
        'total': len(letters_data['letters']),
        'already_geocoded': 0,
        'newly_geocoded': 0,
        'failed': 0,
        'no_location': 0,
        'named_houses': 0
    }

    letters_to_process = []
    for letter in letters_data['letters']:
        if force:
            letters_to_process.append(letter)
        elif retry_failed and letter.get('geocode_error'):
            letters_to_process.append(letter)
        elif not letter.get('geocoded') and not letter.get('geocode_error'):
            letters_to_process.append(letter)
        elif letter.get('geocoded'):
            stats['already_geocoded'] += 1

    if not letters_to_process:
        logger.info("No letters to geocode")
        return stats

    logger.info(f"Processing {len(letters_to_process)} letters with cascading fallback strategy...")

    for i, letter in enumerate(letters_to_process):
        logger.info(f"Processing {i+1}/{len(letters_to_process)}: {letter['id']} - {letter['description'][:40]}...")

        # Extract cleaned address from description
        address_text = extract_location_from_description(letter['description'], letter.get('application'))

        if not address_text:
            logger.warning(f"Could not extract location from: {letter['description'][:50]}...")
            letter['geocode_error'] = "no_location_found"
            stats['no_location'] += 1
            continue

        # Use cascading fallback geocoding
        lat, lng, matched_location = geocode_with_fallbacks(address_text, letter.get('application'))

        if lat is not None and lng is not None:
            letter['lat'] = lat
            letter['lng'] = lng
            letter['geocoded'] = True
            letter['geocode_error'] = None
            letter['geocoded_location'] = matched_location
            stats['newly_geocoded'] += 1

            # Track if it was a named house approximation
            if 'approx:' in (matched_location or ''):
                stats['named_houses'] += 1
        else:
            letter['geocode_error'] = "geocoding_failed"
            stats['failed'] += 1
            logger.warning(f"Failed to geocode: {address_text}")

        # Save periodically (every 20 letters) to preserve progress
        if (i + 1) % 20 == 0:
            save_letters(letters_data)
            logger.info(f"Progress saved: {i+1}/{len(letters_to_process)}")

    # Save final data
    save_letters(letters_data)

    logger.info(f"Geocoding complete: {stats['newly_geocoded']} successful ({stats['named_houses']} named houses), {stats['failed']} failed, {stats['no_location']} no location")
    return stats

def get_geocoded_letters():
    """
    Get all successfully geocoded letters for heatmap display

    Returns:
        list: Letters with lat/lng coordinates
    """
    letters_data = load_letters()
    return [
        {
            'id': l['id'],
            'application': l['application'],
            'date': l['date'],
            'lat': l['lat'],
            'lng': l['lng'],
            'location': l.get('geocoded_location', '')
        }
        for l in letters_data['letters']
        if l.get('geocoded') and l.get('lat') is not None
    ]

def print_stats():
    """Print statistics about geocoded letters"""
    letters_data = load_letters()

    total = len(letters_data['letters'])
    geocoded = sum(1 for l in letters_data['letters'] if l.get('geocoded'))
    failed = sum(1 for l in letters_data['letters'] if l.get('geocode_error'))
    pending = total - geocoded - failed

    print("\n" + "="*60)
    print("GEOCODING STATISTICS")
    print("="*60)
    print(f"Total letters:     {total}")
    print(f"Geocoded:          {geocoded} ({100*geocoded/total:.1f}%)" if total > 0 else "Geocoded: 0")
    print(f"Failed:            {failed}")
    print(f"Pending:           {pending}")
    print("="*60 + "\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Geocode objection letters')
    parser.add_argument('--force', action='store_true', help='Re-geocode ALL letters (including successful)')
    parser.add_argument('--retry-failed', action='store_true', help='Retry previously failed letters with improved strategy')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    args = parser.parse_args()

    if args.stats:
        print_stats()
    else:
        stats = geocode_all_letters(force=args.force, retry_failed=args.retry_failed)
        print_stats()
