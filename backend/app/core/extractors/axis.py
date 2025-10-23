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
        """Extract statement period for Axis Bank"""
        summary_pattern = r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}/\d{1,2}/\d{4})"
        match = re.search(summary_pattern, text)
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
        # Fallback to previous logic
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
                start_date = parse_date(date_raw)
                if start_date:
                    field = DateRangeField(
                        raw=f"Statement Date {date_raw}",
                        start_date=start_date,
                        end_date=""
                    )
                    logger.info(f"Axis: Found single statement date: {start_date}")
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
            return field, 0.9
        logger.warning("Axis: Statement period not found")
        return DateRangeField(raw=""), 0.0

    def extract_statement_date(self, text: str) -> Tuple[str, float]:
        """Extract statement generated date for Axis Bank"""
        summary_pattern = r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}/\d{1,2}/\d{4})"
        match = re.search(summary_pattern, text)
        if match:
            statement_raw = match.group(4)
            statement_date = parse_date(statement_raw)
            if statement_date:
                logger.info(f"Axis: Found statement generated date: {statement_date}")
                return statement_date, 0.9
        # Fallback to single date patterns
        single_patterns = [
            r"Statement\s+Date\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Statement\s+on\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
            r"Date\s+of\s+Statement\s*:?\s*.{0,100}?(\d{2}/\d{2}/\d{4})",
        ]
        for pattern in single_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                date_raw = match.group(1)
                statement_date = parse_date(date_raw)
                if statement_date:
                    logger.info(f"Axis: Found statement generated date (fallback): {statement_date}")
                    return statement_date, 0.85
        logger.warning("Axis: Statement generated date not found")
        return "", 0.0
    def extract_all(self, text: str) -> dict:
        logger.info(f"Extracting data using {self.__class__.__name__}")
        logger.info(f"Text length: {len(text)} characters")
        if len(text) > 0:
            logger.info(f"First 800 chars:\n{text[:800]}")
            logger.info(f"Last 800 chars:\n{text[-800:]}")

        issuer, issuer_conf = self.extract_card_issuer(text)
        card_number, card_conf = self.extract_card_number(text)
        statement_period, period_conf = self.extract_statement_period(text)
        statement_date, date_conf = self.extract_statement_date(text)
        due_date, due_conf = self.extract_due_date(text)
        total_amount, amount_conf = self.extract_total_amount(text)

        # Axis-specific optional fields
        min_due = self.extract_minimum_amount_due(text)
        prev_bal = self.extract_previous_balance(text)
        avail_credit = self.extract_available_credit_limit(text)
        rewards = self.extract_reward_points_summary(text)

        data = {
            "card_issuer": issuer,
            "card_number": card_number,
            "statement_period": statement_period,
            "statement_date": statement_date,
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
                "statement_date": date_conf,
                "payment_due_date": due_conf,
                "total_amount_due": amount_conf,
            }
        }
        # Fallback to previous logic
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
                start_date = parse_date(date_raw)
                if start_date:
                    field = DateRangeField(
                        raw=f"Statement Date {date_raw}",
                        start_date=start_date,
                        end_date=""
                    )
                    logger.info(f"Axis: Found single statement date: {start_date}")
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
            return field, 0.9
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


    # -----------------------
    # Axis-specific optional extractors
    # -----------------------
    def extract_minimum_amount_due(self, text: str):
        """Extract Minimum Amount Due from Axis payment summary line.
        Example line:
        40,491.00 Dr 810.00 Dr 16/08/2024 - 15/09/2024 05/10/2024 13/09/2024
        """
        pattern = r"([\d,]+\.\d{2})\s*Dr\s+([\d,]+\.\d{2})\s*Dr\s+\d{1,2}/\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{1,2}/\d{4}"
        m = re.search(pattern, text)
        if m:
            # group(1) is Total Amount Due, group(2) is Minimum Amount Due
            min_raw = m.group(2)
            try:
                amt = float(min_raw.replace(',', ''))
                field = AmountField(raw=min_raw, amount=amt, currency="INR")
                logger.info(f"Axis: Found minimum amount due: INR {amt}")
                return field
            except ValueError:
                pass
        # Fallback label-based
        fallback = re.search(r"Minimum\s+Amount\s+Due\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if fallback:
            min_raw = fallback.group(1)
            try:
                amt = float(min_raw.replace(',', ''))
                field = AmountField(raw=min_raw, amount=amt, currency="INR")
                logger.info(f"Axis: Found minimum amount due (fallback): INR {amt}")
                return field
            except ValueError:
                pass
        return None

    def extract_previous_balance(self, text: str):
        """Extract Previous Balance from account summary line.
        Looks for a number tagged with Dr near 'Previous Balance'.
        """
        # Try to capture first amount after 'Previous Balance'
        pat = r"Previous\s+Balance[^\n\r]*[\n\r]+\s*([\d,]+\.\d{2})\s*Dr"
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1)
            try:
                amt = float(raw.replace(',', ''))
                field = AmountField(raw=raw, amount=amt, currency="INR")
                logger.info(f"Axis: Found previous balance: INR {amt}")
                return field
            except ValueError:
                pass
        # Generic label match
        m2 = re.search(r"Previous\s+Balance\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
        if m2:
            raw = m2.group(1)
            try:
                amt = float(raw.replace(',', ''))
                field = AmountField(raw=raw, amount=amt, currency="INR")
                logger.info(f"Axis: Found previous balance (fallback): INR {amt}")
                return field
            except ValueError:
                pass
        return None

    def extract_available_credit_limit(self, text: str):
        """Extract available credit or credit limit if present."""
        labels = [
            r"Available\s+Credit\s+Limit\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
            r"Credit\s+Limit\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
            r"Available\s+Limit\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
        ]
        for p in labels:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                raw = m.group(1)
                try:
                    amt = float(raw.replace(',', ''))
                    field = AmountField(raw=raw, amount=amt, currency="INR")
                    logger.info(f"Axis: Found credit/available limit: INR {amt}")
                    return field
                except ValueError:
                    continue
        return None

    def extract_reward_points_summary(self, text: str):
        """Try to capture reward points total or section snippet."""
        m = re.search(r"Reward[s]?\s+Summary[\s\S]{0,120}?Total\s*:?\s*([\d,]+)", text, re.IGNORECASE)
        if m:
            logger.info("Axis: Found reward points total")
            return f"Total Rewards: {m.group(1)}"
        sec = re.search(r"Reward[s]?\s+Summary[\s\S]{0,200}", text, re.IGNORECASE)
        return sec.group(0).strip() if sec else None

