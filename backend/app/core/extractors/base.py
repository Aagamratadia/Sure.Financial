"""Base extractor interface"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from app.models.schemas import DateRangeField, DateField, AmountField
from app.models.enums import CardIssuer
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
        
        return {
            "data": {
                "card_issuer": issuer,
                "card_number": card_number,
                "statement_period": statement_period,
                "payment_due_date": due_date,
                "total_amount_due": total_amount,
            },
            "confidence": {
                "card_issuer": issuer_conf,
                "card_number": card_conf,
                "statement_period": period_conf,
                "payment_due_date": due_conf,
                "total_amount_due": amount_conf,
            }
        }
