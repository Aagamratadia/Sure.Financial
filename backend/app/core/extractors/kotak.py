"""Kotak Mahindra Bank extractor"""
import regex as re
from typing import Tuple
from app.core.extractors.base import BaseExtractor
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.date_parser import parse_date, parse_date_range
from app.utils.amount_parser import parse_amount
import logging

logger = logging.getLogger(__name__)


class KotakExtractor(BaseExtractor):
    """Extractor for Kotak Mahindra Bank credit card statements"""
    
    ISSUER_NAME = CardIssuer.KOTAK
    
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """Extract Kotak Mahindra Bank name"""
        patterns = [
            r"Kotak\s+Mahindra\s+Bank",
            r"Kotak\s+Corporate\s+Credit\s+Card",
            r"GSTIN\s*-?\s*27AAACK4409J3ZI",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return self.ISSUER_NAME.value, 1.0
        
        return "", 0.0
    
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """Extract card number - Kotak format: 414767XXXXXX6705 or various formats"""
        # Kotak specific patterns - try multiple variations
        patterns = [
            r"(\d{6}X{6}\d{4})",  # 414767XXXXXX6705
            r"(\d{4}\s*\d{2}X{2}\s*X{4}\s*\d{4})",  # 4147 67XX XXXX 6705
            r"(\d{4}\s+X{4}\s+X{4}\s+\d{4})",  # 4147 XXXX XXXX 6705
            r"Card\s+Number\s*:?\s*(\d{4}[\s\*X]{1,}\d{2}[\s\*X]{1,}[\s\*X]{1,}\d{4})",  # Card Number: variations
            r"(\d{4})[\s\*X]{4,}(\d{4})",  # Last 4 and first 4 with masking in between
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                card_num = match.group(0)
                # Clean up and standardize format
                card_num = re.sub(r'\s+', ' ', card_num).strip()
                logger.info(f"Kotak: Found card number: {card_num}")
                return card_num, 1.0
        
        logger.warning("Kotak: Card number not found")
        return "", 0.0
    
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """Extract statement period - Kotak format: 2-Feb-2023 To 1-Mar-2023"""
        patterns = [
            # OCR often adds underscores, periods, or extra spaces
            r"Statement\s+Period\s*[_:\s.]*(\d{1,2}-\w{3}-\d{4})\s*[.\s]*[Tt]o\s+(\d{1,2}-\w{3}-\d{4})",
            r"Statement\s+(?:Date|Period)\s*[_:\s.]*(\d{1,2}[/-]\w{3}[/-]\d{4})\s*[.\s]*[Tt]o\s+(\d{1,2}[/-]\w{3}[/-]\d{4})",
            r"Billing\s+Period\s*[_:\s.]*(\d{1,2}[/-]\w{3}[/-]\d{4})\s*[.\s]*[Tt]o\s+(\d{1,2}[/-]\w{3}[/-]\d{4})",
            r"From\s+(\d{1,2}[/-]\w{3}[/-]\d{4})\s*[.\s]*[Tt]o\s+(\d{1,2}[/-]\w{3}[/-]\d{4})",
            r"(\d{1,2}[/-]\w{3}[/-]\d{4})\s*[.\s]*[Tt]o\s+(\d{1,2}[/-]\w{3}[/-]\d{4})",  # Generic date range
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_raw, end_raw = match.groups()
                start_date = parse_date(start_raw)
                end_date = parse_date(end_raw)
                
                if start_date and end_date:
                    field = DateRangeField(
                        raw=f"{start_raw} To {end_raw}",
                        start_date=start_date,
                        end_date=end_date
                    )
                    logger.info(f"Kotak: Found statement period: {start_date} to {end_date}")
                    return field, 1.0
        
        # Try alternative pattern using generic parser
        start_date, end_date = parse_date_range(text)
        if start_date and end_date:
            field = DateRangeField(
                raw="Parsed from text",
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"Kotak: Parsed statement period: {start_date} to {end_date}")
            return field, 0.7
        
        logger.warning("Kotak: Statement period not found")
        return DateRangeField(raw=""), 0.0
    
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """Extract payment due date - Kotak format: 19-Mar-2023"""
        patterns = [
            r"Payment\s+Due\s+Date\s*:?\s*(\d{1,2}[/-]\w{3}[/-]\d{4})",
            r"Due\s+Date\s*:?\s*(\d{1,2}[/-]\w{3}[/-]\d{4})",
            r"Pay\s+by\s*:?\s*(\d{1,2}[/-]\w{3}[/-]\d{4})",
            r"Payment\s+Due\s*:?\s*(\d{1,2}[/-]\w{3}[/-]\d{4})",
            r"Due\s+on\s*:?\s*(\d{1,2}[/-]\w{3}[/-]\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_raw = match.group(1)
                date_formatted = parse_date(date_raw)
                
                if date_formatted:
                    field = DateField(
                        raw=date_raw,
                        formatted=date_formatted
                    )
                    logger.info(f"Kotak: Found due date: {date_formatted}")
                    return field, 1.0
        
        logger.warning("Kotak: Due date not found")
        return DateField(raw=""), 0.0
    
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """Extract total amount due - Kotak format: Rs. 478,387.66"""
        patterns = [
            # OCR may add parentheses around Rs. like (Rs.)
            r"Total\s+Amount\s+Due\s*\(Rs\.\)\s*([\d,]+\.?\d*)",  # Match "(Rs.)" format
            r"Total\s+Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Total\s+Dues\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Your\s+Total\s+Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Total\s+Outstanding\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Balance\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"(?:Rs\.|INR|₹)\s*([\d,]+\.?\d*)",  # Generic amount with currency symbol
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_raw = match.group(0)
                amount, currency = parse_amount(amount_raw)
                
                if amount is not None and amount > 0:
                    field = AmountField(
                        raw=amount_raw,
                        amount=amount,
                        currency=currency
                    )
                    logger.info(f"Kotak: Found amount: {currency} {amount}")
                    return field, 1.0
        
        logger.warning("Kotak: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="INR"), 0.0
