"""
Azure Blob Storage Client
Gère les opérations de lecture/écriture sur Azure Blob Storage
"""

import os
import logging
from typing import Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, AzureError

logger = logging.getLogger(__name__)


class BlobStorageClient:
    """Client pour interagir avec Azure Blob Storage"""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize Blob Storage client

        Args:
            connection_string: Azure Storage connection string
                              Si None, utilise la variable d'environnement BLOB_STORAGE_CONNECTION_STRING
        """
        self.connection_string = connection_string or os.getenv("BLOB_STORAGE_CONNECTION_STRING")

        if not self.connection_string:
            raise ValueError("Blob Storage connection string is required")

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Container names from environment or defaults
        self.container_templates = os.getenv("BLOB_CONTAINER_TEMPLATES", "templates")
        self.container_devis = os.getenv("BLOB_CONTAINER_DEVIS", "devis-sources")
        self.container_proposals = os.getenv("BLOB_CONTAINER_PROPOSALS", "propositions-generated")

    def get_blob_client(self, container_name: str, blob_name: str) -> BlobClient:
        """
        Get a BlobClient for a specific blob

        Args:
            container_name: Name of the container
            blob_name: Name of the blob

        Returns:
            BlobClient instance
        """
        return self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    def upload_blob(
        self,
        container_name: str,
        blob_name: str,
        data: bytes,
        overwrite: bool = True
    ) -> str:
        """
        Upload data to blob storage

        Args:
            container_name: Name of the container
            blob_name: Name of the blob
            data: Binary data to upload
            overwrite: Whether to overwrite if blob exists

        Returns:
            Blob URL
        """
        try:
            blob_client = self.get_blob_client(container_name, blob_name)
            blob_client.upload_blob(data, overwrite=overwrite)

            logger.info(f"Uploaded blob: {blob_name} to container: {container_name}")
            return blob_client.url

        except AzureError as e:
            logger.error(f"Failed to upload blob {blob_name}: {str(e)}")
            raise

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        """
        Download blob from storage

        Args:
            container_name: Name of the container
            blob_name: Name of the blob

        Returns:
            Blob content as bytes
        """
        try:
            blob_client = self.get_blob_client(container_name, blob_name)
            download_stream = blob_client.download_blob()
            content = download_stream.readall()

            logger.info(f"Downloaded blob: {blob_name} from container: {container_name}")
            return content

        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name} in container: {container_name}")
            raise
        except AzureError as e:
            logger.error(f"Failed to download blob {blob_name}: {str(e)}")
            raise

    def blob_exists(self, container_name: str, blob_name: str) -> bool:
        """
        Check if a blob exists

        Args:
            container_name: Name of the container
            blob_name: Name of the blob

        Returns:
            True if blob exists, False otherwise
        """
        try:
            blob_client = self.get_blob_client(container_name, blob_name)
            return blob_client.exists()
        except AzureError as e:
            logger.error(f"Error checking blob existence: {str(e)}")
            return False

    def delete_blob(self, container_name: str, blob_name: str) -> bool:
        """
        Delete a blob

        Args:
            container_name: Name of the container
            blob_name: Name of the blob

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            blob_client = self.get_blob_client(container_name, blob_name)
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name} from container: {container_name}")
            return True
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {blob_name}")
            return False
        except AzureError as e:
            logger.error(f"Failed to delete blob {blob_name}: {str(e)}")
            raise

    def list_blobs(self, container_name: str, name_starts_with: Optional[str] = None) -> list[str]:
        """
        List all blobs in a container

        Args:
            container_name: Name of the container
            name_starts_with: Filter blobs by name prefix

        Returns:
            List of blob names
        """
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blobs = container_client.list_blobs(name_starts_with=name_starts_with)
            blob_names = [blob.name for blob in blobs]

            logger.info(f"Listed {len(blob_names)} blobs from container: {container_name}")
            return blob_names

        except AzureError as e:
            logger.error(f"Failed to list blobs in container {container_name}: {str(e)}")
            raise

    def get_blob_url(self, container_name: str, blob_name: str) -> str:
        """
        Get the URL of a blob

        Args:
            container_name: Name of the container
            blob_name: Name of the blob

        Returns:
            Blob URL
        """
        blob_client = self.get_blob_client(container_name, blob_name)
        return blob_client.url


# Singleton instance
_blob_client_instance: Optional[BlobStorageClient] = None


def get_blob_client() -> BlobStorageClient:
    """
    Get singleton instance of BlobStorageClient

    Returns:
        BlobStorageClient instance
    """
    global _blob_client_instance

    if _blob_client_instance is None:
        _blob_client_instance = BlobStorageClient()

    return _blob_client_instance
