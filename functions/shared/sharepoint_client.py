"""
SharePoint client for file operations and Word to PDF conversion
"""

import os
import logging
import requests
from typing import Optional
from .auth_helper import get_auth_helper
from .logger import setup_logger

logger = setup_logger(__name__)


class SharePointClient:
    """
    SharePoint client for file upload, download, and Word to PDF conversion

    SharePoint can automatically convert Word documents to PDF using its native API.
    This is useful for generating PDF versions of proposals without requiring
    external services or LibreOffice.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize SharePoint client with singleton pattern"""
        if self._initialized:
            return

        self.site_url = os.environ.get("SHAREPOINT_SITE_URL")
        self.temp_library = os.environ.get("SHAREPOINT_TEMP_LIBRARY", "TempConversions")

        if not self.site_url:
            logger.warning("SHAREPOINT_SITE_URL not configured")

        self.auth_helper = get_auth_helper()
        self._initialized = True

        logger.info(f"SharePointClient initialized for site: {self.site_url}")

    def _get_access_token(self) -> str:
        """
        Get access token for SharePoint API

        Returns:
            Access token string
        """
        # SharePoint scope format: https://{tenant}.sharepoint.com/.default
        sharepoint_scope = f"{self.site_url}/.default"
        return self.auth_helper.get_access_token(sharepoint_scope)

    def _get_headers(self) -> dict:
        """
        Get HTTP headers with authentication for SharePoint API

        Returns:
            Dictionary of headers
        """
        access_token = self._get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose"
        }

    def upload_file(
        self,
        file_name: str,
        file_content: bytes,
        library_name: Optional[str] = None
    ) -> dict:
        """
        Upload file to SharePoint library

        Args:
            file_name: Name of the file to upload
            file_content: File content as bytes
            library_name: SharePoint library name (defaults to temp_library)

        Returns:
            Dictionary with file metadata including ServerRelativeUrl

        Raises:
            Exception if upload fails
        """
        library = library_name or self.temp_library

        # SharePoint REST API endpoint for file upload
        upload_url = (
            f"{self.site_url}/_api/web/GetFolderByServerRelativeUrl('{library}')"
            f"/Files/add(url='{file_name}',overwrite=true)"
        )

        logger.info(f"Uploading file to SharePoint: {file_name}")

        headers = self._get_headers()
        headers["Content-Type"] = "application/octet-stream"

        try:
            response = requests.post(
                upload_url,
                headers=headers,
                data=file_content,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            file_data = result.get("d", {})

            logger.info(f"File uploaded successfully: {file_data.get('ServerRelativeUrl')}")
            return file_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload file to SharePoint: {str(e)}")
            raise Exception(f"SharePoint upload failed: {str(e)}")

    def download_file_as_pdf(self, server_relative_url: str) -> bytes:
        """
        Download a Word document from SharePoint as PDF

        SharePoint automatically converts .docx files to PDF when requested
        with the appropriate format parameter.

        Args:
            server_relative_url: Server-relative URL of the Word file

        Returns:
            PDF file content as bytes

        Raises:
            Exception if download or conversion fails
        """
        # SharePoint PDF conversion endpoint
        # Format: /_layouts/15/download.aspx?SourceUrl={url}&format=pdf
        pdf_url = f"{self.site_url}/_layouts/15/download.aspx"

        params = {
            "SourceUrl": server_relative_url,
            "format": "pdf"
        }

        logger.info(f"Downloading file as PDF: {server_relative_url}")

        headers = self._get_headers()
        headers.pop("Content-Type", None)  # Remove Content-Type for download

        try:
            response = requests.get(
                pdf_url,
                headers=headers,
                params=params,
                timeout=120  # PDF conversion can take time
            )
            response.raise_for_status()

            pdf_content = response.content
            logger.info(f"PDF downloaded successfully ({len(pdf_content)} bytes)")
            return pdf_content

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download PDF from SharePoint: {str(e)}")
            raise Exception(f"SharePoint PDF download failed: {str(e)}")

    def delete_file(self, server_relative_url: str) -> bool:
        """
        Delete file from SharePoint

        Args:
            server_relative_url: Server-relative URL of the file to delete

        Returns:
            True if deletion successful, False otherwise
        """
        delete_url = f"{self.site_url}/_api/web/GetFileByServerRelativeUrl('{server_relative_url}')"

        logger.info(f"Deleting file from SharePoint: {server_relative_url}")

        headers = self._get_headers()
        headers["X-HTTP-Method"] = "DELETE"
        headers["IF-MATCH"] = "*"

        try:
            response = requests.post(
                delete_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            logger.info("File deleted successfully")
            return True

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to delete file from SharePoint: {str(e)}")
            return False

    def convert_word_to_pdf(
        self,
        word_content: bytes,
        file_name: str
    ) -> bytes:
        """
        Convert Word document to PDF using SharePoint

        Process:
        1. Upload Word file to temporary SharePoint library
        2. Request file as PDF (SharePoint converts automatically)
        3. Download the PDF
        4. Delete temporary Word file

        Args:
            word_content: Word document content as bytes
            file_name: Name for the temporary file (should end with .docx)

        Returns:
            PDF content as bytes

        Raises:
            Exception if conversion fails
        """
        if not self.site_url:
            raise Exception("SharePoint site URL not configured (SHAREPOINT_SITE_URL)")

        logger.info(f"Starting Word to PDF conversion via SharePoint: {file_name}")

        try:
            # Step 1: Upload Word file
            uploaded_file = self.upload_file(
                file_name=file_name,
                file_content=word_content
            )

            server_relative_url = uploaded_file.get("ServerRelativeUrl")
            if not server_relative_url:
                raise Exception("Failed to get ServerRelativeUrl from upload response")

            # Step 2: Download as PDF
            pdf_content = self.download_file_as_pdf(server_relative_url)

            # Step 3: Clean up temporary file
            self.delete_file(server_relative_url)

            logger.info("Word to PDF conversion completed successfully")
            return pdf_content

        except Exception as e:
            logger.error(f"Word to PDF conversion failed: {str(e)}")
            raise


def get_sharepoint_client() -> SharePointClient:
    """
    Get singleton instance of SharePointClient

    Returns:
        SharePointClient instance
    """
    return SharePointClient()
