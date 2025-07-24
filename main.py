#!/usr/bin/env python3
"""
External IP Change Notifier

A simple script to monitor external IP address changes and send notifications
via ntfy when changes are detected. Designed to be run via cron.

Usage:
    python main.py                          # Normal operation
    python main.py --test --ip 192.168.1.1 # Test mode with custom IP
    python main.py --health-check-only      # Send health check only
"""

import argparse
import json
import os
import sys
import requests
from datetime import datetime, timedelta
from config import Config


def ensure_logs_directory():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists(Config.LOGS_DIR):
        os.makedirs(Config.LOGS_DIR)


def get_external_ip():
    """Get external IP address from a reliable service"""
    services = [
        'https://httpbin.org/ip',
        'https://api.ipify.org?format=json',
        'https://icanhazip.com'
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=10)
            response.raise_for_status()
            
            if 'httpbin.org' in service:
                return response.json()['origin'].split(',')[0].strip()
            elif 'ipify.org' in service:
                return response.json()['ip']
            else:  # icanhazip.com
                return response.text.strip()
                
        except Exception as e:
            print(f"Failed to get IP from {service}: {e}")
            continue
    
    raise Exception("Failed to get external IP from all services")


def load_last_ip(log_file):
    """Load the most recent IP from the log file"""
    if not os.path.exists(log_file):
        return None
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                # Parse the last line: "2025-07-24 10:30:15 | 192.168.1.1"
                last_line = lines[-1].strip()
                if ' | ' in last_line:
                    return last_line.split(' | ')[1]
    except Exception as e:
        print(f"Error reading log file {log_file}: {e}")
    
    return None


def log_ip_change(ip, log_file, is_change=True):
    """Log IP address with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "CHANGED" if is_change else "CHECKED"
    log_entry = f"{timestamp} | {ip} | {status}\n"
    
    try:
        with open(log_file, 'a') as f:
            f.write(log_entry)
        print(f"Logged: {log_entry.strip()}")
    except Exception as e:
        print(f"Error writing to log file {log_file}: {e}")


def send_notification(title, message, priority="default"):
    """Send notification via ntfy"""
    try:
        url = f"{Config.NTFY_SERVER}/{Config.NTFY_TOPIC}"
        
        headers = {
            'Title': title,
            'Priority': priority,
            'Tags': 'computer,globe_with_meridians',
            'Content-Type': 'text/plain; charset=utf-8'
        }
        
        # Add authentication if configured
        auth = None
        if Config.NTFY_TOKEN:
            # Use Bearer token authentication (recommended)
            headers['Authorization'] = f'Bearer {Config.NTFY_TOKEN}'
        elif Config.NTFY_USERNAME and Config.NTFY_PASSWORD:
            # Use Basic authentication for username/password
            auth = (Config.NTFY_USERNAME, Config.NTFY_PASSWORD)
        
        response = requests.post(
            url,
            data=message.encode('utf-8'),
            headers=headers,
            auth=auth,
            timeout=10
        )
        response.raise_for_status()
        
        print(f"Notification sent: {title}")
        return True
        
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return False


def get_last_health_check_time():
    """Get the timestamp of the last health check"""
    if not os.path.exists(Config.HEALTH_CHECK_FILE):
        return None
    
    try:
        with open(Config.HEALTH_CHECK_FILE, 'r') as f:
            timestamp_str = f.read().strip()
            return datetime.fromisoformat(timestamp_str)
    except Exception as e:
        print(f"Error reading health check file: {e}")
        return None


def update_health_check_time():
    """Update the last health check timestamp"""
    try:
        with open(Config.HEALTH_CHECK_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        print(f"Error updating health check file: {e}")


def should_send_health_check():
    """Check if it's time to send a health check notification"""
    last_health_check = get_last_health_check_time()
    
    if last_health_check is None:
        return True  # First run
    
    time_since_last = datetime.now() - last_health_check
    interval = timedelta(hours=Config.HEALTH_CHECK_INTERVAL_HOURS)
    
    return time_since_last >= interval


def validate_ip_address(ip):
    """Basic IP address validation"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            num = int(part)
            if not 0 <= num <= 255:
                return False
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description='External IP Change Notifier')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--ip', help='Custom IP for test mode')
    parser.add_argument('--health-check-only', action='store_true', 
                       help='Send health check notification only')
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Ensure logs directory exists
    ensure_logs_directory()
    
    # Handle health check only mode
    if args.health_check_only:
        if should_send_health_check():
            message = f"External IP Monitor is running normally.\nLast check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            send_notification("IP Monitor Health Check", message, "low")
            update_health_check_time()
        else:
            print("Health check not due yet")
        return
    
    # Determine mode and log file
    is_test_mode = args.test
    log_file = Config.TEST_IP_LOG_FILE if is_test_mode else Config.IP_LOG_FILE
    
    try:
        # Get current IP
        if is_test_mode:
            if not args.ip:
                print("Error: --ip parameter is required in test mode")
                sys.exit(1)
            
            if not validate_ip_address(args.ip):
                print(f"Error: Invalid IP address format: {args.ip}")
                sys.exit(1)
            
            current_ip = args.ip
            print(f"Test mode: Using IP {current_ip}")
        else:
            current_ip = get_external_ip()
            print(f"Current external IP: {current_ip}")
        
        # Load previous IP
        last_ip = load_last_ip(log_file)
        print(f"Previous IP: {last_ip}")
        
        # Check for changes
        ip_changed = current_ip != last_ip
        
        if ip_changed:
            # IP has changed - log and notify
            log_ip_change(current_ip, log_file, is_change=True)
            
            if last_ip:
                title = "External IP Address Changed"
                message = f"Your external IP address has changed:\n\nPrevious: {last_ip}\nCurrent: {current_ip}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                priority = "default" if not is_test_mode else "low"
            else:
                title = "External IP Monitor Started"
                message = f"IP monitoring has started.\n\nCurrent IP: {current_ip}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                priority = "low"
            
            if is_test_mode:
                title = f"[TEST] {title}"
            
            send_notification(title, message, priority)
        else:
            # IP hasn't changed - just log the check
            log_ip_change(current_ip, log_file, is_change=False)
            print("IP address unchanged")
        
        # Check if health notification is due (only in normal mode)
        if not is_test_mode and should_send_health_check():
            health_message = f"External IP Monitor is running normally.\n\nCurrent IP: {current_ip}\nLast check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            send_notification("IP Monitor Health Check", health_message, "low")
            update_health_check_time()
    
    except Exception as e:
        error_msg = f"Error in IP monitoring: {e}"
        print(error_msg)
        
        # Send error notification (only in normal mode)
        if not is_test_mode:
            send_notification("IP Monitor Error", 
                            f"An error occurred while monitoring IP:\n\n{error_msg}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                            "high")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
