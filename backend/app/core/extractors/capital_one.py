"""Capital One extractor"""
import regex as re
from typing import Tuple
from app.core.extractors.base import BaseExtractor
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.date_parser import parse_date, parse_date_range
from app.utils.amount_parser import parse_amount
import logging

logger = logging.getLogger(__name__)


class CapitalOneExtractor(BaseExtractor):
    """Extractor for Capital One Europe credit card statements"""
    
    ISSUER_NAME = CardIssuer.CAPITAL_ONE
    
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """Extract Capital One name"""
        patterns = [
            r"Capital\s+One\s+Europe",
            r"capitalone\.co\.uk",
            r"Capital\s+One",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return self.ISSUER_NAME.value, 1.0
        
        return "", 0.0
    
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """Extract card number - Capital One format: 4811 (short) or full masked"""
        patterns = [
            r"(\d{4}\s*\*{4}\s*\*{4}\s*\d{4})",
            r"(\d{4}\s*X{4}\s*X{4}\s*\d{4})",
            r"Card\s+ending\s+in\s+(\d{4})",
            r"(\d{4})(?:\s|$)",  # Last resort: just 4 digits
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                card_num = match.group(1)
                return card_num, 0.9 if len(card_num) == 4 else 1.0
        
        logger.warning("Capital One: Card number not found")
        return "", 0.0
    
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """Extract statement period - Capital One format: Statement date 5 October 24"""
        patterns = [
            # Capital One uses "Statement date DD Month YY" format
            r"Statement\s+date\s+(\d{1,2}\s+\w+\s+\d{2,4})",
            r"From\s+(\d{8})\s+to\s+(\d{8})",
            r"Statement\s+Period\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{1,2}\s+\w+\s+\d{4})\s+to\s+(\d{1,2}\s+\w+\s+\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    # Single statement date - use as end date
                    date_raw = groups[0]
                    end_date = parse_date(date_raw)
                    if end_date:
                        field = DateRangeField(
                            raw=f"Statement date {date_raw}",
                            start_date="",
                            end_date=end_date
                        )
                        logger.info(f"Capital One: Found statement date: {end_date}")
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
                        logger.info(f"Capital One: Found statement period: {start_date} to {end_date}")
                        return field, 1.0
        
        # Fallback
        start_date, end_date = parse_date_range(text)
        if start_date and end_date:
            field = DateRangeField(
                raw="Parsed from text",
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"Capital One: Parsed statement period: {start_date} to {end_date}")
            return field, 0.7
        
        logger.warning("Capital One: Statement period not found")
        return DateRangeField(raw=""), 0.0
    
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """Extract payment due date - Capital One format: It's due on 31 Oct 24"""
        patterns = [
            # Capital One uses "It's due on DD Mon YY" format
            r"(?:It'?s\s+)?due\s+on\s+(\d{1,2}\s+\w+\s+\d{2,4})",
            r"Payment\s+Due\s+Date\s*:?\s*(\d{8})",
            r"Due\s+Date\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Pay\s+by\s*:?\s*(\d{1,2}\s+\w+\s+\d{2,4})",
            # Generic date after "due"
            r"due\s+(?:date\s+)?(?:on\s+)?(\d{1,2}\s+\w+\s+\d{2,4})",
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
                    logger.info(f"Capital One: Found due date: {date_formatted}")
                    return field, 1.0
        
        logger.warning("Capital One: Due date not found")
        return DateField(raw=""), 0.0
    
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """Extract total amount due - Capital One format: Your new balance £1,219.26"""
        patterns = [
            # Capital One shows "Your new balance £amount"
            r"(?:Your\s+)?[Nn]ew\s+balance\s+£\s*([\d,]+\.?\d*)",
            r"NEW\s+CLOSING\s+BALANCE\s+£\s*([\d,]+\.?\d*)",
            r"Total\s+Amount\s+Due\s*:?\s*£\s*([\d,]+\.?\d*)",
            r"New\s+Balance\s*:?\s*£\s*([\d,]+\.?\d*)",
            r"Amount\s+Due\s*:?\s*£\s*([\d,]+\.?\d*)",
            # Support GBP symbol without space
            r"(?:Your\s+)?[Nn]ew\s+balance\s+£([\d,]+\.?\d*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_raw = match.group(0)
                amount, currency = parse_amount(amount_raw, default_currency="GBP")
                
                if amount is not None and amount > 0:
                    field = AmountField(
                        raw=amount_raw,
                        amount=amount,
                        currency=currency
                    )
                    logger.info(f"Capital One: Found amount: {currency} {amount}")
                    return field, 1.0
        
        logger.warning("Capital One: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="GBP"), 0.0
