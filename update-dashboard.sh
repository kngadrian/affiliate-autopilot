#!/bin/bash
#
# Affiliate Autopilot Dashboard Update Script
# Runs the MunchEye scraper and maintains logs with rotation
#

# Configuration
PROJECT_DIR="/root/.openclaw/workspace/affiliate-autopilot"
SCRAPER_SCRIPT="$PROJECT_DIR/scraper.py"
OUTPUT_FILE="$PROJECT_DIR/launches_data.json"
LOG_FILE="$PROJECT_DIR/scraper.log"
LOG_RETENTION_DAYS=7

# Ensure we're in the project directory
cd "$PROJECT_DIR" || {
    echo "[ERROR] $(date -u +"%Y-%m-%d %H:%M:%S UTC") - Failed to change to project directory: $PROJECT_DIR" | tee -a "$LOG_FILE"
    exit 1
}

# Log rotation - keep last 7 days
rotate_logs() {
    if [ -f "$LOG_FILE" ]; then
        # Archive old log with timestamp
        local archive_date=$(date -u +"%Y%m%d_%H%M%S")
        cp "$LOG_FILE" "${LOG_FILE}.${archive_date}"
        
        # Keep only last 7 days of archived logs
        find "$PROJECT_DIR" -name "scraper.log.*" -type f -mtime +${LOG_RETENTION_DAYS} -delete
        
        # Truncate current log if it's too large (>10MB)
        local log_size=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
        if [ "$log_size" -gt 10485760 ]; then
            tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp"
            mv "${LOG_FILE}.tmp" "$LOG_FILE"
        fi
    fi
}

# Send alert (can be extended to email, Slack, etc.)
send_alert() {
    local message="$1"
    echo "[ALERT] $message" | tee -a "$LOG_FILE"
    # TODO: Add email/notification service integration here
    # Example: echo "$message" | mail -s "Affiliate Autopilot Alert" admin@example.com
}

# Main execution
echo "========================================" | tee -a "$LOG_FILE"
echo "[START] $(date -u +"%Y-%m-%d %H:%M:%S UTC") - Running Affiliate Autopilot scraper" | tee -a "$LOG_FILE"

# Check if scraper exists
if [ ! -f "$SCRAPER_SCRIPT" ]; then
    send_alert "Scraper script not found: $SCRAPER_SCRIPT"
    exit 1
fi

# Make sure Python3 is available
if ! command -v python3 &> /dev/null; then
    send_alert "Python3 is not installed or not in PATH"
    exit 1
fi

# Run the scraper and capture output
SCRAPER_OUTPUT=$(python3 "$SCRAPER_SCRIPT" 2>&1)
SCRAPER_EXIT_CODE=$?

# Check exit code
if [ $SCRAPER_EXIT_CODE -eq 0 ]; then
    # Success - count launches and log
    if [ -f "$OUTPUT_FILE" ]; then
        # Count launches in JSON file
        LAUNCH_COUNT=$(python3 -c "import json; data=json.load(open('$OUTPUT_FILE')); print(len(data) if isinstance(data, list) else len(data.get('launches', [])))" 2>/dev/null || echo "unknown")
        
        echo "[SUCCESS] $(date -u +"%Y-%m-%d %H:%M:%S UTC") - Scraper completed successfully" | tee -a "$LOG_FILE"
        echo "[INFO] Launch count: $LAUNCH_COUNT" | tee -a "$LOG_FILE"
        echo "[INFO] Output file: $OUTPUT_FILE" | tee -a "$LOG_FILE"
        
        # Rotate logs after successful run
        rotate_logs
        
        exit 0
    else
        send_alert "Scraper completed but output file not found: $OUTPUT_FILE"
        echo "$SCRAPER_OUTPUT" >> "$LOG_FILE"
        exit 1
    fi
else
    # Failure - log error and send alert
    echo "[ERROR] $(date -u +"%Y-%m-%d %H:%M:%S UTC") - Scraper failed with exit code $SCRAPER_EXIT_CODE" | tee -a "$LOG_FILE"
    echo "[ERROR] Scraper output:" >> "$LOG_FILE"
    echo "$SCRAPER_OUTPUT" >> "$LOG_FILE"
    
    send_alert "Scraper failed with exit code $SCRAPER_EXIT_CODE. Check $LOG_FILE for details."
    
    exit $SCRAPER_EXIT_CODE
fi
