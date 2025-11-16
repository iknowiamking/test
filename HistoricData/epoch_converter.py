from datetime import datetime
import time

def date_to_epoch(date_string):
    """Convert date string (YYYY-MM-DD) to epoch timestamp"""
    dt = datetime.strptime(date_string, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()))

def epoch_to_date(epoch_timestamp):
    """Convert epoch timestamp to date string"""
    return datetime.fromtimestamp(int(epoch_timestamp)).strftime("%Y-%m-%d")

def current_epoch():
    """Get current epoch timestamp"""
    return int(time.time())