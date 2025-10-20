"""
List Created Documents - Liste les documents finaux créés par l'utilisateur
"""

import json
import logging
import os
from typing import List, Dict
import azure.functions as func

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.blob_client import get_blob_client
from shared.logger import setup_logger
from shared.config import CONTAINER_DOCUMENTS

logger = setup_logger(__name__)


def list_created_documents(req: func.HttpRequest) -> func.HttpResponse:
    """
    Liste tous les documents finaux créés (Word + PDF)

    Les documents finaux sont stockés dans le dossier {user_folder}/
    du container word-documents.

    Query parameters:
    - user_folder (required): Nom du dossier utilisateur (e.g., "Eric FER")

    Response:
    {
        "success": true,
        "user_folder": "Eric FER",
        "documents": [
            {
                "name": "proposition_20251020_0830.docx",
                "path": "Eric FER/proposition_20251020_0830.docx",
                "size": 45678,
                "last_modified": "2025-10-20T08:30:00Z",
                "type": "word"
            },
            {
                "name": "proposition_20251020_0830.pdf",
                "path": "Eric FER/proposition_20251020_0830.pdf",
                "size": 123456,
                "last_modified": "2025-10-20T08:30:00Z",
                "type": "pdf"
            }
        ],
        "count": 2
    }
    """
    logger.info("List created documents endpoint called")

    try:
        # Get query parameter
        user_folder = req.params.get('user_folder')

        if not user_folder:
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required parameter: user_folder"
                }),
                status_code=400,
                mimetype="application/json"
            )

        logger.info(f"Listing created documents for user: {user_folder}")

        # Initialize Blob client
        blob_client = get_blob_client()
        container_name = CONTAINER_DOCUMENTS

        # Ensure user_folder ends with /
        folder_prefix = user_folder if user_folder.endswith('/') else f"{user_folder}/"

        # List all blobs in user folder
        blobs = blob_client.list_blobs_with_metadata(
            container_name=container_name,
            name_starts_with=folder_prefix
        )

        # Filter and format results
        documents = []
        for blob in blobs:
            # Skip .keep files
            if blob['name'].endswith('.keep'):
                continue

            # Skip if it's just the folder
            if blob['name'] == folder_prefix or blob['name'].endswith('/'):
                continue

            # Extract document name (remove user_folder prefix)
            document_name = blob['name'].replace(folder_prefix, '')

            # Skip if it's in a subfolder
            if '/' in document_name:
                continue

            # Determine document type
            doc_type = None
            if document_name.lower().endswith('.docx'):
                doc_type = "word"
            elif document_name.lower().endswith('.pdf'):
                doc_type = "pdf"

            documents.append({
                "name": document_name,
                "path": blob['name'],
                "size": blob['size'],
                "last_modified": blob['last_modified'].isoformat() if blob['last_modified'] else None,
                "type": doc_type
            })

        logger.info(f"Found {len(documents)} created documents in {user_folder}/")

        # Sort by last_modified (most recent first)
        documents.sort(key=lambda x: x['last_modified'] or '', reverse=True)

        # Return success response
        response_data = {
            "success": True,
            "user_folder": user_folder,
            "documents": documents,
            "count": len(documents)
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error listing user documents: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to list user documents",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
