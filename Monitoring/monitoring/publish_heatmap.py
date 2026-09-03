#!/usr/bin/env python3.9
"""
Publish a privacy-preserving heatmap feed from the private letters file.

letters.json holds one record per objection letter, geocoded to rooftop
precision and often carrying the street address in its description. That file
is private and gitignored. This script reduces it to the only thing the public
heatmap actually needs - weighted points on a coarse grid - and writes that to
monitoring_data/heatmap.json, which is the file the site serves.

Two reductions do the work:

  1. Coordinates are snapped to the centre of a ~275m grid cell, so a point no
     longer identifies a dwelling.
  2. Cells holding fewer than MIN_CELL_COUNT letters are dropped entirely, so a
     lone objector on an outlying lane is not published as a lone marker.

Suppressed letters still appear in the totals, so the counts on the page stay
truthful. No address, description, id or date-of-letter is published.

Usage:
    python3.9 publish_heatmap.py
"""

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'monitoring_data'
LETTERS_PATH = DATA_DIR / 'letters.json'          # private, full precision
HEATMAP_PATH = DATA_DIR / 'heatmap.json'          # public, aggregated

# Grid size. 0.0025 deg of latitude is ~278m; at 51.9N, 0.0040 deg of longitude
# is ~275m. Roughly square cells, comfortably larger than a garden.
GRID_LAT = 0.0025
GRID_LNG = 0.0040

# A cell must hold at least this many letters to be published.
MIN_CELL_COUNT = 3


def cell_centre(lat, lng):
    """Snap a coordinate to the centre of its grid cell."""
    lat_c = math.floor(lat / GRID_LAT) * GRID_LAT + GRID_LAT / 2
    lng_c = math.floor(lng / GRID_LNG) * GRID_LNG + GRID_LNG / 2
    return round(lat_c, 5), round(lng_c, 5)


def build_feed(letters_data):
    """Reduce the private letters list to an aggregated public feed."""
    letters = letters_data.get('letters', [])

    cells = {}
    mapped = 0
    for letter in letters:
        lat, lng = letter.get('lat'), letter.get('lng')
        if not letter.get('geocoded') or lat is None or lng is None:
            continue
        mapped += 1
        centre = cell_centre(lat, lng)
        cells[centre] = cells.get(centre, 0) + 1

    published = [
        {'lat': lat, 'lng': lng, 'count': count}
        for (lat, lng), count in sorted(cells.items())
        if count >= MIN_CELL_COUNT
    ]
    suppressed = mapped - sum(p['count'] for p in published)

    return {
        'generated': datetime.now(timezone.utc).isoformat(),
        'last_updated': letters_data.get('last_updated'),
        'totals': {
            'objections': len(letters),
            'mapped': mapped,
            'published': sum(p['count'] for p in published),
            'suppressed': suppressed,
        },
        'privacy': {
            'grid_metres': 275,
            'min_cell_count': MIN_CELL_COUNT,
            'note': (
                'Points are grid-cell centres, not addresses. Cells holding '
                'fewer than %d letters are not published. Suppressed letters '
                'are still counted in totals.' % MIN_CELL_COUNT
            ),
        },
        'points': published,
    }


def main():
    if not LETTERS_PATH.exists():
        logger.error("No private letters file at %s - nothing to publish", LETTERS_PATH)
        return 1

    with open(LETTERS_PATH) as f:
        letters_data = json.load(f)

    feed = build_feed(letters_data)

    with open(HEATMAP_PATH, 'w') as f:
        json.dump(feed, f, indent=2)
        f.write('\n')

    totals = feed['totals']
    logger.info(
        "Published %d points from %d mapped letters (%d suppressed in cells under %d) -> %s",
        len(feed['points']), totals['mapped'], totals['suppressed'],
        MIN_CELL_COUNT, HEATMAP_PATH.name
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
