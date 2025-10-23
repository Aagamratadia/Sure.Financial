"""Regex patterns for data extraction"""
import regex as re


# Card issuer detection patterns
ISSUER_PATTERNS = {
    "kotak": [
        r"Kotak\s+Mahindra\s+Bank",
        r"Kotak\s+Corporate\s+Credit\s+Card",
        r"Kotak\s+Credit\s+Card",
        r"Kotak\s+Bank",
        r"Kotak\s+Mahindra",
        r"Kotak",  # Just "Kotak" by itself
        r"GSTIN\s*-?\s*27AAACK4409J3ZI",
        r"kotak\.com",
        r"Corporate\s+Credit\s+Card\s+Statement",  # Common in Kotak statements
        r"414767",  # BIN number for Kotak cards
    ],
    "hdfc": [
        r"HDFC\s+Bank",
        r"Platinum\s+Times\s+Card",
        r"GSTIN\s*33AAACH2702H2Z6",
        r"hdfcbank\.com",
        r"HDFC\s+Credit\s+Card",
    ],
    "icici": [
        r"ICICI\s+Bank",
        r"GSTIN\s*27AAACI1195H3ZK",
        r"icicibank\.com",
        r"ICICI\s+Credit\s+Card",
    ],
    "amex": [
        r"American\s+Express",
        r"AEBC",
        r"americanexpress\.co\.in",
        r"American\s+Express\s+Banking\s+Corp",
    ],
    "capital_one": [
        r"Capital\s+One\s+Europe",
        r"capitalone\.co\.uk",
        r"Capital\s+One",
    ],
    "idfc": [
        r"IDFC\s+First\s+Bank",
        r"IDFC\s+FIRST\s+Bank",
        r"idfcfirstbank\.com",
        r"IDFC\s+Bank",
        r"IDFC\s+FIRST",
    ]
}


# Card number patterns (various masking formats)
CARD_NUMBER_PATTERNS = [
    r"\d{4}\s*\d{2}X{2}\s*X{4}\s*\d{4}",           # 5228 52XX XXXX 0591
    r"\d{6}X{6}\d{4}",                              # 414767XXXXXX6705
    r"\d{4}\s*X{4}\s*X{4}\s*\d{3,4}",              # 3769 XXXX XXXX 000
    r"X{4}-X{6}-\d{5}",                             # XXXX-XXXXXX-01007
    r"\d{4}\s+\d{4}\s+\d{4}\s+\d{4}",              # Full unmasked (rare)
    r"\d{4}\s*\*{4}\s*\*{4}\s*\d{4}",              # With asterisks
    r"\d{6}\*{6}\d{4}",                             # 414767******6705
    r"\d{4}",                                        # Short form (last 4 digits)
]

# Card number context keywords
CARD_NUMBER_KEYWORDS = [
    r"Card\s+Number",
    r"Card\s+No\.?",
    r"Account\s+No\.?",
    r"Card\s+Account\s+No\.?",
    r"Membership\s+Number",
    r"Account\s+Number",
    r"Credit\s+Card\s+No\.?",
]


# Statement period patterns
STATEMENT_PERIOD_PATTERNS = [
    r"Statement\s+Period\s*:?\s*(\d{1,2}-\w{3}-\d{4})\s+(?:To|to)\s+(\d{1,2}-\w{3}-\d{4})",
    r"Statement\s+Date\s*:?\s*(\d{1,2}-\w{3}-\d{4})\s+(?:To|to)\s+(\d{1,2}-\w{3}-\d{4})",
    r"From\s+(\w+\s+\d{1,2})\s+to\s+(\w+\s+\d{1,2},\s+\d{4})",
    r"(\d{8})\s+(?:to|To)\s+(\d{8})",
    r"From\s+(\d{2}\d{2}\d{4})\s+to\s+(\d{2}\d{2}\d{4})",
    r"Billing\s+Cycle\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})",
    r"Period\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})\s+to\s+(\d{1,2}\s+\w+\s+\d{4})",
]

# Statement period keywords
STATEMENT_PERIOD_KEYWORDS = [
    r"Statement\s+Period",
    r"Statement\s+Date",
    r"Billing\s+Cycle",
    r"Billing\s+Period",
]


# Payment due date patterns
DUE_DATE_PATTERNS = [
    r"Payment\s+Due\s+Date\s*:?\s*(\d{1,2}-\w{3}-\d{4})",
    r"Due\s+Date\s*:?\s*(\d{2}\d{2}\d{4})",
    r"Due\s+by\s+(\w+\s+\d{1,2},\s+\d{4})",
    r"Pay\s+by\s+(\d{1,2}\s+\w{3}\s+\d{2,4})",
    r"Payment\s+Date\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})",
    r"Due\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})",
]

# Due date keywords
DUE_DATE_KEYWORDS = [
    r"Payment\s+Due\s+Date",
    r"Due\s+Date",
    r"Payment\s+Date",
    r"Pay\s+By",
    r"Due\s+By",
]


# Total amount due patterns
TOTAL_AMOUNT_PATTERNS = [
    r"Total\s+Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
    r"Total\s+Dues\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
    r"Your\s+Total\s+Amount\s+Due\s*:?\s*([\d,]+\.?\d*)",
    r"New\s+Balance\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
    r"CLOSING\s+BALANCE\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
    r"Total\s+Outstanding\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
    r"Amount\s+Due\s*:?\s*([\d,]+\.?\d*)",
    r"Total\s+Amount\s+Due\s*:?\s*₹\s*([\d,]+\.?\d*)",
    r"Balance\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
]

# Total amount keywords
TOTAL_AMOUNT_KEYWORDS = [
    r"Total\s+Amount\s+Due",
    r"Total\s+Dues",
    r"New\s+Balance",
    r"Closing\s+Balance",
    r"Total\s+Outstanding",
    r"Amount\s+Due",
    r"Your\s+Total\s+Amount\s+Due",
]


def compile_patterns(patterns: list[str]) -> list[re.Pattern]:
    """
    Compile regex patterns for faster matching
    
    Args:
        patterns: List of regex pattern strings
        
    Returns:
        List of compiled regex patterns
    """
    return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]


def search_with_context(text: str, pattern: str, context_chars: int = 100) -> tuple[str, str]:
    """
    Search for pattern and return match with surrounding context
    
    Args:
        text: Text to search
        pattern: Regex pattern
        context_chars: Number of characters to include before/after match
        
    Returns:
        Tuple of (matched_text, context)
    """
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start = max(0, match.start() - context_chars)
        end = min(len(text), match.end() + context_chars)
        context = text[start:end]
        return match.group(0), context
    return "", ""


def find_nearest_value(text: str, keyword_pattern: str, value_pattern: str, max_distance: int = 200) -> str:
    """
    Find value near a keyword
    
    Args:
        text: Text to search
        keyword_pattern: Pattern for keyword (e.g., "Due Date")
        value_pattern: Pattern for value (e.g., date pattern)
        max_distance: Maximum characters between keyword and value
        
    Returns:
        Matched value or empty string
    """
    keyword_match = re.search(keyword_pattern, text, re.IGNORECASE)
    if not keyword_match:
        return ""
    
    # Search in text near the keyword
    search_start = keyword_match.end()
    search_end = min(len(text), search_start + max_distance)
    search_text = text[search_start:search_end]
    
    value_match = re.search(value_pattern, search_text, re.IGNORECASE)
    if value_match:
        return value_match.group(1) if value_match.groups() else value_match.group(0)
    
    return ""
