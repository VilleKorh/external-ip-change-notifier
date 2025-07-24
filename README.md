# External IP Change Notifier

A simple Python script that monitors your external IP address and sends push notifications via [ntfy](https://ntfy.sh) when it changes. Designed to run via cron for reliable monitoring.

## Features

- 🌐 Monitors external IP address changes
- 📱 Push notifications via ntfy when IP changes
- 📊 Logs all IP checks with timestamps
- 🏥 Health check notifications (configurable interval)
- 🧪 Test mode for safe testing
- 🔄 Cron-optimized (single execution)

## Quick Setup

1. **Clone and install:**
   ```bash
   git clone <repo-url> external-ip-change-notifier
   cd external-ip-change-notifier
   ./setup.sh
   ```

2. **Configure notifications:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Test it works:**
   ```bash
   python main.py --test --ip 1.2.3.4
   ```

4. **Set up cron:**
   ```bash
   crontab -e
   # Add: */15 * * * * /path/to/external-ip-change-notifier/run_ip_monitor.sh
   ```

## Configuration

Edit `.env` with your ntfy settings:

```env
# Required: Your unique topic name (acts as a password)
NTFY_TOPIC=my-unique-ip-monitor-2024

# Optional: ntfy server (defaults to https://ntfy.sh)
NTFY_SERVER=https://ntfy.sh

# Optional: Access token for protected topics
NTFY_TOKEN=tk_your_token_here

# Optional: Health check interval in hours (default: 24)
HEALTH_CHECK_INTERVAL_HOURS=24
```

## Getting Notifications

**Mobile/Desktop:**
1. Install the [ntfy app](https://ntfy.sh/app) or visit [ntfy.sh](https://ntfy.sh)
2. Subscribe to your topic name (e.g., `my-unique-ip-monitor-2024`)
3. You'll receive notifications when your IP changes

**Topic Security:** Anyone who knows your topic name can send notifications to it, so choose something unique and hard to guess.

## Usage

```bash
# Normal operation
python main.py

# Test with fake IP
python main.py --test --ip 192.168.1.100

# Send health check
python main.py --health-check-only
```

## Cron Examples

```bash
# Check every 15 minutes (recommended)
*/15 * * * * /path/to/external-ip-change-notifier/run_ip_monitor.sh

# Check every 5 minutes (more frequent)
*/5 * * * * /path/to/external-ip-change-notifier/run_ip_monitor.sh

# Check hourly (less frequent)
0 * * * * /path/to/external-ip-change-notifier/run_ip_monitor.sh
```

## Files Created

- `logs/ip_history.txt` - Normal mode IP changes
- `logs/test_ip_history.txt` - Test mode changes  
- `logs/cron.log` - Cron execution logs
- `logs/last_health_check.txt` - Health check timestamp

## Requirements

- Python 3.6+
- `requests` and `python-dotenv` (installed via `setup.sh`)
- Internet connection
- Cron (for automated monitoring)

## License

Open source - modify and distribute as needed.
