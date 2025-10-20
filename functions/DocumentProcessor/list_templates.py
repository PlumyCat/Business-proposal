"""
List General Templates - Liste les templates généraux disponibles
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
from shared.config import CONTAINER_TEMPLATES

logger = setup_logger(__name__)


def list_general_templates(req: func.HttpRequest) -> func.HttpResponse:
    """
    Liste tous les templates généraux disponibles

    Les templates généraux sont stockés dans le dossier "general/"
    du container word-templates.

    Query parameters: Aucun

    Response:
    {
        "success": true,
        "templates": [
            {
                "name": "template.docx",
                "path": "general/template.docx",
                "size": 45678,
                "last_modified": "2025-10-20T08:30:00Z"
            }
        ],
        "count": 1
    }
    """
    logger.info("List general templates endpoint called")

    try:
        # Initialize Blob client
        blob_client = get_blob_client()
        container_name = CONTAINER_TEMPLATES

        # List all blobs in general/ folder
        blobs = blob_client.list_blobs_with_metadata(
            container_name=container_name,
            name_starts_with="general/"
        )

        # Filter out .keep files and directories
        templates = []
        for blob in blobs:
            # Skip .keep files
            if blob['name'].endswith('.keep'):
                continue

            # Skip if it's just the folder
            if blob['name'] == 'general/' or blob['name'].endswith('/'):
                continue

            # Only include .docx files
            if not blob['name'].lower().endswith('.docx'):
                continue

            # Extract template name (remove "general/" prefix)
            template_name = blob['name'].replace('general/', '')

            templates.append({
                "name": template_name,
                "path": blob['name'],
                "size": blob['size'],
                "last_modified": blob['last_modified'].isoformat() if blob['last_modified'] else None
            })

        logger.info(f"Found {len(templates)} templates in general/")

        # Sort by name
        templates.sort(key=lambda x: x['name'])

        # Return success response
        response_data = {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to list templates",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
