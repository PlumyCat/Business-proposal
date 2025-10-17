"""
Clean Document Handler
Nettoie un document extrait en supprimant les données renseignées et en normalisant le contenu
"""

import json
import logging
import re
from typing import Dict, List, Any
import azure.functions as func

import sys
sys.path.append('..')
from shared.validators import validate_required_fields, ValidationError
from shared.logger import setup_logger

logger = setup_logger(__name__)


def remove_filled_data_from_text(text: str) -> str:
    """
    Remove filled data patterns from text

    Patterns to remove:
    - Dates (format DD/MM/YYYY, DD-MM-YYYY)
    - Emails
    - Phone numbers
    - Specific client names/addresses (heuristic)

    Args:
        text: Original text

    Returns:
        Cleaned text
    """
    # Remove dates
    text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '[DATE]', text)

    # Remove emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

    # Remove phone numbers (French format and international)
    text = re.sub(r'\b0[1-9](?:\s?\d{2}){4}\b', '[PHONE]', text)
    text = re.sub(r'\+\d{1,3}(?:\s?\d{1,4}){1,4}\b', '[PHONE]', text)

    # Remove potential prices/amounts
    text = re.sub(r'\b\d+[,\s]?\d*\s?€\b', '[AMOUNT]', text)
    text = re.sub(r'\b\d+[,\s]?\d*\s?EUR\b', '[AMOUNT]', text)

    return text


def normalize_table(table_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize table by removing filled data from cells

    Args:
        table_data: Table dictionary with headers and rows

    Returns:
        Normalized table
    """
    normalized_table = {
        "table_index": table_data.get("table_index"),
        "headers": table_data.get("headers", []),
        "rows": []
    }

    # Clean each row
    for row in table_data.get("rows", []):
        cleaned_row = []
        for cell in row:
            # Remove filled data from cell
            cleaned_cell = remove_filled_data_from_text(cell)
            # If cell becomes empty or placeholder, keep as empty template
            if cleaned_cell.strip() in ['[DATE]', '[EMAIL]', '[PHONE]', '[AMOUNT]', '']:
                cleaned_cell = ''
            cleaned_row.append(cleaned_cell)

        # Only keep rows that have some non-empty cells
        if any(cell.strip() for cell in cleaned_row):
            normalized_table["rows"].append(cleaned_row)

    return normalized_table


def apply_cleaning_rules(extracted_content: Dict[str, Any], rules: List[str]) -> Dict[str, Any]:
    """
    Apply cleaning rules to extracted content

    Args:
        extracted_content: Content from extract_content endpoint
        rules: List of cleaning rules to apply

    Returns:
        Cleaned content
    """
    cleaned_content = {
        "file_id": extracted_content.get("file_id"),
        "text": extracted_content.get("text", ""),
        "paragraphs": extracted_content.get("paragraphs", []),
        "tables": extracted_content.get("tables", []),
        "structure": extracted_content.get("structure", {}),
        "removed_items": []
    }

    if "remove_filled_data" in rules:
        logger.info("Applying rule: remove_filled_data")

        # Clean full text
        cleaned_content["text"] = remove_filled_data_from_text(cleaned_content["text"])

        # Clean paragraphs
        for para in cleaned_content["paragraphs"]:
            original_text = para["text"]
            para["text"] = remove_filled_data_from_text(para["text"])
            if original_text != para["text"]:
                cleaned_content["removed_items"].append(f"Paragraph {para['index']}: removed filled data")

    if "normalize_tables" in rules:
        logger.info("Applying rule: normalize_tables")

        # Normalize all tables
        normalized_tables = []
        for table in cleaned_content["tables"]:
            normalized_table = normalize_table(table)
            normalized_tables.append(normalized_table)

            original_rows = len(table.get("rows", []))
            cleaned_rows = len(normalized_table.get("rows", []))
            if original_rows != cleaned_rows:
                cleaned_content["removed_items"].append(
                    f"Table {table['table_index']}: removed {original_rows - cleaned_rows} filled rows"
                )

        cleaned_content["tables"] = normalized_tables

    if "remove_empty_paragraphs" in rules:
        logger.info("Applying rule: remove_empty_paragraphs")

        # Remove paragraphs that are now empty or only placeholders
        original_count = len(cleaned_content["paragraphs"])
        cleaned_content["paragraphs"] = [
            para for para in cleaned_content["paragraphs"]
            if para["text"].strip() and para["text"].strip() not in ['[DATE]', '[EMAIL]', '[PHONE]', '[AMOUNT]']
        ]
        removed_count = original_count - len(cleaned_content["paragraphs"])
        if removed_count > 0:
            cleaned_content["removed_items"].append(f"Removed {removed_count} empty paragraphs")

    logger.info(f"Cleaning complete. {len(cleaned_content['removed_items'])} changes made")
    return cleaned_content


def clean_document(req: func.HttpRequest) -> func.HttpResponse:
    """
    Clean extracted document content

    Request body:
    {
        "extracted_content": {...},  // Output from extract_content
        "cleaning_rules": ["remove_filled_data", "normalize_tables", "remove_empty_paragraphs"]
    }

    Response:
    {
        "file_id": "unique-file-id",
        "cleaned_content": {...},
        "removed_items": [...]
    }
    """
    logger.info("Clean document endpoint called")

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
        try:
            validate_required_fields(req_body, ["extracted_content"])
        except ValidationError as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=400,
                mimetype="application/json"
            )

        extracted_content = req_body["extracted_content"]
        cleaning_rules = req_body.get("cleaning_rules", ["remove_filled_data", "normalize_tables"])

        logger.info(f"Cleaning document with rules: {cleaning_rules}")

        # Apply cleaning rules
        cleaned_content = apply_cleaning_rules(extracted_content, cleaning_rules)

        # Build response
        response_data = {
            "file_id": cleaned_content.get("file_id"),
            "cleaned_content": cleaned_content,
            "removed_items": cleaned_content.get("removed_items", []),
            "stats": {
                "paragraphs_remaining": len(cleaned_content.get("paragraphs", [])),
                "tables_remaining": len(cleaned_content.get("tables", [])),
                "changes_made": len(cleaned_content.get("removed_items", []))
            }
        }

        logger.info(f"Successfully cleaned document")
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Unexpected error in clean_document: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
