from datetime import datetime

def time_to_seconds(time_str):
    """
    Convert a time string in HH:MM:SS format to seconds from midnight.
    """
    t = datetime.strptime(time_str, "%H:%M:%S")
    return t.hour * 3600 + t.minute * 60 + t.second
