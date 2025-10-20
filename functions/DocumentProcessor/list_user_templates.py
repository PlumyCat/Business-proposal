"""
List User Templates - Liste les templates personnels de l'utilisateur
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


def list_user_templates(req: func.HttpRequest) -> func.HttpResponse:
    """
    Liste les templates personnels de l'utilisateur

    Les templates utilisateur sont stockés dans le dossier {user_folder}/
    du container word-templates (fichiers de travail et templates perso).

    Query parameters:
    - user_folder (required): Nom du dossier utilisateur (e.g., "Eric FER")

    Response:
    {
        "success": true,
        "user_folder": "Eric FER",
        "templates": [
            {
                "name": "temp_working.docx",
                "path": "Eric FER/temp_working.docx",
                "size": 45678,
                "last_modified": "2025-10-20T08:30:00Z"
            }
        ],
        "count": 1
    }
    """
    logger.info("List user templates endpoint called")

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

        logger.info(f"Listing templates for user: {user_folder}")

        # Initialize Blob client
        blob_client = get_blob_client()
        container_name = CONTAINER_TEMPLATES

        # Ensure user_folder ends with /
        folder_prefix = user_folder if user_folder.endswith('/') else f"{user_folder}/"

        # List all blobs in user folder
        blobs = blob_client.list_blobs_with_metadata(
            container_name=container_name,
            name_starts_with=folder_prefix
        )

        # Filter and format results
        templates = []
        for blob in blobs:
            # Skip .keep files
            if blob['name'].endswith('.keep'):
                continue

            # Skip if it's just the folder
            if blob['name'] == folder_prefix or blob['name'].endswith('/'):
                continue

            # Extract template name (remove user_folder prefix)
            template_name = blob['name'].replace(folder_prefix, '')

            # Skip if it's in a subfolder
            if '/' in template_name:
                continue

            # Only include .docx files
            if not template_name.lower().endswith('.docx'):
                continue

            templates.append({
                "name": template_name,
                "path": blob['name'],
                "size": blob['size'],
                "last_modified": blob['last_modified'].isoformat() if blob['last_modified'] else None
            })

        logger.info(f"Found {len(templates)} templates in {user_folder}/")

        # Sort by last_modified (most recent first)
        templates.sort(key=lambda x: x['last_modified'] or '', reverse=True)

        # Return success response
        response_data = {
            "success": True,
            "user_folder": user_folder,
            "templates": templates,
            "count": len(templates)
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error listing user templates: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to list user templates",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
