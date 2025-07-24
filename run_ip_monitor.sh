#!/bin/bash
#
# Wrapper script for running the IP monitor via cron
# This provides better error handling and logging for cron jobs
#

# Set script directory
SCRIPT_DIR="/Users/villekorhonen/projects/external-ip-change-notifier"

# Change to script directory
cd "$SCRIPT_DIR" || {
    echo "$(date): ERROR: Cannot change to directory $SCRIPT_DIR" >&2
    exit 1
}

# Activate virtual environment
source venv/bin/activate || {
    echo "$(date): ERROR: Cannot activate virtual environment" >&2
    exit 1
}

# Ensure logs directory exists
mkdir -p logs

# Log start time
echo "$(date): Starting IP monitor" >> logs/cron.log

# Run the script and capture exit code
python main.py >> logs/cron.log 2>&1
exit_code=$?

# Log completion with exit code
echo "$(date): IP monitor completed with exit code $exit_code" >> logs/cron.log

# If there was an error, also log to stderr for cron to potentially email
if [ $exit_code -ne 0 ]; then
    echo "$(date): IP monitor failed with exit code $exit_code" >&2
fi

exit $exit_code
