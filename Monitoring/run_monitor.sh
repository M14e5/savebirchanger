#!/bin/bash
# Start Planning Objection Monitor in background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEDULER="$SCRIPT_DIR/monitoring/scheduler.py"
PID_FILE="$SCRIPT_DIR/monitoring_data/monitor.pid"
LOG_FILE="$SCRIPT_DIR/monitoring_data/scraper.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ Monitor is already running (PID: $PID)"
        echo "   To stop: kill $PID"
        echo "   Or: pkill -f 'scheduler.py'"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

echo "🚀 Starting Planning Objection Monitor..."
echo "   Log file: $LOG_FILE"
echo "   PID file: $PID_FILE"

# Start scheduler in background
nohup python3.9 "$SCHEDULER" >> "$LOG_FILE" 2>&1 &
MONITOR_PID=$!

# Save PID
echo "$MONITOR_PID" > "$PID_FILE"

echo "✅ Monitor started successfully (PID: $MONITOR_PID)"
echo ""
echo "Commands:"
echo "  View logs:  tail -f $LOG_FILE"
echo "  Stop:       kill $MONITOR_PID"
echo "  Or:         pkill -f 'scheduler.py'"
echo "  Dashboard:  firefox monitoring/dashboard.html"
echo ""
