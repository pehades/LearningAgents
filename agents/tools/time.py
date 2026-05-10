from datetime import datetime


def get_current_local_time() -> datetime:
    """
    Returns the local datetime .now() when it is called
    """
    return datetime.now().astimezone()
