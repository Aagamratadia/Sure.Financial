"""HDFC Bank extractor"""
import regex as re
from typing import Tuple
from app.core.extractors.base import BaseExtractor
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.date_parser import parse_date, parse_date_range
from app.utils.amount_parser import parse_amount
import logging

logger = logging.getLogger(__name__)


class HDFCExtractor(BaseExtractor):
    """Extractor for HDFC Bank credit card statements"""
    
    ISSUER_NAME = CardIssuer.HDFC
    
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """Extract HDFC Bank name"""
        patterns = [
            r"HDFC\s+Bank",
            r"Platinum\s+Times\s+Card",
            r"GSTIN\s*33AAACH2702H2Z6",
            r"hdfcbank\.com",
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return self.ISSUER_NAME.value, 1.0
        
        return "", 0.0
    
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """Extract card number - HDFC format: 5228 52XX XXXX 0591"""
        patterns = [
            r"(\d{4}\s*\d{2}X{2}\s*X{4}\s*\d{4})",
            r"(\d{4}\s+X{4}\s+X{4}\s+\d{4})",
            r"Card\s+No\.?\s*:?\s*(\d{4}\s+\d{2}X{2}\s+X{4}\s+\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                card_num = match.group(1) if match.lastindex else match.group(0)
                # Normalize spacing
                card_num = ' '.join(card_num.split())
                return card_num, 1.0
        
        logger.warning("HDFC: Card number not found")
        return "", 0.0
    
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """Extract statement period - HDFC format: Statement Date:08/06/2019"""
        patterns = [
            # HDFC shows "Statement Date:DD/MM/YYYY" format
            r"Statement\s+Date\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"Statement\s+for.*?(\d{2}/\d{2}/\d{4})",
            # Also support 8-digit format (DDMMYYYY)
            r"Statement\s+Date\s*:?\s*(\d{8})",
            # Look for two dates near "Statement" or "Period"
            r"(?:Statement|Period|From).{0,100}?(\d{2}/\d{2}/\d{4}).{0,50}?(?:to|To)\s*(\d{2}/\d{2}/\d{4})",
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
                            raw=f"Statement Date {date_raw}",
                            start_date="",
                            end_date=end_date
                        )
                        logger.info(f"HDFC: Found statement date: {end_date}")
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
                        logger.info(f"HDFC: Found statement period: {start_date} to {end_date}")
                        return field, 1.0
        
        # Fallback to general date range parsing
        start_date, end_date = parse_date_range(text)
        if start_date and end_date:
            field = DateRangeField(
                raw="Parsed from text",
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"HDFC: Parsed statement period: {start_date} to {end_date}")
            return field, 0.7
        
        logger.warning("HDFC: Statement period not found")
        return DateRangeField(raw=""), 0.0
    
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """Extract payment due date - HDFC format: 28/06/2019"""
        patterns = [
            # Look for any DD/MM/YYYY date after "Payment Due Date" within 200 characters
            r"Payment\s+Due\s+Date.{0,200}?(\d{2}/\d{2}/\d{4})",
            r"Due\s+Date.{0,100}?(\d{2}/\d{2}/\d{4})",
            # Same line patterns
            r"Payment\s+Due\s+Date\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"Due\s+Date\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"Pay\s+by\s*:?\s*(\d{2}/\d{2}/\d{4})",
            # Also support 8-digit format (DDMMYYYY)
            r"Payment\s+Due\s+Date.{0,200}?(\d{8})",
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
                    logger.info(f"HDFC: Found due date: {date_formatted}")
                    return field, 1.0
        
        logger.warning("HDFC: Due date not found")
        return DateField(raw=""), 0.0
    
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """Extract total amount due - HDFC format: 45,240.00"""
        patterns = [
            # HDFC shows "Payment Due Date Minimum Amount Due" followed by amounts on next line
            # Format: "28/06/2019 45,240.00 2,262.00" - first number after date is total
            r"Payment\s+Due\s+Date\s+Minimum\s+Amount\s+Due[\s\n]+\d{2}/\d{2}/\d{4}\s+([\d,]+\.?\d*)",
            r"Minimum\s+Amount\s+Due[\s\n]+\d{2}/\d{2}/\d{4}\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)",
            # Standard patterns
            r"Total\s+Amount\s+Due\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Total\s+Dues\s*:?\s*([\d,]+\.?\d*)",
            r"New\s+Balance\s*:?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"CLOSING\s+BALANCE\s*:?\s*([\d,]+\.?\d*)",
            # Just look for the pattern "DD/MM/YYYY number number" and take first number
            r"\d{2}/\d{2}/\d{4}\s+([\d,]+\.?\d*)\s+[\d,]+\.?\d*",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
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
                        logger.info(f"HDFC: Found amount: INR {amount}")
                        return field, 1.0
                except ValueError:
                    continue
        
        logger.warning("HDFC: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="INR"), 0.0
