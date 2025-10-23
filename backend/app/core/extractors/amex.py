"""American Express extractor"""
import regex as re
from typing import Tuple
from app.core.extractors.base import BaseExtractor
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.date_parser import parse_date, parse_date_range
from app.utils.amount_parser import parse_amount
import logging

logger = logging.getLogger(__name__)


class AmexExtractor(BaseExtractor):
    """Extractor for American Express credit card statements"""
    
    ISSUER_NAME = CardIssuer.AMEX
    
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """Extract American Express name"""
        patterns = [
            r"American\s+Express",
            r"AEBC",
            r"americanexpress\.co\.in",
            r"American\s+Express\s+Banking\s+Corp",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return self.ISSUER_NAME.value, 1.0
        
        return "", 0.0
    
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """Extract card number - Amex format: 3769 XXXX XXXX 000 or XXXX-XXXXXX-01007"""
        patterns = [
            r"(\d{4}\s*X{4}\s*X{4}\s*\d{3,4})",
            r"(X{4}-X{6}-\d{5})",
            r"(\d{4}[\s\-]X{6}[\s\-]\d{5})",
            r"Membership\s+Number\s*:?\s*(\d{4}[\sX\-]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                card_num = match.group(1)
                card_num = ' '.join(card_num.split()).replace(' ', ' ')
                logger.info(f"Amex: Found card number: {card_num}")
                return card_num, 1.0
        
        logger.warning("Amex: Card number not found")
        return "", 0.0
    
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """Extract statement period - Amex format varies"""
        patterns = [
            r"From\s+(\w+\s+\d{1,2})\s+to\s+(\w+\s+\d{1,2},\s+\d{4})",
            r"Statement\s+Period\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"From\s+(\d{2}\d{2}\d{4})\s+to\s+(\d{2}\d{2}\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_raw, end_raw = match.groups()
                start_date = parse_date(start_raw)
                end_date = parse_date(end_raw)
                
                if start_date and end_date:
                    field = DateRangeField(
                        raw=f"{start_raw} to {end_raw}",
                        start_date=start_date,
                        end_date=end_date
                    )
                    logger.info(f"Amex: Found statement period: {start_date} to {end_date}")
                    return field, 1.0
        
        # Fallback
        start_date, end_date = parse_date_range(text)
        if start_date and end_date:
            field = DateRangeField(
                raw="Parsed from text",
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"Amex: Parsed statement period: {start_date} to {end_date}")
            return field, 0.7
        
        logger.warning("Amex: Statement period not found")
        return DateRangeField(raw=""), 0.0
    
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """Extract payment due date - Amex format: February 1, 2024"""
        patterns = [
            # Minimum Payment Due section often has the date
            r"Minimum\s+Payment\s+Due\s*.*?(\w+\s+\d{1,2},?\s+\d{4})",
            r"Payment\s+Due\s+Date\s*:?\s*(\w+\s+\d{1,2},?\s+\d{4})",
            r"Due\s+Date\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})",
            r"Pay\s+by\s*:?\s*(\w+\s+\d{1,2},?\s+\d{4})",
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
                    logger.info(f"Amex: Found due date: {date_formatted}")
                    return field, 1.0
        
        logger.warning("Amex: Due date not found")
        return DateField(raw=""), 0.0
    
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """Extract total amount due - Amex format: Rs. 1,219.26"""
        patterns = [
            # Amex shows "Closing Balance Rs" as the total amount
            r"Closing\s+Balance\s+Rs\.?\s*([\d,]+\.?\d*)",
            r"Total\s+Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"New\s+Balance\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Your\s+Total\s+Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            # Min Payment Due is also important
            r"Min\s+Payment\s+Due\s+Rs\.?\s*([\d,]+\.?\d*)",
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
                    logger.info(f"Amex: Found amount: {currency} {amount}")
                    return field, 1.0
        
        logger.warning("Amex: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="INR"), 0.0
