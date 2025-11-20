# Local Cron Job Setup for Objection Scraper

This guide explains how to set up the objection scraper to run automatically on your local machine using cron.

## Why Local Cron?

The Uttlesford planning portal blocks automated access from cloud providers (GitHub Actions, proxies, etc.), but works reliably from residential connections. A local cron job is the most reliable solution.

## Prerequisites

- Your machine must be powered on when cron runs
- Git must be configured with your credentials
- Python 3.9+ installed with required packages

## Quick Setup

### 1. Test the Script First

```bash
cd /path/to/savebirchanger
./Monitoring/run-scraper-cron.sh
```

You should see output like:
```
[2025-11-20 09:36:15] Starting objection scraper cron job
...
✅ B999 representation letters: 38
...
[2025-11-20 09:36:18] ✅ Push successful
[2025-11-20 09:36:18] Cron job completed successfully
```

### 2. Set Up the Cron Job

Open your crontab:
```bash
crontab -e
```

Add this line (replace `/path/to/` with your actual path):
```bash
# Run objection scraper every hour at 5 minutes past the hour
5 * * * * /path/to/savebirchanger/Monitoring/run-scraper-cron.sh >> /path/to/savebirchanger/monitoring_data/cron.log 2>&1
```

**Example with actual path:**
```bash
5 * * * * /home/mike/fixrepo/savebirchanger/Monitoring/run-scraper-cron.sh >> /home/mike/fixrepo/savebirchanger/monitoring_data/cron.log 2>&1
```

Save and exit (usually `Ctrl+X`, then `Y`, then `Enter`).

### 3. Verify Cron Job is Scheduled

```bash
crontab -l
```

You should see your new cron job listed.

## Cron Schedule Examples

```bash
# Every hour at 5 past
5 * * * * /path/to/script

# Every 30 minutes
*/30 * * * * /path/to/script

# Every 2 hours
0 */2 * * * /path/to/script

# Every day at 9 AM
0 9 * * * /path/to/script

# Every Monday at 10 AM
0 10 * * 1 /path/to/script
```

## Monitoring the Cron Job

### Check if it's running:
```bash
# View recent cron logs
tail -f /path/to/savebirchanger/monitoring_data/cron.log

# View scraper-specific logs
tail -f /path/to/savebirchanger/monitoring_data/scraper.log

# Check recent commits
cd /path/to/savebirchanger
git log --oneline -5
```

### Verify on GitHub:
- Go to your repository on GitHub
- Check the "commits" page for automated updates
- Look for commits like: "Update objection data - 2025-11-20 09:36:16"

## Troubleshooting

### Cron job not running?

1. **Check cron service is running:**
   ```bash
   systemctl status cron     # On systemd Linux
   # or
   service cron status        # On older systems
   ```

2. **Check cron logs:**
   ```bash
   grep CRON /var/log/syslog  # Ubuntu/Debian
   # or
   journalctl -u cron         # systemd
   ```

3. **Test manually:**
   ```bash
   cd /path/to/savebirchanger
   ./Monitoring/run-scraper-cron.sh
   ```

### Script fails with permission denied?

```bash
chmod +x /path/to/savebirchanger/Monitoring/run-scraper-cron.sh
```

### Git push fails with authentication error?

Make sure your Git credentials are cached:
```bash
# For HTTPS
git config --global credential.helper store
git push  # Enter credentials once, they'll be saved

# For SSH
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa  # or your SSH key
```

### Python module not found?

The script uses `python3`. Make sure packages are installed:
```bash
cd /path/to/savebirchanger
pip3 install -r Monitoring/requirements_monitoring.txt
```

## Disabling the Cron Job

To temporarily disable:
```bash
crontab -e
# Add # at the start of the line:
# 5 * * * * /path/to/script
```

To permanently remove:
```bash
crontab -e
# Delete the line entirely
```

## Keeping Your Machine On

For reliable cron execution:

### On Linux:
```bash
# Prevent sleep
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### On macOS:
```bash
# Keep awake while plugged in
sudo pmset -c sleep 0
```

### Alternative: Run on a Raspberry Pi
If you don't want your main machine on 24/7, run this on a Raspberry Pi:
1. Install Raspberry Pi OS
2. Clone your repository
3. Set up the cron job
4. Leave it running (uses ~3W of power)

## Cost Comparison

| Method | Cost | Reliability |
|--------|------|-------------|
| **Local Cron** | $0 (or ~$2/month electricity) | ⭐⭐⭐⭐⭐ |
| GitHub Actions | $0 (free tier) | ❌ Blocked |
| Proxies (IPRoyal) | ~$7/month | ❌ Gov domains blocked |
| UK VPS | ~$5/month | ⭐⭐⭐⭐ |
| Raspberry Pi | ~$35 one-time + $2/month power | ⭐⭐⭐⭐⭐ |

## Questions?

If you have issues:
1. Check the logs at `monitoring_data/cron.log`
2. Run the script manually to see errors
3. Check Git credentials are working: `git push`
4. Verify Python packages: `python3 -c "import requests; print('OK')"`
