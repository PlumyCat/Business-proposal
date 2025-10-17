"""
DocumentProcessor Azure Function
Handles document extraction and cleaning
"""

import json
import logging
import azure.functions as func
from .extract_content import extract_content
from .clean_document import clean_document
from .clean_quote import clean_quote

# Setup logging
logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main entry point for DocumentProcessor function

    Endpoints:
    - POST /api/document/extract-content - Extract content from document
    - POST /api/document/clean-document - Clean extracted document (legacy)
    - POST /api/document/clean-quote - Clean old quote (empty tables only)
    """
    logger.info('DocumentProcessor function triggered')

    # Route to appropriate handler based on route
    route = req.route_params.get('action')

    try:
        if route == 'extract-content':
            return extract_content(req)
        elif route == 'clean-document':
            return clean_document(req)
        elif route == 'clean-quote':
            return clean_quote(req)
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": "Invalid route. Use /extract-content, /clean-document, or /clean-quote"
                }),
                status_code=404,
                mimetype="application/json"
            )

    except Exception as e:
        logger.error(f"Error in DocumentProcessor: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
