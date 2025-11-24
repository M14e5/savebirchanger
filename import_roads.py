#!/usr/bin/env python3
"""
Import roads from OpenStreetMap into Supabase for the Canvassing Planner.

This script:
1. Queries Overpass API for all roads in the CM22, CM23, CM24 area
2. Converts them to GeoJSON format
3. Uploads to Supabase roads table

Usage:
    pip install requests supabase
    python3 import_roads.py
"""

import requests
import json
import hashlib
import time
from typing import Dict, List, Any

# Supabase configuration
SUPABASE_URL = "https://jwbjrgpcwwqrumstaqfi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3YmpyZ3Bjd3dxcnVtc3RhcWZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM5MDM2MDUsImV4cCI6MjA3OTQ3OTYwNX0.ZaN62Uhe09uheuzoLT1NWv4otrH0TI5XnKaDNwAFUUk"

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Bounding box for CM22, CM23, CM24 area (Bishop's Stortford, Stansted, Birchanger)
# Format: south, west, north, east
BBOX = "51.82,0.05,51.95,0.30"

def get_overpass_query() -> str:
    """Generate Overpass query for roads in the target area."""
    return f"""
[out:json][timeout:90];
(
  // Get all named roads/streets in the bounding box
  way["highway"]["name"]({BBOX});
);
out body;
>;
out skel qt;
"""

def fetch_roads_from_osm() -> Dict:
    """Fetch roads from OpenStreetMap via Overpass API."""
    print("Fetching roads from OpenStreetMap...")
    query = get_overpass_query()

    response = requests.post(
        OVERPASS_URL,
        data={'data': query},
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if response.status_code != 200:
        raise Exception(f"Overpass API error: {response.status_code} - {response.text}")

    return response.json()

def process_osm_data(osm_data: Dict) -> List[Dict]:
    """Process OSM data into road records for Supabase."""
    elements = osm_data.get('elements', [])

    # Separate nodes and ways
    nodes = {}
    ways = []

    for element in elements:
        if element['type'] == 'node':
            nodes[element['id']] = {
                'lat': element['lat'],
                'lng': element['lon']
            }
        elif element['type'] == 'way':
            ways.append(element)

    print(f"Found {len(ways)} road segments, {len(nodes)} nodes")

    # Convert ways to road records
    roads = []
    seen_names = {}  # Track roads by name to combine segments

    for way in ways:
        name = way.get('tags', {}).get('name', 'Unnamed Road')
        highway_type = way.get('tags', {}).get('highway', 'road')

        # Skip certain types
        if highway_type in ['footway', 'cycleway', 'path', 'steps', 'pedestrian', 'service']:
            continue

        # Build coordinates from node references
        coords = []
        for node_id in way.get('nodes', []):
            if node_id in nodes:
                node = nodes[node_id]
                coords.append([node['lng'], node['lat']])

        if len(coords) < 2:
            continue

        # Create GeoJSON LineString
        geojson = {
            "type": "Feature",
            "properties": {
                "name": name,
                "highway": highway_type,
                "osm_id": way['id']
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        }

        # Generate unique ID based on OSM way ID
        road_id = f"osm_{way['id']}"

        roads.append({
            'id': road_id,
            'name': name,
            'geojson': geojson,
            'status': 'none',
            'last_checked': None,
            'updated_by': None
        })

    print(f"Processed {len(roads)} valid road segments")
    return roads

def upload_to_supabase(roads: List[Dict]) -> None:
    """Upload roads to Supabase using REST API."""
    print(f"Uploading {len(roads)} roads to Supabase...")

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }

    # Upload in batches of 100
    batch_size = 100
    total_uploaded = 0

    for i in range(0, len(roads), batch_size):
        batch = roads[i:i + batch_size]

        # Convert geojson to JSON string for each road
        payload = []
        for road in batch:
            payload.append({
                'id': road['id'],
                'name': road['name'],
                'geojson': road['geojson'],  # Supabase will handle JSONB conversion
                'status': 'none'
            })

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/roads",
            headers=headers,
            json=payload
        )

        if response.status_code not in [200, 201]:
            print(f"Error uploading batch {i//batch_size + 1}: {response.status_code}")
            print(response.text[:500])
        else:
            total_uploaded += len(batch)
            print(f"Uploaded batch {i//batch_size + 1}: {total_uploaded}/{len(roads)} roads")

        # Rate limiting
        time.sleep(0.5)

    print(f"Done! Uploaded {total_uploaded} roads to Supabase")

def get_road_count() -> int:
    """Check how many roads are currently in Supabase."""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Prefer': 'count=exact'
    }

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/roads?select=id",
        headers=headers
    )

    if 'content-range' in response.headers:
        # Parse count from content-range header
        range_header = response.headers['content-range']
        if '/' in range_header:
            return int(range_header.split('/')[-1])

    return len(response.json()) if response.status_code == 200 else 0

def main():
    """Main entry point."""
    import sys

    # Check for --force flag
    force = '--force' in sys.argv

    print("=" * 50)
    print("Road Import Script for Canvassing Planner")
    print("=" * 50)

    # Check existing count
    existing = get_road_count()
    print(f"Current roads in Supabase: {existing}")

    if existing > 0 and not force:
        confirm = input(f"There are already {existing} roads. Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return

    # Fetch and process roads
    osm_data = fetch_roads_from_osm()
    roads = process_osm_data(osm_data)

    if not roads:
        print("No roads found!")
        return

    # Show sample
    print("\nSample roads:")
    for road in roads[:5]:
        print(f"  - {road['name']} ({road['id']})")

    # Confirm upload
    if not force:
        confirm = input(f"\nUpload {len(roads)} roads to Supabase? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return
    else:
        print(f"\nUploading {len(roads)} roads to Supabase (--force mode)...")

    # Upload
    upload_to_supabase(roads)

    # Verify
    final_count = get_road_count()
    print(f"\nFinal road count in Supabase: {final_count}")

if __name__ == '__main__':
    main()
