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
        """Extract card number - ICICI masked variants
        Examples: '3769 XXXX XXXX 000' or '4375 XXXX XXXX 3019'
        """
        patterns = [
            # 4-4-4-3/4 masked with X/\*
            r"(\d{4}\s*[X*]{4}\s*[X*]{4}\s*\d{3,4})",
            # 6-6-4 mask
            r"(\d{6}[X*]{6}\d{4})",
            # With label 'Card No.'
            r"Card\s+No\.?\s*:?\s*(\d{4}[\sX*]{4,}[\sX*]{4,}\d{3,4})",
            # With label 'Card Account No'
            r"Card\s+Account\s+No\s*:?\s*(\d{4}[\sX*]{4,}[\sX*]{4,}\d{3,4})",
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
        """Extract total amount due - ICICI format: Your Total Amount Due 5,882.52
        Ensure we don't capture the day from a date (e.g., '23' from '23/04/2019').
        """
        patterns = [
            r"Your\s+Total\s+Amount\s+Due[^\d]{0,50}([\d,]+\.\d{2})",
            # Next-line variant
            r"Your\s+Total\s+Amount\s+Due[^\n\r]*[\n\r]+\s*([\d,]+\.\d{2})",
            # With rupee sign nearby
            r"Your\s+Total\s+Amount\s+Due[\s\S]{0,80}?₹\s*([\d,]+\.\d{2})",
            # Words possibly split by newlines/spaces
            r"Your\s*\n?\s*Total\s*\n?\s*Amount\s*\n?\s*Due[\s\S]{0,120}?([\d,]+\.\d{2})",
            # Amount near the 'Due Date' block on the right panel
            r"₹\s*([\d,]+\.\d{2})[\s\S]{0,60}?Due\s*Date",
            # Allow newlines/spaces between words
            r"Your\s*\n?\s*Total\s*\n?\s*Amount\s*\n?\s*Due\s*\n?\s*([\d,]+\.\d{2})",
            # Allow newlines/spaces between words and rupee sign
            r"Your\s*\n?\s*Total\s*\n?\s*Amount\s*\n?\s*Due\s*\n?\s*₹\s*([\d,]+\.\d{2})",
            # Label variants with currency
            r"Total\s+Amount\s+Due\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.\d{2})",
            r"Total\s+Outstanding\s*:?\s*(?:Rs\.?|INR|₹)\s*([\d,]+\.\d{2})",
            r"New\s+Balance\s*:?\s*([\d,]+\.\d{2})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                amount_raw = match.group(1)
                # Clean and parse the amount
                amount_str = amount_raw.replace(',', '')
                # Skip if the matched amount appears near 'Minimum Amount Due'
                try:
                    span_start = match.start(1)
                    context = text[max(0, span_start - 80): span_start + 20]
                    if re.search(r"Minimum\s+Amount\s+Due", context, re.IGNORECASE):
                        continue
                except Exception:
                    pass
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

        # Additional targeted fallbacks around visible labels
        m_after_label = re.search(
            r"Total\s+Amount\s+Due[\s\S]{0,200}?(?:₹|INR|Rs\.?)[^\d]{0,5}([\d,]+\.\d{2})",
            text,
            re.IGNORECASE,
        )
        if m_after_label:
            try:
                val = float(m_after_label.group(1).replace(',', ''))
                field = AmountField(raw=m_after_label.group(1), amount=val, currency="INR")
                logger.info(f"ICICI: Found amount near label fallback: INR {val}")
                return field, 0.85
            except ValueError:
                pass

        m_due = re.search(r"Due\s*Date", text, re.IGNORECASE)
        if m_due:
            idx = m_due.start()
            window = text[max(0, idx - 160):idx]
            m_num = re.search(r"([\d,]+\.\d{2})\s*$", window, re.MULTILINE)
            if m_num:
                try:
                    val = float(m_num.group(1).replace(',', ''))
                    field = AmountField(raw=m_num.group(1), amount=val, currency="INR")
                    logger.info(f"ICICI: Found amount before Due Date fallback: INR {val}")
                    return field, 0.8
                except ValueError:
                    pass
        
        # Fallback: compute from Statement Summary block (robust to OCR noise)
        try:
            block_start = re.search(r"Statement\s+Summary", text, re.IGNORECASE)
            if block_start:
                # Take up to next 200 chars as the row region
                start_idx = block_start.start()
                region = text[start_idx:start_idx + 220]
                # Extract numeric tokens with optional decimals (handles '000', '0 00', '6,481.76')
                nums = re.findall(r"\d[\d,]*(?:\.\d{1,2})?", region)
                if len(nums) >= 4:
                    prev_bal = float(nums[0].replace(',', ''))
                    purchases = float(nums[1].replace(',', ''))
                    cash_adv = float(nums[2].replace(',', ''))
                    payments = float(nums[3].replace(',', ''))
                    total = round(prev_bal + purchases + cash_adv - payments, 2)
                    field = AmountField(raw=f"{total:,.2f}", amount=total, currency="INR")
                    logger.info(f"ICICI: Computed total amount due from summary (robust): INR {total}")
                    return field, 0.7
        except Exception:
            pass

        logger.warning("ICICI: Total amount not found")
        return AmountField(raw="", amount=0.0, currency="INR"), 0.0

    # -----------------------
    # ICICI-specific optional extractors
    # -----------------------
    def extract_minimum_amount_due(self, text: str):
        """Extract Minimum Amount Due for ICICI statements.
        Sample (from logs):
        "Statement Date ... Minimum Amount Due Your Total Amount Due\n23/04/2019 300.00 ... Your Total Amount Due 5,882.52"
        """
        # Look for a number near "Minimum Amount Due"
        pats = [
            r"Minimum\s+Amount\s+Due\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
            # Table header style: date followed by value (support numeric months too)
            r"Statement\s*Date[\s\S]{0,60}?[\n\r]+\s*\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}\s+([\d,]+\.?\d*)",
        ]
        for p in pats:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                raw = m.group(1)
                try:
                    amt = float(raw.replace(',', ''))
                    field = AmountField(raw=raw, amount=amt, currency="INR")
                    logger.info(f"ICICI: Found minimum amount due: INR {amt}")
                    return field
                except ValueError:
                    continue
        return None

    def extract_previous_balance(self, text: str):
        """Extract Previous Balance for ICICI statements.
        Ex: line contains 'Previous Bal' or 'Previous Balance' followed by an amount.
        """
        pats = [
            r"Previous\s+Bal(?:ance)?\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
            r"Opening\s+Balance\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
        ]
        for p in pats:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                raw = m.group(1)
                try:
                    amt = float(raw.replace(',', ''))
                    field = AmountField(raw=raw, amount=amt, currency="INR")
                    logger.info(f"ICICI: Found previous balance: INR {amt}")
                    return field
                except ValueError:
                    continue
        return None

    def extract_available_credit_limit(self, text: str):
        """Extract Available Credit and/or Credit Limit for ICICI statements.
        We'll capture Available Credit as the field value when possible.
        """
        # Prefer Available Credit if present
        m_avail = re.search(r"Available\s+Credit\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if m_avail:
            raw = m_avail.group(1)
            try:
                amt = float(raw.replace(',', ''))
                field = AmountField(raw=raw, amount=amt, currency="INR")
                logger.info(f"ICICI: Found available credit: INR {amt}")
                return field
            except ValueError:
                pass
        # Fallback to Credit Limit if needed
        m_limit = re.search(r"Credit\s+Limit\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if m_limit:
            raw = m_limit.group(1)
            try:
                amt = float(raw.replace(',', ''))
                field = AmountField(raw=raw, amount=amt, currency="INR")
                logger.info(f"ICICI: Found credit limit: INR {amt}")
                return field
            except ValueError:
                pass
        return None

    def extract_reward_points_summary(self, text: str):
        """Extract reward points summary (opening/earned/redeemed/closing) when visible."""
        # Try closing balance of points
        m_close = re.search(r"Rewards.*?Closing\s+Balance\s*[:\-]?\s*([\d,]+)", text, re.IGNORECASE | re.DOTALL)
        if m_close:
            logger.info("ICICI: Found rewards closing balance")
            return f"Rewards Closing Balance: {m_close.group(1)}"
        # Fallback: capture short snippet
        sec = re.search(r"Rewards[\s\S]{0,200}", text, re.IGNORECASE)
        return sec.group(0).strip() if sec else None

    def extract_all(self, text: str) -> dict:
        logger.info(f"Extracting data using {self.__class__.__name__}")
        logger.info(f"Text length: {len(text)} characters")
        if len(text) > 0:
            logger.info(f"First 800 chars:\n{text[:800]}")
            logger.info(f"Last 800 chars:\n{text[-800:]}")

        issuer, issuer_conf = self.extract_card_issuer(text)
        card_number, card_conf = self.extract_card_number(text)
        statement_period, period_conf = self.extract_statement_period(text)
        due_date, due_conf = self.extract_due_date(text)
        total_amount, amount_conf = self.extract_total_amount(text)

        # ICICI-specific optional fields
        min_due = self.extract_minimum_amount_due(text)
        prev_bal = self.extract_previous_balance(text)
        avail_credit = self.extract_available_credit_limit(text)
        rewards = self.extract_reward_points_summary(text)

        data = {
            "card_issuer": issuer,
            "card_number": card_number,
            "statement_period": statement_period,
            "payment_due_date": due_date,
            "total_amount_due": total_amount,
        }
        if min_due:
            data["minimum_amount_due"] = min_due
        if prev_bal:
            data["previous_balance"] = prev_bal
        if avail_credit:
            data["available_credit_limit"] = avail_credit
        if rewards:
            data["reward_points_summary"] = rewards

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
