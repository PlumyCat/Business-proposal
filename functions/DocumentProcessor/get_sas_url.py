"""
Get SAS URL - Génère une URL SAS pour télécharger un document
"""

import json
import logging
import os
from typing import Dict
import azure.functions as func

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.blob_client import get_blob_client
from shared.validators import validate_required_fields
from shared.logger import setup_logger
from shared.config import CONTAINER_TEMPLATES, CONTAINER_DOCUMENTS

logger = setup_logger(__name__)


def get_sas_url(req: func.HttpRequest) -> func.HttpResponse:
    """
    Génère une URL SAS pour télécharger un document

    Permet au bot de générer des liens de téléchargement temporaires
    pour n'importe quel fichier dans le blob storage.

    Request body:
    {
        "file_path": "Eric FER/temp_working.docx",
        "container": "word-templates",  // optional, default: word-templates
        "expiry_hours": 24,  // optional, default: 24
        "permissions": "r"   // optional, default: "r" (read-only)
    }

    Response:
    {
        "success": true,
        "sas_url": "https://...?sas_token",
        "file_path": "Eric FER/temp_working.docx",
        "expiry_hours": 24,
        "container": "word-templates"
    }
    """
    logger.info("Get SAS URL endpoint called")

    try:
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        if not validate_required_fields(req_body, ["file_path"]):
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required field: file_path"
                }),
                status_code=400,
                mimetype="application/json"
            )

        file_path = req_body["file_path"]
        container = req_body.get("container", CONTAINER_TEMPLATES)
        expiry_hours = req_body.get("expiry_hours", 24)
        permissions = req_body.get("permissions", "r")

        # Validate expiry_hours
        if not isinstance(expiry_hours, int) or expiry_hours < 1 or expiry_hours > 168:
            return func.HttpResponse(
                json.dumps({
                    "error": "expiry_hours must be between 1 and 168 (7 days)"
                }),
                status_code=400,
                mimetype="application/json"
            )

        logger.info(f"Generating SAS URL for: {container}/{file_path} (expires in {expiry_hours}h)")

        # Initialize Blob client
        blob_client = get_blob_client()

        # Check if file exists
        if not blob_client.blob_exists(container, file_path):
            return func.HttpResponse(
                json.dumps({
                    "error": "File not found",
                    "file_path": file_path,
                    "container": container
                }),
                status_code=404,
                mimetype="application/json"
            )

        # Generate SAS URL
        sas_url = blob_client.generate_sas_url(
            container_name=container,
            blob_name=file_path,
            expiry_hours=expiry_hours,
            permissions=permissions
        )

        logger.info(f"SAS URL generated successfully for {file_path}")

        # Return success response
        response_data = {
            "success": True,
            "sas_url": sas_url,
            "file_path": file_path,
            "expiry_hours": expiry_hours,
            "container": container
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error generating SAS URL: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to generate SAS URL",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
