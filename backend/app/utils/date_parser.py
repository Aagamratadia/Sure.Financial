"""Date parsing utilities"""
from datetime import datetime
from dateutil import parser as date_parser
from typing import Optional
import regex as re
import logging

logger = logging.getLogger(__name__)


# Common date formats in credit card statements
DATE_FORMATS = [
    "%d-%b-%Y",      # 1-Mar-2023
    "%d%m%Y",        # 08062019
    "%B %d, %Y",     # January 14, 2024
    "%d/%m/%Y",      # 01/03/2023
    "%Y-%m-%d",      # 2023-03-01
    "%d %B %Y",      # 1 March 2023
    "%d %b %Y",      # 1 Mar 2023
    "%d %b %y",      # 31 Oct 24
    "%d-%m-%Y",      # 01-03-2023
    "%d.%m.%Y",      # 01.03.2023
]


def parse_date(date_string: str) -> Optional[str]:
    """
    Parse date string and return in ISO 8601 format (YYYY-MM-DD)
    
    Args:
        date_string: Raw date string from PDF
        
    Returns:
        ISO 8601 formatted date string or None if parsing fails
    """
    if not date_string or not date_string.strip():
        return None
    
    date_string = date_string.strip()
    
    # Try each format
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_string, fmt)
            
            # Handle 2-digit years
            if dt.year < 100:
                # Assume 20XX for years < 50, 19XX for years >= 50
                if dt.year < 50:
                    dt = dt.replace(year=2000 + dt.year)
                else:
                    dt = dt.replace(year=1900 + dt.year)
            
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Try dateutil parser as fallback (flexible parsing)
    try:
        dt = date_parser.parse(date_string, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception as e:
        logger.warning(f"Failed to parse date '{date_string}': {e}")
        return None


def parse_date_range(text: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse date range from text
    
    Args:
        text: Text containing date range (e.g., "From 01-Jan-2023 To 31-Jan-2023")
        
    Returns:
        Tuple of (start_date, end_date) in ISO 8601 format
    """
    # Try to find two dates
    date_patterns = [
        r"(\d{1,2}-\w{3}-\d{4})\s+(?:To|to)\s+(\d{1,2}-\w{3}-\d{4})",
        r"(\d{8})\s+(?:to|To)\s+(\d{8})",
        r"From\s+(\d{2}\d{2}\d{4})\s+to\s+(\d{2}\d{2}\d{4})",
        r"From\s+(\w+\s+\d{1,2})\s+to\s+(\w+\s+\d{1,2},\s+\d{4})",
        r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})",
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start_raw, end_raw = match.groups()
            start_date = parse_date(start_raw)
            end_date = parse_date(end_raw)
            
            if start_date and end_date:
                return start_date, end_date
    
    return None, None


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate that date range is reasonable
    
    Args:
        start_date: Start date in ISO format
        end_date: End date in ISO format
        
    Returns:
        True if valid, False otherwise
    """
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Start must be before end
        if start >= end:
            return False
        
        # Typical billing cycle is 28-31 days
        days_diff = (end - start).days
        if days_diff < 20 or days_diff > 40:
            logger.warning(f"Unusual date range: {days_diff} days")
            # Still return True, just log warning
        
        return True
    except Exception:
        return False


def is_future_date(date_string: str, tolerance_days: int = 90) -> bool:
    """
    Check if date is in the future (within tolerance)
    
    Args:
        date_string: Date in ISO format
        tolerance_days: Number of days into future allowed
        
    Returns:
        True if date is reasonably in future
    """
    try:
        date = datetime.fromisoformat(date_string)
        now = datetime.now()
        days_diff = (date - now).days
        
        return 0 <= days_diff <= tolerance_days
    except Exception:
        return False
