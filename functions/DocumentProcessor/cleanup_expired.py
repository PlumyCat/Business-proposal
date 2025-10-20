"""
Cleanup Expired Documents - Supprime les documents de plus de 24h
"""

import json
import logging
import os
from typing import Dict, List
from datetime import datetime, timedelta, timezone
import azure.functions as func

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.blob_client import get_blob_client
from shared.logger import setup_logger
from shared.config import CONTAINER_TEMPLATES

logger = setup_logger(__name__)


def cleanup_expired(req: func.HttpRequest) -> func.HttpResponse:
    """
    Supprime les documents temporaires de plus de 24h

    Query parameters:
    - user_folder (optional): Si spécifié, nettoie uniquement ce dossier
    - max_age_hours (optional): Âge maximum en heures (défaut: 24h)

    Response:
    {
        "success": true,
        "deleted_count": 5,
        "deleted_files": ["Eric FER/temp_working.docx", ...]
    }
    """
    logger.info("Cleanup expired documents endpoint called")

    try:
        # Get query parameters
        user_folder = req.params.get('user_folder')
        max_age_hours = int(req.params.get('max_age_hours', 24))

        logger.info(f"Cleanup: user_folder={user_folder}, max_age_hours={max_age_hours}")

        # Initialize Blob client
        blob_client = get_blob_client()
        container_name = CONTAINER_TEMPLATES

        # Calculate cutoff time
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        # List blobs with metadata
        name_prefix = user_folder if user_folder else None
        blobs = blob_client.list_blobs_with_metadata(container_name, name_starts_with=name_prefix)

        deleted_files = []
        for blob in blobs:
            # Check if blob is older than cutoff time
            blob_age = blob['last_modified']

            # Make cutoff_time offset-aware if it isn't already
            if blob_age.tzinfo is None:
                blob_age = blob_age.replace(tzinfo=timezone.utc)

            if blob_age < cutoff_time:
                # Skip general templates (only delete user files)
                if blob['name'].startswith('general/'):
                    continue

                # Delete the blob
                try:
                    blob_client.delete_blob(container_name, blob['name'])
                    deleted_files.append(blob['name'])
                    logger.info(f"Deleted expired file: {blob['name']} (age: {blob_age})")
                except Exception as e:
                    logger.error(f"Failed to delete {blob['name']}: {str(e)}")

        logger.info(f"Cleanup complete: {len(deleted_files)} files deleted")

        # Return success response
        response_data = {
            "success": True,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "cutoff_time": cutoff_time.isoformat(),
            "max_age_hours": max_age_hours
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error cleaning up expired documents: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to cleanup expired documents",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
