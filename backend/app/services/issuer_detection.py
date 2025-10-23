"""Issuer detection service"""
import regex as re
from typing import Optional
from app.models.enums import CardIssuer
from app.utils.regex_patterns import ISSUER_PATTERNS
import logging

logger = logging.getLogger(__name__)


class IssuerDetector:
    """Detect credit card issuer from PDF text"""
    
    def detect_issuer(self, text: str) -> Optional[CardIssuer]:
        """
        Detect issuer from text
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Detected CardIssuer or None
        """
        # Analyze first 2000 characters (header area) - increased from 1000
        header_text = text[:2000]
        
        # Also check full text for issuer keywords (sometimes they appear later)
        full_text_sample = text[:5000] if len(text) > 5000 else text
        
        scores = {}
        
        # Check each issuer's patterns in both header and full text
        for issuer_key, patterns in ISSUER_PATTERNS.items():
            score = 0
            for pattern in patterns:
                # Check header (weighted more)
                header_matches = re.findall(pattern, header_text, re.IGNORECASE)
                score += len(header_matches) * 2  # Header matches count double
                
                # Check extended text
                full_matches = re.findall(pattern, full_text_sample, re.IGNORECASE)
                score += len(full_matches)
            
            if score > 0:
                scores[issuer_key] = score
                logger.info(f"Issuer detection - {issuer_key}: score {score}")
        
        if not scores:
            logger.warning("No issuer detected")
            logger.debug(f"Text sample (first 500 chars): {text[:500]}")
            return None
        
        # Get issuer with highest score
        best_issuer = max(scores, key=scores.get)
        
        # Map to CardIssuer enum
        issuer_map = {
            "kotak": CardIssuer.KOTAK,
            "hdfc": CardIssuer.HDFC,
            "icici": CardIssuer.ICICI,
            "idfc": CardIssuer.IDFC,
            "amex": CardIssuer.AMEX,
            "capital_one": CardIssuer.CAPITAL_ONE,
        }
        
        detected = issuer_map.get(best_issuer, CardIssuer.UNKNOWN)
        logger.info(f"Detected issuer: {detected.value} (score: {scores[best_issuer]})")
        
        return detected
