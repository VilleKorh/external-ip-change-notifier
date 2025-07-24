import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # ntfy configuration
    NTFY_TOPIC = os.getenv('NTFY_TOPIC')
    NTFY_SERVER = os.getenv('NTFY_SERVER', 'https://ntfy.sh')
    NTFY_USERNAME = os.getenv('NTFY_USERNAME')
    NTFY_PASSWORD = os.getenv('NTFY_PASSWORD')
    NTFY_TOKEN = os.getenv('NTFY_TOKEN')
    
    # Health check interval
    HEALTH_CHECK_INTERVAL_HOURS = int(os.getenv('HEALTH_CHECK_INTERVAL_HOURS', 24))
    
    # File paths
    LOGS_DIR = 'logs'
    IP_LOG_FILE = os.path.join(LOGS_DIR, 'ip_history.txt')
    TEST_IP_LOG_FILE = os.path.join(LOGS_DIR, 'test_ip_history.txt')
    HEALTH_CHECK_FILE = os.path.join(LOGS_DIR, 'last_health_check.txt')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.NTFY_TOPIC:
            raise ValueError("NTFY_TOPIC is required in .env file")
        
        if not cls.NTFY_TOKEN and not (cls.NTFY_USERNAME and cls.NTFY_PASSWORD):
            print("Warning: No ntfy authentication configured. Notifications may fail if topic requires auth.")
            print("         For public topics, no authentication is needed.")
            print("         For protected topics, set either NTFY_TOKEN or NTFY_USERNAME/NTFY_PASSWORD.")
