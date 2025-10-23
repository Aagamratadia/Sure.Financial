"""Parser orchestrator - coordinates all parsing operations"""
import time
from typing import Optional
from datetime import datetime
from app.core.parsers.pymupdf_parser import PyMuPDFParser
from app.core.parsers.pdfplumber_parser import PDFPlumberParser
from app.core.parsers.tesseract_parser import TesseractOCRParser, detect_if_ocr_needed
from app.core.extractors.kotak import KotakExtractor
from app.core.extractors.hdfc import HDFCExtractor
from app.core.extractors.icici import ICICIExtractor
from app.core.extractors.idfc import IDFCExtractor
from app.core.extractors.amex import AmexExtractor
from app.core.extractors.capital_one import CapitalOneExtractor
from app.services.issuer_detection import IssuerDetector
from app.models.schemas import ParseResult, ParsedData, ConfidenceScores, Metadata
from app.models.enums import CardIssuer, JobStatus, ParserType
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ParserOrchestrator:
    """Orchestrates PDF parsing and data extraction"""
    
    def __init__(self):
        # Initialize parsers
        self.pymupdf_parser = PyMuPDFParser()
        self.pdfplumber_parser = PDFPlumberParser()
        self.tesseract_parser = TesseractOCRParser()
        
        # Initialize extractors
        self.extractors = {
            CardIssuer.KOTAK: KotakExtractor(),
            CardIssuer.HDFC: HDFCExtractor(),
            CardIssuer.ICICI: ICICIExtractor(),
            CardIssuer.IDFC: IDFCExtractor(),
            CardIssuer.AMEX: AmexExtractor(),
            CardIssuer.CAPITAL_ONE: CapitalOneExtractor(),
        }
        
        # Initialize issuer detector
        self.issuer_detector = IssuerDetector()
    
    async def parse(
        self,
        file_path: str,
        filename: str,
        job_id: str,
        use_ocr: bool = False
    ) -> ParseResult:
        """
        Parse PDF and extract credit card statement data
        
        Args:
            file_path: Path to PDF file
            filename: Original filename
            job_id: Unique job identifier
            use_ocr: Force OCR usage
            
        Returns:
            ParseResult with extracted data
        """
        start_time = time.time()
        
        logger.info(f"Starting parsing for job {job_id}: {filename}")
        
        # Step 1: Extract text from PDF
        text, parser_used, metadata = await self._extract_text_with_fallback(
            file_path, use_ocr
        )
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Failed to extract sufficient text from PDF")
        
        logger.info(f"Extracted {len(text)} characters using {parser_used.value}")
        
        # Step 2: Detect issuer
        issuer = self.issuer_detector.detect_issuer(text)
        if not issuer or issuer == CardIssuer.UNKNOWN:
            logger.warning("Could not detect issuer, using generic extraction")
            issuer = CardIssuer.UNKNOWN
        else:
            logger.info(f"Detected issuer: {issuer.value}")
        
        # Step 3: Extract data using issuer-specific extractor
        extracted_data = await self._extract_data(text, issuer)
        
        # Step 4: Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Step 5: Build result
        result = ParseResult(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            filename=filename,
            issuer=issuer,
            data=extracted_data["data"],
            confidence_scores=extracted_data["confidence"],
            metadata=Metadata(
                pages=metadata["pages"],
                processing_time_ms=processing_time_ms,
                parser_used=parser_used,
                ocr_required=parser_used == ParserType.TESSERACT,
                file_size_bytes=metadata["file_size_bytes"]
            ),
            processed_at=datetime.utcnow()
        )
        
        logger.info(f"Parsing completed for job {job_id}, confidence: {result.confidence_scores.average:.2f}")
        
        return result
    
    async def _extract_text_with_fallback(
        self,
        file_path: str,
        force_ocr: bool = False
    ) -> tuple[str, ParserType, dict]:
        """
        Extract text with parser fallback logic
        
        Returns:
            Tuple of (text, parser_used, metadata)
        """
        # Check if OCR is needed
        if force_ocr or detect_if_ocr_needed(file_path, settings.MIN_TEXT_THRESHOLD):
            logger.info("Using OCR parser")
            text = await self.tesseract_parser.extract_text(file_path)
            metadata = await self.tesseract_parser.extract_metadata(file_path)
            return text, ParserType.TESSERACT, metadata
        
        # Try PyMuPDF first (fastest)
        logger.info("Trying PyMuPDF parser")
        text = await self.pymupdf_parser.extract_text(file_path)
        
        if self.pymupdf_parser.has_sufficient_text(text, settings.MIN_TEXT_THRESHOLD):
            metadata = await self.pymupdf_parser.extract_metadata(file_path)
            return text, ParserType.PYMUPDF, metadata
        
        # Try pdfplumber as fallback
        logger.info("PyMuPDF insufficient, trying pdfplumber")
        text = await self.pdfplumber_parser.extract_text(file_path)
        
        if self.pdfplumber_parser.has_sufficient_text(text, settings.MIN_TEXT_THRESHOLD):
            metadata = await self.pdfplumber_parser.extract_metadata(file_path)
            return text, ParserType.PDFPLUMBER, metadata
        
        # Last resort: OCR
        logger.info("Text-based parsers failed, falling back to OCR")
        text = await self.tesseract_parser.extract_text(file_path)
        metadata = await self.tesseract_parser.extract_metadata(file_path)
        return text, ParserType.TESSERACT, metadata
    
    async def _extract_data(self, text: str, issuer: CardIssuer) -> dict:
        """
        Extract data using issuer-specific extractor
        
        Returns:
            Dict with data and confidence scores
        """
        # Get extractor for issuer
        extractor = self.extractors.get(issuer)
        
        if not extractor:
            logger.warning(f"No extractor for {issuer.value}, using HDFC as fallback")
            extractor = self.extractors[CardIssuer.HDFC]
        
        # Extract all data
        extracted = extractor.extract_all(text)
        
        # Build Pydantic models
        parsed_data = ParsedData(
            card_issuer=extracted["data"]["card_issuer"],
            card_number=extracted["data"]["card_number"],
            statement_period=extracted["data"]["statement_period"],
            payment_due_date=extracted["data"]["payment_due_date"],
            total_amount_due=extracted["data"]["total_amount_due"]
        )
        
        confidence_scores = ConfidenceScores(
            card_issuer=extracted["confidence"]["card_issuer"],
            card_number=extracted["confidence"]["card_number"],
            statement_period=extracted["confidence"]["statement_period"],
            payment_due_date=extracted["confidence"]["payment_due_date"],
            total_amount_due=extracted["confidence"]["total_amount_due"]
        )
        
        return {
            "data": parsed_data,
            "confidence": confidence_scores
        }
