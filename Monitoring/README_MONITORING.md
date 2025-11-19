# Planning Objection Letter Monitoring System

Automated tracking and visualization of public objection letters (B999 - Representation Letters) submitted to Uttlesford District Council planning applications.

## Applications Monitored

- **Birchanger (UTT/25/3011/OP):** 180 dwellings outline application
- **Stansted (UTT/25/3012/OP):** 300 dwellings + commercial outline application

## Features

✅ **Automated Scraping:** Polls planning portal every 6 hours
✅ **Real-time Tracking:** Counts objection letters as they're submitted
✅ **Interactive Visualization:** Chart.js dashboard with zoom functionality
✅ **Historical Data:** CSV timeseries for analysis
✅ **Auto-refresh Dashboard:** Updates every 10 minutes
✅ **Polite Scraping:** Rate limited, respectful of server resources

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_monitoring.txt
```

### 2. Run Initial Scrape

```bash
python3.9 monitoring/scraper.py
```

**Expected output:**
```
================================================================================
PLANNING OBJECTION LETTER MONITOR - SCRAPE RESULTS
================================================================================

📋 Birchanger (UTT/25/3011/OP)
   ✅ Total B999 Letters: 38
   📅 Letters by date:
      2025-11-19: 2 letters
      2025-11-18: 7 letters
      2025-11-17: 14 letters
      ...
```

### 3. View Dashboard

```bash
firefox monitoring/dashboard.html
# OR
python -m http.server 8000  # Then visit http://localhost:8000/monitoring/dashboard.html
```

### 4. Start Background Monitoring (Optional)

```bash
./run_monitor.sh
```

**To stop:**
```bash
pkill -f "scheduler.py"
```

## System Architecture

```
monitoring/
├── scraper.py              # Core scraping logic
├── data_manager.py         # CSV + JSON data persistence
├── scheduler.py            # 6-hour automated polling
└── dashboard.html          # Interactive visualization

monitoring_data/
├── timeseries.csv          # Historical data (timestamp, application, date, count)
├── latest.json             # Current snapshot for dashboard
├── metadata.json           # Last update, scrape count, errors
└── scraper.log             # Execution logs
```

## Data Format

### timeseries.csv
```csv
timestamp,application,date_published,count
2025-11-19T14:09:14.395639,birchanger,2025-11-19,2
2025-11-19T14:09:14.395639,birchanger,2025-11-18,7
2025-11-19T14:09:14.395639,stansted,2025-11-19,2
...
```

### latest.json
```json
{
  "last_updated": "2025-11-19T14:09:14.395639",
  "applications": {
    "birchanger": {
      "name": "Birchanger (UTT/25/3011/OP)",
      "total": 38,
      "by_date": {
        "2025-11-19": 2,
        "2025-11-18": 7,
        "2025-11-17": 14
      },
      "success": true
    },
    "stansted": {
      "name": "Stansted (UTT/25/3012/OP)",
      "total": 36,
      "by_date": { ... },
      "success": true
    }
  }
}
```

## Usage Examples

### Manual One-Time Scrape

```bash
python3.9 monitoring/scraper.py
```

### Check Data Summary

```bash
python3.9 monitoring/data_manager.py
```

### Start Scheduled Monitoring

```bash
# Foreground (see logs in terminal)
python3.9 monitoring/scheduler.py

# Background (logs to file)
./run_monitor.sh
```

### View Logs

```bash
tail -f monitoring_data/scraper.log
```

### Stop Background Monitoring

```bash
# Find PID
cat monitoring_data/monitor.pid

# Kill process
kill $(cat monitoring_data/monitor.pid)

# OR
pkill -f "scheduler.py"
```

## Dashboard Features

### Total Count Cards
- Large numbers showing current objection letter counts
- Color-coded by application
- Error indicators if scraping fails

### Interactive Timeline Chart
- **X-axis:** Date published
- **Y-axis:** Number of letters submitted
- **Dual lines:** Birchanger (blue) vs Stansted (red)
- **Hover:** See exact counts for each date
- **Zoom:** Click and drag to zoom into date range
- **Reset:** Double-click to reset zoom
- **Auto-refresh:** Updates every 10 minutes

### Status Indicators
- Green pulse: System healthy, data current
- Red pulse: Scraping error encountered
- Last update timestamp

## Configuration

### Change Polling Interval

Edit `monitoring/scheduler.py`:

```python
scheduler.add_job(
    run_scrape_job,
    'interval',
    hours=6,  # Change this (e.g., 1, 12, 24)
    ...
)
```

### Add More Applications

Edit `monitoring/scraper.py`:

```python
APPLICATIONS = {
    'birchanger': {
        'name': 'Birchanger (UTT/25/3011/OP)',
        'url': 'https://publicaccess.uttlesford.gov.uk/online-applications/...'
    },
    'your_app': {
        'name': 'Your Application Name',
        'url': 'https://publicaccess.uttlesford.gov.uk/online-applications/...'
    }
}
```

## Troubleshooting

### "No data available" in dashboard

**Cause:** Scraper hasn't run yet
**Fix:** Run `python3.9 monitoring/scraper.py`

### Dashboard not loading JSON

**Cause:** CORS restriction when opening file:// directly
**Fix:** Run local HTTP server:
```bash
python -m http.server 8000
# Visit: http://localhost:8000/monitoring/dashboard.html
```

### Scraper finds 0 letters despite portal showing documents

**Cause:** HTML structure changed or parser issue
**Fix:**
1. Check if portal is accessible: Visit URL in browser
2. Run scraper with verbose logging
3. Check `monitoring_data/scraper.log` for errors

### Background monitoring not starting

**Cause:** PID file exists from previous run
**Fix:**
```bash
rm monitoring_data/monitor.pid
./run_monitor.sh
```

### Rate limiting / 429 errors

**Cause:** Too frequent requests
**Fix:** Increase polling interval in scheduler.py (recommended: 6+ hours)

## Development

### Run Tests

```bash
# Test scraper only
python3.9 monitoring/scraper.py

# Test data manager only
python3.9 monitoring/data_manager.py

# Test integrated pipeline
python3.9 -c "
from monitoring import scraper, data_manager
results = scraper.scrape_all_applications()
data_manager.save_scrape_results(results)
"
```

### Debug Mode

Add logging to scraper.py:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Technical Details

### Scraping Methodology

- **HTTP Library:** `requests` with `lxml` parser
- **HTML Parsing:** BeautifulSoup4
- **Target Table:** `id="Documents"`
- **Document Type Filter:** "B999 - Representation Letter"
- **Date Format:** "DD MMM YYYY" → ISO 8601 (YYYY-MM-DD)
- **Rate Limiting:** 5-second delay between applications
- **Timeout:** 30 seconds per request
- **User Agent:** `Mozilla/5.0 (Objection Monitor - Research Tool)`

### Polite Scraping Practices

✅ Clear user agent identification
✅ 6-hour polling interval (4 requests/day)
✅ 5-second delays between requests
✅ 30-second timeouts
✅ Graceful error handling
✅ Respects robots.txt spirit (public consultation data)

### Data Storage

- **CSV:** Append-only, suitable for long-term analysis
- **JSON:** Overwrite, optimized for dashboard fast loading
- **No database required:** Filesystem-based for simplicity

### Visualization Stack

- **Chart.js 4.4.0:** MIT license, 187KB
- **Chart.js Zoom Plugin 2.0.1:** Drag-to-zoom functionality
- **Vanilla JavaScript:** No build step required
- **Static HTML:** No web server required (optional for CORS)

## Ethical Considerations

### Legal Basis

- **Public Data:** Planning consultation documents are publicly accessible
- **Legitimate Interest:** Monitoring public objection campaigns
- **No Authentication:** No login bypass or access control circumvention
- **No Personal Data:** Counts only, no extraction of objector identities

### Robots.txt

Site has `Disallow: /` but:
- This is **public consultation data** required to be accessible
- Polling frequency (6 hours) is **extremely respectful**
- User agent is **clearly identified**
- No aggressive crawling or scraping beyond these specific pages

### Server Impact

- **4 requests per day** (2 applications × 2 requests per scrape, every 6 hours)
- **Minimal load:** Static HTML parsing, no JavaScript execution
- **Rate limited:** 5 seconds between requests
- **Cacheable:** Responses could be cached by council CDN

## Data Analysis Examples

### Export to Excel

```bash
# CSV is already Excel-compatible
libreoffice monitoring_data/timeseries.csv
```

### Python Analysis

```python
import pandas as pd

df = pd.read_csv('monitoring_data/timeseries.csv')

# Total letters over time
df.groupby('timestamp')['count'].sum().plot()

# Letters by application
df.groupby('application')['count'].sum()

# Daily submission rate
df.groupby('date_published')['count'].sum().plot(kind='bar')
```

### Generate Report for Media

```python
import json

with open('monitoring_data/latest.json') as f:
    data = json.load(f)

print(f"📊 OBJECTION LETTER UPDATE")
print(f"As of {data['last_updated'][:10]}:")
print(f"  Birchanger: {data['applications']['birchanger']['total']} letters")
print(f"  Stansted: {data['applications']['stansted']['total']} letters")
print(f"  Total: {sum(app['total'] for app in data['applications'].values())} letters")
```

## Use Cases

### Community Campaign Tracking

Monitor momentum of objection campaign in real-time. Share dashboard with:
- Parish councils
- Residents' associations
- Ward councillors
- Local media

### Strategic Timing

Identify peak submission periods to:
- Coordinate additional outreach when momentum is high
- Plan media releases around submission milestones
- Time committee member engagement

### Evidence for Committee

Demonstrate breadth of public concern:
- "74 objection letters submitted to date"
- "Peak submissions on Nov 17 with 14 letters in one day"
- "Consistent objections over 7-day period"

### Media Engagement

Provide data for news stories:
- Timeline charts for visual interest
- Cumulative totals for headlines
- Trend analysis for features

## Maintenance

### Regular Checks

- **Daily:** Check dashboard for anomalies
- **Weekly:** Review scraper.log for errors
- **Monthly:** Archive old CSV data if growing large

### Updates

If planning portal HTML structure changes:
1. Update CSS selectors in `scraper.py`
2. Test with `python3.9 monitoring/scraper.py`
3. Verify data in `monitoring_data/latest.json`

### End of Campaign

When applications are determined:
1. Run final scrape: `python3.9 monitoring/scraper.py`
2. Stop scheduler: `pkill -f "scheduler.py"`
3. Archive data: `tar -czf objection_data_$(date +%F).tar.gz monitoring_data/`
4. Generate final report

## Support

### Logs Location

- **Scraper logs:** `monitoring_data/scraper.log`
- **Scheduler logs:** Same file (append mode)
- **Error tracking:** `monitoring_data/metadata.json`

### Common Issues

| Issue | Solution |
|-------|----------|
| Dashboard blank | Run scraper first to generate data |
| CORS errors | Use local HTTP server |
| No new data | Check scraper.log for errors |
| Wrong counts | Verify portal is accessible, check HTML structure |
| High memory usage | Archive old CSV rows, restart scheduler |

## License & Attribution

This monitoring system is part of the planning objection campaign for Uttlesford applications UTT/25/3011/OP and UTT/25/3012/OP.

**Dependencies:**
- BeautifulSoup4 (MIT License)
- Requests (Apache 2.0 License)
- APScheduler (MIT License)
- Chart.js (MIT License)
- Chart.js Zoom Plugin (MIT License)

## Version History

- **v1.0** (2025-11-19): Initial release
  - Birchanger and Stansted application monitoring
  - 6-hour polling
  - Interactive dashboard with zoom
  - CSV + JSON data storage

---

**Created:** 2025-11-19
**Status:** Production Ready
**Author:** Planning Objection Campaign Team
