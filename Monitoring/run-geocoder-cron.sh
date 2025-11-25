#!/bin/bash
#
# Save Birchanger Geocoder - Cron Job Wrapper
# This script runs the geocoder to convert addresses to coordinates
#
# Usage: Add to crontab with:
#   10 * * * * /path/to/savebirchanger/Monitoring/run-geocoder-cron.sh >> /path/to/geocoder-cron.log 2>&1

# Exit on error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GEOCODER_DIR="$SCRIPT_DIR/monitoring"

# Log file location (relative to project root)
LOG_FILE="$PROJECT_DIR/monitoring_data/geocoder.log"

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Starting geocoder cron job"
log "Project directory: $PROJECT_DIR"
log "=========================================="

# Change to project directory
cd "$PROJECT_DIR" || {
    log "ERROR: Could not change to project directory"
    exit 1
}

# Run the geocoder
log "Running geocoder with --retry-failed..."
cd "$GEOCODER_DIR" || {
    log "ERROR: Could not change to geocoder directory"
    exit 1
}

if python3.9 geocoder.py --retry-failed; then
    log "✅ Geocoder completed successfully"
else
    log "❌ Geocoder failed with exit code $?"
    exit 1
fi

# Change back to project root for git operations
cd "$PROJECT_DIR" || exit 1

# Check if there are changes to commit
if git diff --quiet monitoring_data/letters.json; then
    log "No changes to commit"
else
    log "Changes detected in letters.json, committing..."

    # Configure git (in case not already configured)
    git config user.name "Cron Geocoder" 2>/dev/null || true
    git config user.email "geocoder@local" 2>/dev/null || true

    # Add changes
    git add monitoring_data/letters.json

    # Commit with timestamp
    COMMIT_MSG="Update geocoding data - $(date +'%Y-%m-%d %H:%M:%S')"
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
