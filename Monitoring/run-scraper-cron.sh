#!/bin/bash
#
# Save Birchanger Objection Scraper - Cron Job Wrapper
# This script runs the objection scraper and commits/pushes changes
#
# Usage: Add to crontab with:
#   5 * * * * /path/to/savebirchanger/Monitoring/run-scraper-cron.sh >> /path/to/scraper.log 2>&1

# Exit on error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRAPER_DIR="$SCRIPT_DIR/monitoring"

# Log file location (relative to project root)
LOG_FILE="$PROJECT_DIR/monitoring_data/scraper.log"

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Starting objection scraper cron job"
log "Project directory: $PROJECT_DIR"
log "=========================================="

# Change to project directory
cd "$PROJECT_DIR" || {
    log "ERROR: Could not change to project directory"
    exit 1
}

# Run the scraper
log "Running scraper..."
cd "$SCRAPER_DIR" || {
    log "ERROR: Could not change to scraper directory"
    exit 1
}

if python3 scraper.py; then
    log "✅ Scraper completed successfully"
else
    log "❌ Scraper failed with exit code $?"
    exit 1
fi

# Change back to project root for git operations
cd "$PROJECT_DIR" || exit 1

# Check if there are changes to commit
if git diff --quiet monitoring_data/; then
    log "No changes to commit"
else
    log "Changes detected, committing..."

    # Configure git (in case not already configured)
    git config user.name "Cron Scraper" 2>/dev/null || true
    git config user.email "scraper@local" 2>/dev/null || true

    # Add changes
    git add monitoring_data/

    # Commit with timestamp
    COMMIT_MSG="Update objection data - $(date +'%Y-%m-%d %H:%M:%S')"
    if git commit -m "$COMMIT_MSG"; then
        log "✅ Committed: $COMMIT_MSG"

        # Pull and push
        log "Pulling latest changes..."
        if git pull --rebase origin main; then
            log "✅ Pull successful"
        else
            log "⚠️  Pull failed, attempting to continue"
        fi

        log "Pushing changes..."
        if git push origin main; then
            log "✅ Push successful"
        else
            log "❌ Push failed"
            exit 1
        fi
    else
        log "❌ Commit failed"
        exit 1
    fi
fi

log "=========================================="
log "Cron job completed successfully"
log "=========================================="
