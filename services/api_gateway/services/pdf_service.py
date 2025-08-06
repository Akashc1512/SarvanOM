"""
PDF Service

This service handles PDF processing and analysis functionality for the PDF agent.
It provides PDF text extraction, content analysis, and document processing capabilities.
"""

import logging
from shared.core.unified_logging import get_logger
import asyncio
import io
import tempfile
import os
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import fitz  # PyMuPDF
import PyPDF2
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from .base_service import BaseAgentService, ServiceType, ServiceStatus
from shared.core.api.exceptions import (
    ExternalServiceError, ValidationError, ResourceNotFoundError,
    QueryProcessingError
)
from services.api_gateway.middleware.error_handling import (
    handle_service_error, validate_service_response, log_service_operation
)

logger = get_logger(__name__)


class PDFService(BaseAgentService):
    """
    PDF service for document processing and analysis.
    
    This service provides PDF text extraction, content analysis,
    and document processing capabilities for the PDF agent.
    """
    
    def __init__(self, service_type: ServiceType, config: Optional[Dict[str, Any]] = None):
        """Initialize the PDF service."""
        super().__init__(service_type, config)
        self.max_file_size = self.get_config("max_file_size", 50 * 1024 * 1024)  # 50MB
        self.max_pages = self.get_config("max_pages", 100)
        self.extract_images = self.get_config("extract_images", True)
        self.ocr_enabled = self.get_config("ocr_enabled", True)
        self.supported_formats = self.get_config("supported_formats", [".pdf"])
        self.temp_dir = self.get_config("temp_dir", tempfile.gettempdir())
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("PDF service initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check PDF service health.
        
        Returns:
            Health status and metrics
        """
        try:
            # Test PDF processing capabilities
            test_result = await self._test_pdf_processing()
            
            if test_result["success"]:
                self.update_status(ServiceStatus.HEALTHY)
                return {
                    "healthy": True,
                    "pdf_processing": "OK",
                    "ocr_available": self.ocr_enabled and await self._check_ocr_availability_async(),
                    "max_file_size": self.max_file_size,
                    "max_pages": self.max_pages,
                    "supported_formats": self.supported_formats
                }
            else:
                self.update_status(ServiceStatus.DEGRADED)
                return {
                    "healthy": False,
                    "pdf_processing": "FAILED",
                    "error": test_result.get("error", "Unknown error")
                }
                
        except Exception as e:
            self.update_status(ServiceStatus.UNHEALTHY)
            logger.error(f"PDF service health check failed: {e}")
            return {
                "healthy": False,
                "pdf_processing": "FAILED",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get detailed PDF service status.
        
        Returns:
            Service status information
        """
        health_info = await self.health_check()
        service_info = self.get_service_info()
        
        return {
            **service_info,
            **health_info,
            "capabilities": {
                "text_extraction": True,
                "image_extraction": self.extract_images,
                "ocr_processing": self.ocr_enabled,
                "metadata_extraction": True,
                "background_processing": True
            }
        }
    
    async def validate_config(self) -> bool:
        """
        Validate PDF service configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check file size limits
            if self.max_file_size <= 0:
                logger.error("PDF service: Invalid max_file_size value")
                return False
            
            if self.max_pages <= 0:
                logger.error("PDF service: Invalid max_pages value")
                return False
            
            # Check OCR availability if enabled
            if self.ocr_enabled:
                ocr_available = await self._check_ocr_availability_async()
                if not ocr_available:
                    logger.warning("PDF service: OCR enabled but Tesseract not available")
            
            # Check temp directory
            if not os.path.exists(self.temp_dir):
                logger.error(f"PDF service: Temp directory does not exist: {self.temp_dir}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"PDF service configuration validation failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get PDF service metrics.
        
        Returns:
            Service metrics
        """
        try:
            metrics = {
                "files_processed": 0,  # TODO: Implement counter
                "average_processing_time": 0.0,  # TODO: Implement timing
                "ocr_usage_rate": 0.0,  # TODO: Implement OCR tracking
                "error_rate": 0.0,  # TODO: Implement error tracking
                "max_file_size": self.max_file_size,
                "max_pages": self.max_pages,
                "thread_pool_size": self.executor._max_workers
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get PDF service metrics: {e}")
            return {"error": str(e)}
    
    async def process_pdf(self, pdf_content: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Process PDF content with comprehensive error handling.
        
        Args:
            pdf_content: PDF file content as bytes
            filename: Name of the PDF file
            
        Returns:
            PDF processing results
            
        Raises:
            ValidationError: If PDF content is invalid
            ExternalServiceError: If PDF processing fails
        """
        start_time = time.time()
        request_id = f"pdf_process_{int(start_time * 1000)}"
        
        try:
            # Validate inputs
            if not pdf_content:
                raise ValidationError(
                    field="pdf_content",
                    message="PDF content cannot be empty",
                    value=None
                )
            
            if len(pdf_content) > self.max_file_size:
                raise ValidationError(
                    field="pdf_content",
                    message=f"PDF file size exceeds maximum limit of {self.max_file_size} bytes",
                    value=len(pdf_content)
                )
            
            if not filename or not filename.strip():
                raise ValidationError(
                    field="filename",
                    message="Filename is required",
                    value=filename
                )
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False, dir=self.temp_dir
            ) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Process PDF in background thread
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    partial(self._extract_pdf_content_sync, temp_file_path, filename)
                )
                
                # Validate response
                validate_service_response(result, "PDFService", "process_pdf", dict)
                
                # Log successful operation
                duration = time.time() - start_time
                log_service_operation(
                    "PDFService",
                    "process_pdf",
                    True,
                    duration,
                    request_id,
                    {
                        "filename": filename,
                        "file_size": len(pdf_content),
                        "pages": result.get("pages", 0)
                    }
                )
                
                return {
                    "success": True,
                    "data": result,
                    "filename": filename,
                    "processing_time": duration,
                    "request_id": request_id
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass  # File might already be deleted
                    
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            log_service_operation(
                "PDFService",
                "process_pdf",
                False,
                duration,
                request_id,
                {"filename": filename, "timeout": True}
            )
            raise ExternalServiceError(
                service="PDFService",
                operation="process_pdf",
                error="PDF processing timeout",
                retryable=True
            )
            
        except (ValueError, TypeError) as e:
            duration = time.time() - start_time
            log_service_operation(
                "PDFService",
                "process_pdf",
                False,
                duration,
                request_id,
                {"filename": filename, "validation_error": str(e)}
            )
            raise ValidationError(
                field="pdf_content",
                message=f"Invalid PDF content: {str(e)}",
                value=filename
            )
            
        except Exception as e:
            duration = time.time() - start_time
            log_service_operation(
                "PDFService",
                "process_pdf",
                False,
                duration,
                request_id,
                {"filename": filename, "error": str(e)}
            )
            # Use the error handling utility
            handle_service_error("PDFService", "process_pdf", e, request_id)
            raise  # Re-raise the converted exception
    
    async def extract_text(self, pdf_content: bytes, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract text from PDF asynchronously.
        
        Args:
            pdf_content: PDF file content
            pages: Specific pages to extract
            
        Returns:
            Extracted text
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text in background task
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    partial(self._extract_text_only_sync, temp_file_path, pages)
                )
                
                return {
                    "success": True,
                    "result": result
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def extract_images(self, pdf_content: bytes, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract images from PDF asynchronously.
        
        Args:
            pdf_content: PDF file content
            pages: Specific pages to extract
            
        Returns:
            Extracted images
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract images in background task
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    partial(self._extract_images_only_sync, temp_file_path, pages)
                )
                
                return {
                    "success": True,
                    "result": result
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Analyze PDF structure asynchronously.
        
        Args:
            pdf_content: PDF file content
            
        Returns:
            Analysis results
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Analyze PDF in background task
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    partial(self._analyze_pdf_structure_sync, temp_file_path)
                )
                
                return {
                    "success": True,
                    "result": result
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_pdf_content_sync(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Extract comprehensive content from PDF (synchronous version for background task).
        
        Args:
            file_path: Path to PDF file
            filename: Original filename
            
        Returns:
            Extracted content
        """
        try:
            doc = fitz.open(file_path)
            
            # Basic document info
            metadata = doc.metadata
            page_count = len(doc)
            
            if page_count > self.max_pages:
                raise ValueError(f"PDF has {page_count} pages, exceeds maximum {self.max_pages}")
            
            # Extract text from all pages
            text_content = []
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                text_content.append({
                    "page": page_num + 1,
                    "text": text,
                    "word_count": len(text.split())
                })
            
            # Extract images if enabled
            images = []
            if self.extract_images:
                images = self._extract_images_from_doc_sync(doc)
            
            # Extract metadata
            doc_info = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", "")
            }
            
            doc.close()
            
            return {
                "filename": filename,
                "page_count": page_count,
                "total_words": sum(page["word_count"] for page in text_content),
                "metadata": doc_info,
                "text_content": text_content,
                "images": images,
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PDF content extraction failed: {e}")
            raise
    
    def _extract_text_only_sync(self, file_path: str, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract only text from PDF (synchronous version for background task).
        
        Args:
            file_path: Path to PDF file
            pages: Specific pages to extract
            
        Returns:
            Extracted text
        """
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            
            if pages is None:
                pages = list(range(page_count))
            else:
                # Validate page numbers
                pages = [p for p in pages if 0 <= p < page_count]
            
            text_content = []
            for page_num in pages:
                page = doc[page_num]
                text = page.get_text()
                text_content.append({
                    "page": page_num + 1,
                    "text": text,
                    "word_count": len(text.split())
                })
            
            doc.close()
            
            return {
                "pages": text_content,
                "total_pages": len(pages),
                "total_words": sum(page["word_count"] for page in text_content)
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    def _extract_images_only_sync(self, file_path: str, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract only images from PDF (synchronous version for background task).
        
        Args:
            file_path: Path to PDF file
            pages: Specific pages to extract
            
        Returns:
            Extracted images
        """
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            
            if pages is None:
                pages = list(range(page_count))
            else:
                # Validate page numbers
                pages = [p for p in pages if 0 <= p < page_count]
            
            images = self._extract_images_from_doc_sync(doc, pages)
            doc.close()
            
            return {
                "images": images,
                "total_images": len(images),
                "pages_processed": len(pages)
            }
            
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            raise
    
    def _extract_images_from_doc_sync(self, doc: fitz.Document, pages: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Extract images from PDF document (synchronous version).
        
        Args:
            doc: PDF document
            pages: Specific pages to extract
            
        Returns:
            List of extracted images
        """
        images = []
        
        if pages is None:
            pages = list(range(len(doc)))
        
        for page_num in pages:
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                    else:  # CMYK: convert to RGB
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        img_data = pix1.tobytes("png")
                        pix1 = None
                    
                    images.append({
                        "page": page_num + 1,
                        "image_index": img_index,
                        "width": pix.width,
                        "height": pix.height,
                        "format": "png",
                        "data": img_data,
                        "size_bytes": len(img_data)
                    })
                    
                    pix = None
                    
                except Exception as e:
                    logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
                    continue
        
        return images
    
    def _analyze_pdf_structure_sync(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze PDF structure (synchronous version for background task).
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Analysis results
        """
        try:
            doc = fitz.open(file_path)
            
            # Basic structure analysis
            page_count = len(doc)
            toc = doc.get_toc()
            
            # Analyze text distribution
            text_stats = {
                "total_pages": page_count,
                "pages_with_text": 0,
                "total_words": 0,
                "average_words_per_page": 0
            }
            
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                word_count = len(text.split())
                
                if word_count > 0:
                    text_stats["pages_with_text"] += 1
                    text_stats["total_words"] += word_count
            
            if text_stats["pages_with_text"] > 0:
                text_stats["average_words_per_page"] = text_stats["total_words"] / text_stats["pages_with_text"]
            
            # Analyze images
            image_stats = {
                "total_images": 0,
                "pages_with_images": 0,
                "average_images_per_page": 0
            }
            
            for page_num in range(page_count):
                page = doc[page_num]
                image_list = page.get_images()
                
                if image_list:
                    image_stats["total_images"] += len(image_list)
                    image_stats["pages_with_images"] += 1
            
            if image_stats["pages_with_images"] > 0:
                image_stats["average_images_per_page"] = image_stats["total_images"] / image_stats["pages_with_images"]
            
            doc.close()
            
            return {
                "text_analysis": text_stats,
                "image_analysis": image_stats,
                "table_of_contents": toc,
                "file_size": os.path.getsize(file_path),
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PDF structure analysis failed: {e}")
            raise
    
    async def _test_pdf_processing(self) -> Dict[str, Any]:
        """
        Test PDF processing capabilities asynchronously.
        
        Returns:
            Test results
        """
        try:
            # Create a simple test PDF
            test_pdf_content = self._create_test_pdf()
            
            # Test processing
            result = await self.process_pdf(test_pdf_content, "test.pdf")
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "PDF processing test successful"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_ocr_availability_async(self) -> bool:
        """
        Check OCR availability asynchronously.
        
        Returns:
            True if OCR is available
        """
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, self._check_ocr_availability_sync)
        except Exception as e:
            logger.error(f"OCR availability check failed: {e}")
            return False
    
    def _check_ocr_availability_sync(self) -> bool:
        """
        Check OCR availability (synchronous version).
        
        Returns:
            True if OCR is available
        """
        try:
            # Check if Tesseract is available
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def _create_test_pdf(self) -> bytes:
        """
        Create a simple test PDF for testing.
        
        Returns:
            PDF content as bytes
        """
        try:
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "Test PDF for processing validation")
            pdf_bytes = doc.write()
            doc.close()
            return pdf_bytes
        except Exception as e:
            logger.error(f"Failed to create test PDF: {e}")
            # Return minimal PDF content
            return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n149\n%%EOF\n"
    
    async def shutdown(self) -> None:
        """Shutdown PDF service."""
        try:
            # Shutdown thread pool
            self.executor.shutdown(wait=True)
            logger.info("PDF service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during PDF service shutdown: {e}") 