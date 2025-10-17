"""
Save proposal metadata to Dataverse
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
import azure.functions as func

# Import shared modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.dataverse_client import get_dataverse_client
from shared.validators import validate_required_fields
from shared.logger import setup_logger

logger = setup_logger(__name__)


def save_proposal(req: func.HttpRequest) -> func.HttpResponse:
    """
    Save proposal metadata to Dataverse cr_propositions table

    Request body:
    {
        "proposal_number": "PROP-20250117-ABC123",
        "client_info": {
            "name": "Client Name",
            "contact": "John Doe",
            "email": "john@example.com"
        },
        "word_url": "https://...",
        "pdf_url": "https://...",
        "word_blob_name": "PROP-20250117-ABC123.docx",
        "pdf_blob_name": "PROP-20250117-ABC123.pdf",
        "offer_ids": ["guid1", "guid2"],
        "template_used": "default_template.docx",
        "status": "draft"  // Optional, defaults to "draft"
    }

    Response:
    {
        "success": true,
        "proposal_id": "guid",
        "proposal_number": "PROP-20250117-ABC123"
    }
    """
    logger.info("Save proposal endpoint called")

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
        required_fields = [
            "proposal_number",
            "client_info",
            "word_url",
            "offer_ids",
            "template_used"
        ]
        if not validate_required_fields(req_body, required_fields):
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required fields",
                    "required": required_fields
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Validate client_info
        client_info = req_body["client_info"]
        client_required = ["name", "contact", "email"]
        if not validate_required_fields(client_info, client_required):
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required client_info fields",
                    "required": client_required
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Extract data
        proposal_number = req_body["proposal_number"]
        word_url = req_body["word_url"]
        pdf_url = req_body.get("pdf_url")  # Optional - might not exist if PDF conversion not implemented
        word_blob_name = req_body.get("word_blob_name", "")
        pdf_blob_name = req_body.get("pdf_blob_name", "")
        offer_ids = req_body["offer_ids"]
        template_used = req_body["template_used"]
        status = req_body.get("status", "draft")

        # Prepare Dataverse record
        proposal_data = {
            "cr_proposal_number": proposal_number,
            "cr_client_name": client_info["name"],
            "cr_client_contact": client_info["contact"],
            "cr_client_email": client_info["email"],
            "cr_word_url": word_url,
            "cr_pdf_url": pdf_url if pdf_url else "",
            "cr_word_blob_name": word_blob_name,
            "cr_pdf_blob_name": pdf_blob_name,
            "cr_status": status,
            "cr_generated_date": datetime.utcnow().isoformat(),
            "cr_offer_ids": json.dumps(offer_ids),  # Store as JSON string
            "cr_template_used": template_used,
            "cr_offer_count": len(offer_ids)
        }

        # Initialize Dataverse client
        dataverse_client = get_dataverse_client()

        # Create record in Dataverse
        logger.info(f"Creating proposal record in Dataverse: {proposal_number}")
        created_record = dataverse_client.create_record(
            entity_set="cr_propositions",
            data=proposal_data
        )

        # Extract created record ID
        proposal_id = created_record.get("cr_propositionid")

        if not proposal_id:
            logger.error("Dataverse did not return proposal ID")
            return func.HttpResponse(
                json.dumps({
                    "error": "Failed to retrieve created proposal ID from Dataverse"
                }),
                status_code=500,
                mimetype="application/json"
            )

        # Return success response
        response_data = {
            "success": True,
            "proposal_id": proposal_id,
            "proposal_number": proposal_number,
            "status": status
        }

        logger.info(f"Proposal saved successfully: {proposal_id}")
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=201,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error saving proposal: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to save proposal to Dataverse",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
