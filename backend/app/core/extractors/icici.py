"""ICICI Bank extractor"""
import regex as re
from typing import Tuple
from app.core.extractors.base import BaseExtractor
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.date_parser import parse_date, parse_date_range
from app.utils.amount_parser import parse_amount
import logging

logger = logging.getLogger(__name__)


class ICICIExtractor(BaseExtractor):
    """Extractor for ICICI Bank credit card statements"""
    
    ISSUER_NAME = CardIssuer.ICICI
    
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """Extract ICICI Bank name"""
        patterns = [
            r"ICICI\s+Bank",
            r"GSTIN\s*27AAACI1195H3ZK",
            r"icicibank\.com",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return self.ISSUER_NAME.value, 1.0
        
        return "", 0.0
    
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """Extract card number - ICICI format varies"""
        patterns = [
            r"(\d{4}\s*X{4}\s*X{4}\s*\d{4})",
            r"(\d{6}X{6}\d{4})",
            r"Card\s+No\.?\s*:?\s*(\d{4}[\sX*]{4,}[\sX*]{4,}\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                card_num = match.group(1) if match.lastindex else match.group(0)
                card_num = ' '.join(card_num.split())
                return card_num, 1.0
        
        logger.warning("ICICI: Card number not found")
        return "", 0.0
    
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """Extract statement period - ICICI format: Statement Date 23/04/2019"""
        patterns = [
            # ICICI shows "Statement Date" followed by date
            r"Statement\s+Date.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Statement\s+Period\s*:?\s*(\d{1,2}-\w{3}-\d{4})\s+(?:To|to)\s+(\d{1,2}-\w{3}-\d{4})",
            r"From\s+(\d{2}\d{2}\d{4})\s+to\s+(\d{2}\d{2}\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    # Single statement date - use as end date
                    date_raw = groups[0]
                    end_date = parse_date(date_raw)
                    if end_date:
                        field = DateRangeField(
                            raw=f"Statement Date {date_raw}",
                            start_date="",
                            end_date=end_date
                        )
                        logger.info(f"ICICI: Found statement date: {end_date}")
                        return field, 0.8
                else:
                    start_raw, end_raw = groups
                    start_date = parse_date(start_raw)
                    end_date = parse_date(end_raw)
                    
                    if start_date and end_date:
                        field = DateRangeField(
                            raw=f"{start_raw} to {end_raw}",
                            start_date=start_date,
                            end_date=end_date
                        )
                        logger.info(f"ICICI: Found statement period: {start_date} to {end_date}")
                        return field, 1.0
        
        # Fallback
        start_date, end_date = parse_date_range(text)
        if start_date and end_date:
            field = DateRangeField(
                raw="Parsed from text",
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"ICICI: Parsed statement period: {start_date} to {end_date}")
            return field, 0.7
        
        logger.warning("ICICI: Statement period not found")
        return DateRangeField(raw=""), 0.0
    
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """Extract payment due date - ICICI format: Due Date: 12/06/2019"""
        patterns = [
            # ICICI shows "Due Date:" with colon followed by DD/MM/YYYY
            r"Due\s+Date\s*:\s*(\d{2}/\d{2}/\d{4})",
            r"Payment\s+Due\s+Date\s*:?\s*(\d{1,2}-\w{3}-\d{4})",
            r"Due\s+Date\s*:?\s*(\d{8})",
            r"Pay\s+by\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})",
            # Generic pattern - look for date after "due date"
            r"Due\s+Date.{0,50}?(\d{2}/\d{2}/\d{4})",
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
                    logger.info(f"ICICI: Found due date: {date_formatted}")
                    return field, 1.0
        
        logger.warning("ICICI: Due date not found")
        return DateField(raw=""), 0.0
    
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """Extract total amount due - ICICI format: Your Total Amount Due 5,882.52"""
        patterns = [
            # ICICI shows "Your Total Amount Due" followed by amount on same or next line
            r"Your\s+Total\s+Amount\s+Due.{0,100}?([\d,]+\.?\d*)",
            r"Total\s+Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Total\s+Outstanding\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"New\s+Balance\s*:?\s*([\d,]+\.?\d*)",
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
                        logger.info(f"ICICI: Found amount: INR {amount}")
                        return field, 1.0
                except ValueError:
                    continue
        
        logger.warning("ICICI: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="INR"), 0.0
