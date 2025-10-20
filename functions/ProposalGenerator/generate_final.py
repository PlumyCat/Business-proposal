"""
Generate Final Proposal - Génère le document final Word + PDF
"""

import json
import logging
import io
import os
from datetime import datetime
from typing import Dict
import azure.functions as func
from docx import Document

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.blob_client import get_blob_client
from shared.sharepoint_client import get_sharepoint_client
from shared.validators import validate_required_fields
from shared.logger import setup_logger
from shared.config import CONTAINER_TEMPLATES, CONTAINER_DOCUMENTS, get_user_file_path

logger = setup_logger(__name__)


def generate_final_proposal(req: func.HttpRequest) -> func.HttpResponse:
    """
    Génère le document final (Word + PDF) à partir du temp_working.docx

    Le document temp_working.docx contient déjà:
    - Les infos customer success (ajoutées via /api/proposal/set-customer-info)
    - Les lignes d'offres (ajoutées via /api/proposal/add-offer-line)

    Cet endpoint:
    1. Charge temp_working.docx
    2. Génère un nom de fichier avec timestamp
    3. Sauvegarde Word dans word-documents
    4. Convertit en PDF via SharePoint
    5. Retourne URLs SAS avec expiration 24h

    Request body:
    {
        "user_folder": "Eric FER",
        "proposal_name": "Proposition Client XYZ" (optional)
    }

    Response:
    {
        "success": true,
        "word_file": "Eric FER/proposition_20251017_1430.docx",
        "word_url": "https://...?sas_token",
        "pdf_file": "Eric FER/proposition_20251017_1430.pdf",
        "pdf_url": "https://...?sas_token"
    }
    """
    logger.info("Generate final proposal endpoint called")

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
        if not validate_required_fields(req_body, ["user_folder"]):
            return func.HttpResponse(
                json.dumps({
                    "error": "Missing required field: user_folder"
                }),
                status_code=400,
                mimetype="application/json"
            )

        user_folder = req_body["user_folder"]
        proposal_name = req_body.get("proposal_name", "proposition")

        logger.info(f"Generating final proposal for {user_folder}")

        # Initialize clients
        blob_client = get_blob_client()

        # 1. Load working file from word-templates
        working_file_path = get_user_file_path(user_folder, "temp_working.docx")

        try:
            working_bytes = blob_client.download_blob(CONTAINER_TEMPLATES, working_file_path)
            logger.info(f"Downloaded working file: {working_file_path}")
        except Exception as e:
            logger.error(f"Failed to download working file: {str(e)}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Working file not found",
                    "working_file": working_file_path,
                    "hint": "Call /api/proposal/prepare-template first and add offers"
                }),
                status_code=404,
                mimetype="application/json"
            )

        # 2. Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        # Sanitize proposal_name for filename
        safe_name = "".join(c for c in proposal_name if c.isalnum() or c in (' ', '-', '_')).strip()
        if safe_name and safe_name.lower() != "proposition":
            proposal_filename = f"{safe_name}_{timestamp}"
        else:
            proposal_filename = f"proposition_{timestamp}"

        # 3. Save Word file to word-documents container
        word_file_path = get_user_file_path(user_folder, f"{proposal_filename}.docx")
        word_blob_url = blob_client.upload_blob(
            container_name=CONTAINER_DOCUMENTS,
            blob_name=word_file_path,
            data=working_bytes,
            overwrite=True
        )

        # Generate SAS URL with 24h expiration for Word
        word_sas_url = blob_client.generate_sas_url(
            container_name=CONTAINER_DOCUMENTS,
            blob_name=word_file_path,
            expiry_hours=24,
            permissions="r"
        )

        logger.info(f"Word file saved to: {CONTAINER_DOCUMENTS}/{word_file_path}")

        # 4. Convert to PDF via SharePoint
        pdf_sas_url = None
        pdf_file_path = None

        try:
            sharepoint_client = get_sharepoint_client()
            pdf_bytes = sharepoint_client.convert_word_to_pdf(
                word_content=working_bytes,
                file_name=f"temp_{proposal_filename}.docx"
            )

            if pdf_bytes:
                # Upload PDF to word-documents container
                pdf_file_path = get_user_file_path(user_folder, f"{proposal_filename}.pdf")
                pdf_blob_url = blob_client.upload_blob(
                    container_name=CONTAINER_DOCUMENTS,
                    blob_name=pdf_file_path,
                    data=pdf_bytes,
                    overwrite=True
                )

                # Generate SAS URL with 24h expiration for PDF
                pdf_sas_url = blob_client.generate_sas_url(
                    container_name=CONTAINER_DOCUMENTS,
                    blob_name=pdf_file_path,
                    expiry_hours=24,
                    permissions="r"
                )

                logger.info(f"PDF file saved to: {CONTAINER_DOCUMENTS}/{pdf_file_path}")
            else:
                logger.warning("PDF conversion returned empty bytes")

        except Exception as e:
            logger.error(f"PDF conversion failed: {str(e)}")
            # Continue without PDF, not blocking

        # 5. Return result with SAS URLs
        response_data = {
            "success": True,
            "word_file": word_file_path,
            "word_url": word_sas_url,
            "pdf_file": pdf_file_path if pdf_sas_url else None,
            "pdf_url": pdf_sas_url if pdf_sas_url else None,
            "sas_expiry_hours": 24
        }

        logger.info(f"Final proposal generated successfully for {user_folder}")
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error generating final proposal: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to generate final proposal",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
