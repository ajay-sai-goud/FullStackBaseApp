import datetime

def format_timestamp_to_iso(timestamp: datetime.datetime) -> str:
    """
    A simple utility function to format a datetime object into an ISO 8601 string.
    
    This is a stateless, reusable helper that can be used anywhere in the application.
    For example:
        `formatted_time = format_timestamp_to_iso(datetime.datetime.now())`
    """
    return timestamp.isoformat()
