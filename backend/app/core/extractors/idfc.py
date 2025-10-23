"""IDFC First Bank extractor"""
import regex as re
from typing import Tuple
from app.core.extractors.base import BaseExtractor
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.date_parser import parse_date, parse_date_range
from app.utils.amount_parser import parse_amount
import logging

logger = logging.getLogger(__name__)


class IDFCExtractor(BaseExtractor):
    """Extractor for IDFC First Bank credit card statements"""
    
    ISSUER_NAME = CardIssuer.IDFC
    
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """Extract IDFC First Bank name"""
        patterns = [
            r"IDFC\s+First\s+Bank",
            r"IDFC\s+FIRST\s+Bank",
            r"idfcfirstbank\.com",
            r"IDFC\s+Bank",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.info(f"IDFC: Found issuer: {self.ISSUER_NAME.value}")
                return self.ISSUER_NAME.value, 1.0
        
        return "", 0.0
    
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """Extract card number - IDFC format: varies (XX7853, XXXX XXXX XXXX 1234)"""
        patterns = [
            # Full format
            r"Card\s+(?:No|Number)\s*\.?\s*:?\s*([X*\d]{4}\s*[X*\d]{4}\s*[X*\d]{4}\s*\d{4})",
            r"(\d{4}\s*X{4}\s*X{4}\s*\d{4})",
            r"(\d{4}\s*\*{4}\s*\*{4}\s*\d{4})",
            r"(\d{4}[\s\-]X{4}[\s\-]X{4}[\s\-]\d{4})",
            # Short format (just last digits)
            r"Card\s+(?:No|Number)\s*\.?\s*:?\s*([X*]{2,6}\d{4})",
            r"Card\s+(?:No|Number)\s*\.?\s*:?\s*(XX\d{4,6})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                card_num = match.group(1).strip()
                # Normalize spacing
                card_num = ' '.join(card_num.split())
                logger.info(f"IDFC: Found card number: {card_num}")
                return card_num, 0.9
        
        logger.warning("IDFC: Card number not found")
        return "", 0.0
    
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """Extract statement period - IDFC format: 20/May/2025 - 19/Jun/2025"""
        patterns = [
            # Mixed format: DD/Mon/YYYY - DD/Mon/YYYY
            r"(\d{1,2}/\w{3}/\d{4})\s*-\s*(\d{1,2}/\w{3}/\d{4})",
            # Standard formats
            r"Statement\s+Period\s*:?\s*.{0,100}?(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:to|To|-)\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Statement\s+Date\s*:?\s*.{0,100}?(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:to|To|-)\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Statement\s+for\s+period\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:to|To|-)\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            r"From\s+(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:to|To)\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            # DD-Mon-YYYY format
            r"(\d{1,2}-\w{3}-\d{4})\s*(?:to|To|-)\s*(\d{1,2}-\w{3}-\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    start_raw, end_raw = groups[0], groups[1]
                    start_date = parse_date(start_raw)
                    end_date = parse_date(end_raw)
                    
                    if start_date and end_date:
                        field = DateRangeField(
                            raw=f"{start_raw} to {end_raw}",
                            start_date=start_date,
                            end_date=end_date
                        )
                        logger.info(f"IDFC: Found statement period: {start_date} to {end_date}")
                        return field, 0.95
        
        # Single date patterns
        single_patterns = [
            r"Statement\s+Date\s*:?\s*.{0,100}?(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Statement\s+Date\s*:?\s*.{0,100}?(\d{1,2}/\w{3}/\d{4})",
        ]
        
        for pattern in single_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                date_raw = match.group(1)
                end_date = parse_date(date_raw)
                if end_date:
                    field = DateRangeField(
                        raw=f"Statement Date {date_raw}",
                        start_date="",
                        end_date=end_date
                    )
                    logger.info(f"IDFC: Found statement date: {end_date}")
                    return field, 0.8
        
        # Fallback
        start_date, end_date = parse_date_range(text)
        if start_date and end_date:
            field = DateRangeField(
                raw="Parsed from text",
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"IDFC: Parsed statement period: {start_date} to {end_date}")
            return field, 0.7
        
        logger.warning("IDFC: Statement period not found")
        return DateRangeField(raw=""), 0.0
    
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """Extract payment due date - IDFC format: 04/Jul/2025"""
        patterns = [
            # DD/Mon/YYYY format
            r"Payment\s+Due\s+Date\s*:?\s*.{0,100}?(\d{1,2}/\w{3}/\d{4})",
            r"Due\s+Date\s*:?\s*.{0,100}?(\d{1,2}/\w{3}/\d{4})",
            # DD-Mon-YYYY format
            r"Payment\s+Due\s+Date\s*:?\s*.{0,100}?(\d{1,2}-\w{3}-\d{4})",
            r"Due\s+Date\s*:?\s*.{0,100}?(\d{1,2}-\w{3}-\d{4})",
            # Standard DD/MM/YYYY format
            r"Payment\s+Due\s+Date\s*:?\s*.{0,100}?(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Due\s+Date\s*:?\s*.{0,100}?(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Pay\s+by\s*:?\s*.{0,100}?(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Payment\s+due\s+on\s*:?\s*.{0,100}?(\d{2}[/-]\d{2}[/-]\d{4})",
            # Generic pattern - look for date after "due"
            r"Due\s+(?:Date|on)\s*.{0,50}?(\d{1,2}[/-]\w{3}[/-]\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                date_raw = match.group(1)
                date_formatted = parse_date(date_raw)
                
                if date_formatted:
                    field = DateField(
                        raw=date_raw,
                        formatted=date_formatted
                    )
                    logger.info(f"IDFC: Found due date: {date_formatted}")
                    return field, 0.95
        
        logger.warning("IDFC: Due date not found")
        return DateField(raw=""), 0.0
    
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """Extract total amount due - IDFC format: varies"""
        patterns = [
            # IDFC common patterns
            r"Total\s+Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Total\s+Outstanding\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"New\s+Balance\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Closing\s+Balance\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            # Without currency symbol
            r"Total\s+Amount\s+Due.{0,100}?([\d,]+\.?\d*)",
            r"Amount\s+Due.{0,50}?([\d,]+\.?\d*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                amount_raw = match.group(1)
                # Clean and parse the amount
                amount_str = amount_raw.replace(',', '')
                try:
                    amount = float(amount_str)
                    if amount > 0:
                        field = AmountField(
                            raw=amount_raw,
                            amount=amount,
                            currency="INR"
                        )
                        logger.info(f"IDFC: Found amount: INR {amount}")
                        return field, 1.0
                except ValueError:
                    continue
        
        logger.warning("IDFC: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="INR"), 0.0
