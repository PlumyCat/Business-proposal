"""
Delete Template - Supprime un template ou document du blob storage
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
from shared.config import CONTAINER_TEMPLATES

logger = setup_logger(__name__)


def delete_template(req: func.HttpRequest) -> func.HttpResponse:
    """
    Supprime un template ou document du blob storage

    Request body:
    {
        "file_path": "Eric FER/temp_working.docx"
    }

    Response:
    {
        "success": true,
        "deleted_file": "Eric FER/temp_working.docx"
    }
    """
    logger.info("Delete template endpoint called")

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

        logger.info(f"Deleting file: {file_path}")

        # Initialize Blob client
        blob_client = get_blob_client()
        container_name = CONTAINER_TEMPLATES

        # Check if file exists
        if not blob_client.blob_exists(container_name, file_path):
            return func.HttpResponse(
                json.dumps({
                    "error": "File not found",
                    "file_path": file_path
                }),
                status_code=404,
                mimetype="application/json"
            )

        # Delete the file
        blob_client.delete_blob(container_name, file_path)

        logger.info(f"File deleted successfully: {file_path}")

        # Return success response
        response_data = {
            "success": True,
            "deleted_file": file_path
        }

        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to delete template",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
