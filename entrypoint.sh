#!/bin/bash

# Function to convert lookback period to cron schedule
get_cron_schedule() {
    local period=$1
    local unit=${period: -1}
    local value=${period%?}
    
    case $unit in
        "m") echo "*/$value * * * *" ;;
        "h") echo "0 */$value * * *" ;;
        "d") echo "0 0 */$value * *" ;;
        "w") echo "0 0 * * */$value" ;;
        *) echo "0 * * * *" ;; # Default to hourly if format is invalid
    esac
}

# Get lookback period from config
LOOKBACK_PERIOD=$(grep -oP 'lookback_period:\s*"\K[^"]+' /app/config.yml)

# Convert lookback period to cron schedule
CRON_SCHEDULE=$(get_cron_schedule "$LOOKBACK_PERIOD")

# Create cron job
echo "$CRON_SCHEDULE python /app/main.py" > /etc/cron.d/plex-updates

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/plex-updates

# Apply cron job
crontab /etc/cron.d/plex-updates

# Send initial message
echo "Sending initial message..."
python /app/main.py

# Start cron in foreground
echo "Starting cron with schedule: $CRON_SCHEDULE"
cron -f 