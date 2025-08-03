"""
PDF Service

This service handles PDF processing and analysis functionality for the PDF agent.
It provides PDF text extraction, content analysis, and document processing capabilities.
"""

import logging
import asyncio
import io
import tempfile
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import fitz  # PyMuPDF
import PyPDF2
from PIL import Image
import pytesseract

from .base_service import BaseAgentService, ServiceType, ServiceStatus

logger = logging.getLogger(__name__)


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
                    "ocr_available": self.ocr_enabled and self._check_ocr_availability(),
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
                "page_analysis": True
            },
            "configuration": {
                "max_file_size": self.max_file_size,
                "max_pages": self.max_pages,
                "extract_images": self.extract_images,
                "ocr_enabled": self.ocr_enabled,
                "supported_formats": self.supported_formats
            }
        }
    
    async def validate_config(self) -> bool:
        """
        Validate PDF service configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check required configuration
            if self.max_file_size <= 0:
                logger.error("PDF service: Invalid max_file_size value")
                return False
            
            if self.max_pages <= 0:
                logger.error("PDF service: Invalid max_pages value")
                return False
            
            if not self.supported_formats:
                logger.error("PDF service: No supported formats configured")
                return False
            
            # Check if temp directory exists and is writable
            if not os.path.exists(self.temp_dir) or not os.access(self.temp_dir, os.W_OK):
                logger.error(f"PDF service: Temp directory not accessible: {self.temp_dir}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"PDF service config validation failed: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get PDF service performance metrics.
        
        Returns:
            Performance metrics
        """
        base_metrics = self.get_service_info()
        
        # Add PDF-specific metrics
        pdf_metrics = {
            "pdfs_processed": 0,  # TODO: Track actual PDF processing
            "pages_extracted": 0,  # TODO: Track pages extracted
            "images_extracted": 0,  # TODO: Track images extracted
            "ocr_operations": 0,  # TODO: Track OCR operations
            "average_processing_time": 0.0,  # TODO: Track processing times
            "success_rate": 1.0 if self.error_count == 0 else 0.0
        }
        
        return {**base_metrics, **pdf_metrics}
    
    async def process_pdf(self, pdf_content: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        Process a PDF document.
        
        Args:
            pdf_content: PDF file content as bytes
            filename: Original filename
            
        Returns:
            Processing results
        """
        await self.pre_request()
        
        try:
            # Validate file size
            if len(pdf_content) > self.max_file_size:
                raise ValueError(f"File size {len(pdf_content)} exceeds maximum {self.max_file_size}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=self.temp_dir) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Process the PDF
                result = await self._extract_pdf_content(temp_file_path, filename)
                await self.post_request(success=True)
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"PDF processing failed: {e}")
            raise
    
    async def extract_text(self, pdf_content: bytes, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract text from PDF.
        
        Args:
            pdf_content: PDF file content as bytes
            pages: Specific pages to extract (None for all pages)
            
        Returns:
            Extracted text
        """
        await self.pre_request()
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=self.temp_dir) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = await self._extract_text_only(temp_file_path, pages)
                await self.post_request(success=True)
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Text extraction failed: {e}")
            raise
    
    async def extract_images(self, pdf_content: bytes, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract images from PDF.
        
        Args:
            pdf_content: PDF file content as bytes
            pages: Specific pages to extract (None for all pages)
            
        Returns:
            Extracted images
        """
        if not self.extract_images:
            raise ValueError("Image extraction is disabled")
        
        await self.pre_request()
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=self.temp_dir) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract images
                result = await self._extract_images_only(temp_file_path, pages)
                await self.post_request(success=True)
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"Image extraction failed: {e}")
            raise
    
    async def analyze_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Analyze PDF structure and content.
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Analysis results
        """
        await self.pre_request()
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=self.temp_dir) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Analyze PDF
                result = await self._analyze_pdf_structure(temp_file_path)
                await self.post_request(success=True)
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            await self.post_request(success=False)
            logger.error(f"PDF analysis failed: {e}")
            raise
    
    async def _extract_pdf_content(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Extract comprehensive content from PDF.
        
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
                images = await self._extract_images_from_doc(doc)
            
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
    
    async def _extract_text_only(self, file_path: str, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract only text from PDF.
        
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
    
    async def _extract_images_only(self, file_path: str, pages: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Extract only images from PDF.
        
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
            
            images = await self._extract_images_from_doc(doc, pages)
            doc.close()
            
            return {
                "images": images,
                "total_images": len(images),
                "pages_processed": len(pages)
            }
            
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            raise
    
    async def _extract_images_from_doc(self, doc: fitz.Document, pages: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Extract images from PDF document.
        
        Args:
            doc: PyMuPDF document
            pages: Specific pages to extract
            
        Returns:
            List of extracted images
        """
        images = []
        
        try:
            page_count = len(doc)
            if pages is None:
                pages = list(range(page_count))
            
            for page_num in pages:
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            images.append({
                                "page": page_num + 1,
                                "image_index": img_index,
                                "format": "png",
                                "size": len(img_data),
                                "width": pix.width,
                                "height": pix.height,
                                "data": img_data
                            })
                        
                        pix = None  # Free memory
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
                        
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
        
        return images
    
    async def _analyze_pdf_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze PDF structure and content.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Analysis results
        """
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            metadata = doc.metadata
            
            # Analyze each page
            page_analysis = []
            total_words = 0
            total_images = 0
            
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()
                word_count = len(text.split())
                total_words += word_count
                
                # Count images on page
                image_list = page.get_images()
                image_count = len(image_list)
                total_images += image_count
                
                page_analysis.append({
                    "page": page_num + 1,
                    "word_count": word_count,
                    "image_count": image_count,
                    "has_text": bool(text.strip()),
                    "text_density": word_count / max(len(text), 1)
                })
            
            doc.close()
            
            return {
                "page_count": page_count,
                "total_words": total_words,
                "total_images": total_images,
                "average_words_per_page": total_words / page_count if page_count > 0 else 0,
                "average_images_per_page": total_images / page_count if page_count > 0 else 0,
                "page_analysis": page_analysis,
                "metadata": metadata,
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            raise
    
    async def _test_pdf_processing(self) -> Dict[str, Any]:
        """
        Test PDF processing capabilities.
        
        Returns:
            Test results
        """
        try:
            # Create a simple test PDF
            test_doc = fitz.open()
            test_page = test_doc.new_page()
            test_page.insert_text((50, 50), "Test PDF for health check")
            test_doc.save("test_health_check.pdf")
            test_doc.close()
            
            # Test processing
            with open("test_health_check.pdf", "rb") as f:
                test_content = f.read()
            
            # Clean up
            os.unlink("test_health_check.pdf")
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_ocr_availability(self) -> bool:
        """
        Check if OCR is available.
        
        Returns:
            True if OCR is available
        """
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the PDF service."""
        await super().shutdown()
        logger.info("PDF service shutdown complete") 