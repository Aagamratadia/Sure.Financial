"""Base extractor interface"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List, Dict
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
from app.utils.amount_parser import parse_amount
from app.utils.date_parser import parse_date
import re
import logging

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for issuer-specific extractors"""
    
    ISSUER_NAME: CardIssuer = CardIssuer.UNKNOWN
    
    @abstractmethod
    def extract_card_issuer(self, text: str) -> Tuple[str, float]:
        """
        Extract and verify card issuer name
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Tuple of (issuer_name, confidence_score)
        """
        pass
    
    @abstractmethod
    def extract_card_number(self, text: str) -> Tuple[str, float]:
        """
        Extract masked card number
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Tuple of (card_number, confidence_score)
        """
        pass
    
    @abstractmethod
    def extract_statement_period(self, text: str) -> Tuple[DateRangeField, float]:
        """
        Extract statement period dates
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Tuple of (date_range_field, confidence_score)
        """
        pass
    
    @abstractmethod
    def extract_due_date(self, text: str) -> Tuple[DateField, float]:
        """
        Extract payment due date
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Tuple of (date_field, confidence_score)
        """
        pass
    
    @abstractmethod
    def extract_total_amount(self, text: str) -> Tuple[AmountField, float]:
        """
        Extract total amount due
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Tuple of (amount_field, confidence_score)
        """
        pass
    
    def extract_all(self, text: str) -> dict:
        """
        Extract all data points
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Dictionary with all extracted data and confidence scores
        """
        logger.info(f"Extracting data using {self.__class__.__name__}")
        
        # Show extracted text to help troubleshoot
        logger.info(f"Text length: {len(text)} characters")
        if len(text) > 0:
            logger.info(f"First 800 chars:\n{text[:800]}")
            logger.info(f"Last 800 chars:\n{text[-800:]}")
        
        issuer, issuer_conf = self.extract_card_issuer(text)
        card_number, card_conf = self.extract_card_number(text)
        statement_period, period_conf = self.extract_statement_period(text)
        due_date, due_conf = self.extract_due_date(text)
        total_amount, amount_conf = self.extract_total_amount(text)

        # Optional fields via generic heuristics
        minimum_amount = self._extract_minimum_amount_due(text)
        if minimum_amount:
            logger.info(f"Optional: Minimum Amount Due detected -> INR {minimum_amount.amount}")
        previous_balance = self._extract_previous_balance(text)
        if previous_balance:
            logger.info(f"Optional: Previous Balance detected -> INR {previous_balance.amount}")
        available_credit = self._extract_available_credit_limit(text)
        if available_credit:
            logger.info(f"Optional: Available Credit Limit detected -> INR {available_credit.amount}")
        rewards_summary = self._extract_reward_points_summary(text)
        if rewards_summary:
            logger.info("Optional: Reward Points Summary section detected")
        transactions = self._extract_transactions(text)
        if transactions:
            logger.info(f"Optional: Transactions detected -> {len(transactions)} rows")

        data: Dict[str, object] = {
            "card_issuer": issuer,
            "card_number": card_number,
            "statement_period": statement_period,
            "payment_due_date": due_date,
            "total_amount_due": total_amount,
        }

        if minimum_amount:
            data["minimum_amount_due"] = minimum_amount
        if previous_balance:
            data["previous_balance"] = previous_balance
        if available_credit:
            data["available_credit_limit"] = available_credit
        if rewards_summary:
            data["reward_points_summary"] = rewards_summary
        if transactions:
            data["transactions"] = transactions

        return {
            "data": data,
            "confidence": {
                "card_issuer": issuer_conf,
                "card_number": card_conf,
                "statement_period": period_conf,
                "payment_due_date": due_conf,
                "total_amount_due": amount_conf,
            }
        }

    # -----------------------
    # Generic optional extractors
    # -----------------------
    def _extract_minimum_amount_due(self, text: str) -> Optional[AmountField]:
        patterns = [
            r"Minimum\s+Amount\s+Due\s*[:\-]?\s*Rs\.?\s*[^\d]{0,2}([\d,]+\.?\d*)",
            r"Minimum\s+Amount\s+Due\s*[\n\r\s]+[^\d]{0,2}([\d,]+\.?\d*)",
            r"Min\.?\s+Amt\.?\s+Due\s*[:\-]?\s*[^\d]{0,2}([\d,]+\.?\d*)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                amt_str = m.group(1).replace(',', '')
                try:
                    amt = float(amt_str)
                    return AmountField(raw=m.group(1), amount=amt, currency="INR")
                except ValueError:
                    continue
        return None

    def _extract_previous_balance(self, text: str) -> Optional[AmountField]:
        patterns = [
            r"Previous\s+Balance\s*[:\-]?\s*Rs\.?\s*[^\d]{0,2}([\d,]+\.?\d*)",
            r"Previous\s+Balance\s*[\n\r\s]+[^\d]{0,2}([\d,]+\.?\d*)",
            r"Opening\s+Balance\s*[:\-]?\s*[^\d]{0,2}([\d,]+\.?\d*)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                amt_str = m.group(1).replace(',', '')
                try:
                    amt = float(amt_str)
                    return AmountField(raw=m.group(1), amount=amt, currency="INR")
                except ValueError:
                    continue
        return None

    def _extract_available_credit_limit(self, text: str) -> Optional[AmountField]:
        patterns = [
            r"Available\s+Credit\s+Limit\s*[:\-]?\s*Rs\.?\s*([\d,]+\.?\d*)",
            r"Available\s+Credit\s*[\n\r\s]+([\d,]+\.?\d*)",
            r"Credit\s+Limit\s*[:\-]?\s*([\d,]+\.?\d*)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                amt_str = m.group(1).replace(',', '')
                try:
                    amt = float(amt_str)
                    return AmountField(raw=m.group(1), amount=amt, currency="INR")
                except ValueError:
                    continue
        return None

    def _extract_reward_points_summary(self, text: str) -> Optional[str]:
        patterns = [
            r"Reward\s+Points\s+Summary[\s\S]{0,120}?Total\s*:?\s*([\d,]+)",
            r"Total\s+Reward\s+Points\s*:?\s*([\d,]+)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(0).strip()
        # If a section exists without total, capture a short snippet
        sec = re.search(r"Reward\s+Points\s+Summary[\s\S]{0,200}", text, re.IGNORECASE)
        return sec.group(0).strip() if sec else None

    def _extract_transactions(self, text: str) -> Optional[List[dict]]:
        # Heuristic: lines with date + merchant + amount
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        txns: List[dict] = []
        date_pat = re.compile(r"(\d{2}[\-/]\d{2}[\-/]\d{4}|\d{2}[\-/]\d{2}[\-/]\d{2})")
        amount_pat = re.compile(r"([\-]?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)$")
        for ln in lines:
            d_match = date_pat.search(ln)
            if not d_match:
                continue
            # Split line into parts; assume last token is amount
            parts = ln.split()
            last = parts[-1]
            if not amount_pat.search(last):
                continue
            amount = last
            merchant = ' '.join(parts[1:-1]) if len(parts) > 2 else ''
            # Normalize date
            d_raw = d_match.group(1)
            d_fmt = parse_date(d_raw) or d_raw
            # Skip if merchant empty or amount malformed
            if merchant and amount:
                txns.append({
                    "date": d_fmt,
                    "merchant": merchant,
                    "amount": f"INR {amount}",
                })
        return txns if txns else None
