
from urllib.parse import urlparse

def get_base_url(url: str) -> str:
    """
    Extracts the base URL (protocol + domain) from a given URL.

    Args:
        url: The input URL string.

    Returns:
        The base URL string, or an empty string if the input URL is invalid.
    """
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:  # Check for valid scheme and netloc
            raise ValueError("parced_url")  # Or raise an exception if you prefer
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    except Exception:  # Catch any parsing errors
        raise

