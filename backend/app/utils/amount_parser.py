"""Amount parsing utilities"""
import regex as re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# Currency symbols and codes
CURRENCY_PATTERNS = {
    "INR": [r"Rs\.?", r"₹", r"INR", r"rupees?"],
    "USD": [r"\$", r"USD", r"dollars?"],
    "GBP": [r"£", r"GBP", r"pounds?"],
    "EUR": [r"€", r"EUR", r"euros?"],
}


def parse_amount(amount_string: str, default_currency: str = "INR") -> Tuple[Optional[float], str]:
    """
    Parse amount string and extract numeric value and currency
    
    Args:
        amount_string: Raw amount string from PDF (e.g., "Rs. 45,240.00")
        default_currency: Default currency if not detected
        
    Returns:
        Tuple of (amount as float, currency code)
    """
    if not amount_string or not amount_string.strip():
        return None, default_currency
    
    original = amount_string
    amount_string = amount_string.strip()
    
    # Detect currency
    currency = detect_currency(amount_string) or default_currency
    
    # Remove currency symbols and codes
    for curr_code, patterns in CURRENCY_PATTERNS.items():
        for pattern in patterns:
            amount_string = re.sub(pattern, "", amount_string, flags=re.IGNORECASE)
    
    # Remove whitespace
    amount_string = amount_string.strip()
    
    # Remove common text like "Cr", "Dr", parentheses
    amount_string = re.sub(r"\(|\)|Cr\.?|Dr\.?", "", amount_string, flags=re.IGNORECASE)
    amount_string = amount_string.strip()
    
    # Extract number (handle commas, periods)
    # Pattern: optional minus, digits with commas, optional decimal point and digits
    number_pattern = r"-?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?"
    match = re.search(number_pattern, amount_string)
    
    if not match:
        # Try alternative format: decimal comma (European style)
        number_pattern = r"-?\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?"
        match = re.search(number_pattern, amount_string)
        
        if match:
            # Convert European format to standard
            amount_str = match.group(0)
            amount_str = amount_str.replace(".", "").replace(",", ".")
            try:
                amount = float(amount_str)
                return amount, currency
            except ValueError:
                pass
    
    if match:
        amount_str = match.group(0)
        # Remove commas
        amount_str = amount_str.replace(",", "")
        
        try:
            amount = float(amount_str)
            return amount, currency
        except ValueError as e:
            logger.warning(f"Failed to convert '{amount_str}' to float: {e}")
            return None, currency
    
    logger.warning(f"No valid amount found in '{original}'")
    return None, currency


def detect_currency(text: str) -> Optional[str]:
    """
    Detect currency from text
    
    Args:
        text: Text containing currency symbol or code
        
    Returns:
        Currency code or None
    """
    for currency_code, patterns in CURRENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return currency_code
    
    return None


def format_amount(amount: float, currency: str = "INR") -> str:
    """
    Format amount with currency symbol
    
    Args:
        amount: Numeric amount
        currency: Currency code
        
    Returns:
        Formatted string (e.g., "₹45,240.00")
    """
    # Format with commas
    formatted = f"{amount:,.2f}"
    
    # Add currency symbol
    symbols = {
        "INR": "₹",
        "USD": "$",
        "GBP": "£",
        "EUR": "€"
    }
    
    symbol = symbols.get(currency, currency)
    return f"{symbol}{formatted}"


def validate_amount(amount: float, min_value: float = 0.01, max_value: float = 10_000_000) -> bool:
    """
    Validate that amount is reasonable
    
    Args:
        amount: Amount to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        True if valid, False otherwise
    """
    if amount is None:
        return False
    
    if amount < min_value:
        logger.warning(f"Amount {amount} below minimum {min_value}")
        return False
    
    if amount > max_value:
        logger.warning(f"Amount {amount} exceeds maximum {max_value}")
        return False
    
    return True
