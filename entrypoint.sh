#!/bin/sh

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Generate timestamped log file
LOGFILE="/app/logs/$(date +"%Y%m%d_%H%M%S").log"

echo "Logging to $LOGFILE"
echo "Running: python main.py $SHOP_NAME $PROFILE_ID $NUMPAGE"

# Execute script with logging
python main.py "$SHOP_NAME" "$PROFILE_ID" "$NUMPAGE" >> "$LOGFILE" 2>&1