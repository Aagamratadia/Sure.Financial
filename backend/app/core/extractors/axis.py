"""Axis Bank credit card statement extractor"""
import regex as re
from typing import Tuple
from app.core.extractors.base import BaseExtractor
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.date_parser import parse_date, parse_date_range
from app.utils.amount_parser import parse_amount
import logging

logger = logging.getLogger(__name__)


class AxisExtractor(BaseExtractor):
    """Extractor for Axis Bank credit card statements"""
    
    ISSUER_NAME = CardIssuer.AXIS
    
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """Extract Axis Bank name"""
        patterns = [
            r"Axis\s+Bank",
            r"AXIS\s+BANK",
            r"axisbank\.com",
            r"Axis\s+Bank\s+Ltd",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return self.ISSUER_NAME.value, 1.0
        
        return "", 0.0
    
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """Extract card number - Axis format variations"""
        patterns = [
            r"Card\s+Number\s*:?\s*([X*\d]{4}[\s\-]*[X*\d]{4}[\s\-]*[X*\d]{4}[\s\-]*\d{4})",
            r"Card\s+No\.?\s*:?\s*([X*\d]{4}[\s\-]*[X*\d]{4}[\s\-]*[X*\d]{4}[\s\-]*\d{4})",
            r"Credit\s+Card\s+Number\s*:?\s*([X*\d]{4}[\s\-]*[X*\d]{4}[\s\-]*[X*\d]{4}[\s\-]*\d{4})",
            r"([X*]{4}[\s\-]*[X*]{4}[\s\-]*[X*]{4}[\s\-]*\d{4})",
            r"(\d{4}[\s\-]*[X*]{4}[\s\-]*[X*]{4}[\s\-]*\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                card_num = match.group(1)
                # Normalize spacing/dashes to spaces
                card_num = re.sub(r'[\s\-]+', ' ', card_num).strip()
                logger.info(f"Axis: Found card number: {card_num}")
                return card_num, 0.9
        
        logger.warning("Axis: Card number not found")
        return "", 0.0
    
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """Extract statement period - Axis formats"""
        # Range patterns
        range_patterns = [
            r"Statement\s+Date\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})\s*(?:to|To|TO)\s*(\d{2}/\d{2}/\d{4})",
            r"Statement\s+Period\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})\s*(?:to|To|TO)\s*(\d{2}/\d{2}/\d{4})",
            r"Billing\s+Cycle\s*:?\s*.{0,100}?(\d{2}-\w{3}-\d{4})\s*(?:to|To|TO)\s*(\d{2}-\w{3}-\d{4})",
            r"From\s+(\d{2}/\d{2}/\d{4})\s+(?:to|To|TO)\s+(\d{2}/\d{2}/\d{4})",
            r"Statement\s+from\s*.{0,100}?(\d{2}/\d{2}/\d{4})\s*(?:to|To|TO)\s*(\d{2}/\d{2}/\d{4})",
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                start_raw = match.group(1)
                end_raw = match.group(2)
                
                start_date = parse_date(start_raw)
                end_date = parse_date(end_raw)
                
                if start_date and end_date:
                    field = DateRangeField(
                        raw=f"{start_raw} to {end_raw}",
                        start_date=start_date,
                        end_date=end_date
                    )
                    logger.info(f"Axis: Found statement period: {start_date} to {end_date}")
                    return field, 0.9
        
        # Single date patterns (fallback)
        single_patterns = [
            r"Statement\s+Date\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Statement\s+on\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Date\s+of\s+Statement\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
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
                    logger.info(f"Axis: Found single statement date: {end_date}")
                    return field, 0.85
        
        # Fallback to general date range parsing
        start_date, end_date = parse_date_range(text)
        if start_date and end_date:
            field = DateRangeField(
                raw="Parsed from text",
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"Axis: Parsed statement period: {start_date} to {end_date}")
            return field, 0.7
        
        logger.warning("Axis: Statement period not found")
        return DateRangeField(raw=""), 0.0
    
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """Extract payment due date - Axis formats"""
        # Try to find a date after the statement period (e.g., 05/10/2024)
        # Payment summary line: ... 16/08/2024 - 15/09/2024 05/10/2024 13/09/2024
        summary_pattern = r"\d{1,2}/\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{1,2}/\d{4}\s+(\d{1,2}/\d{1,2}/\d{4})"
        match = re.search(summary_pattern, text)
        if match:
            date_raw = match.group(1)
            date_formatted = parse_date(date_raw)
            if date_formatted:
                field = DateField(
                    raw=date_raw,
                    formatted=date_formatted
                )
                logger.info(f"Axis: Found due date (summary): {date_formatted}")
                return field, 0.95
        # Fallback to standard patterns
        patterns = [
            r"Payment\s+Due\s+Date\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Due\s+Date\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Pay\s+by\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Payment\s+due\s+on\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Due\s+on\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Payment\s+Due\s+Date\s*:?\s*.{0,100}?(\d{2}-\w{3}-\d{4})",
            r"Due\s+Date\s*:?\s*.{0,100}?(\d{2}-\w{3}-\d{4})",
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
                    logger.info(f"Axis: Found due date: {date_formatted}")
                    return field, 0.9
        logger.warning("Axis: Due date not found")
        return DateField(raw=""), 0.0
    
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """Extract total amount due - Axis formats"""
        # Try to find Dr/Cr pattern in payment summary line
        # Example: 40,491.00 Dr
        drcr_pattern = r"([\d,]+\.\d{2})\s*Dr"
        match = re.search(drcr_pattern, text)
        if match:
            amount_raw = match.group(1)
            amount_str = amount_raw.replace(',', '')
            try:
                amount = float(amount_str)
                if amount > 0:
                    field = AmountField(
                        raw=amount_raw,
                        amount=amount,
                        currency="INR"
                    )
                    logger.info(f"Axis: Found amount (Dr): INR {amount}")
                    return field, 0.95
            except ValueError:
                pass
        # Fallback to standard patterns
        patterns = [
            r"Total\s+Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Amount\s+Payable\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Outstanding\s+Amount\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Total\s+Outstanding\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Current\s+Outstanding\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Total\s+Amount\s+Due\s*.{0,100}?(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
            r"Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                amount_raw = match.group(1)
                amount_str = amount_raw.replace(',', '')
                try:
                    amount = float(amount_str)
                    if amount > 0:
                        field = AmountField(
                            raw=amount_raw,
                            amount=amount,
                            currency="INR"
                        )
                        logger.info(f"Axis: Found amount: INR {amount}")
                        return field, 0.9
                except ValueError:
                    continue
        # Fallback: try to find just the number after "Total Amount Due"
        fallback_patterns = [
            r"Total\s+Amount\s+Due\s*.{0,200}?([\d,]+\.?\d*)",
            r"Amount\s+Payable\s*.{0,200}?([\d,]+\.?\d*)",
        ]
        for pattern in fallback_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                amount_raw = match.group(1)
                if ',' in amount_raw or '.' in amount_raw:
                    try:
                        amount = float(amount_raw.replace(',', ''))
                        if amount > 0:
                            field = AmountField(
                                raw=amount_raw,
                                amount=amount,
                                currency="INR"
                            )
                            logger.info(f"Axis: Found amount (fallback): INR {amount}")
                            return field, 0.75
                    except ValueError:
                        continue
        logger.warning("Axis: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="INR"), 0.0

