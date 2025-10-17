"""
ProposalGenerator Azure Function
Handles proposal generation (Word + PDF) and saving to Dataverse
"""

import json
import logging
import azure.functions as func
from .generate_proposal import generate_proposal
from .save_proposal import save_proposal

# Setup logging
logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main entry point for ProposalGenerator function

    Endpoints:
    - POST /api/proposal/generate - Generate proposal (Word + PDF)
    - POST /api/proposal/save - Save proposal metadata to Dataverse
    """
    logger.info('ProposalGenerator function triggered')

    # Route to appropriate handler based on route
    route = req.route_params.get('action')

    try:
        if route == 'generate':
            return generate_proposal(req)
        elif route == 'save':
            return save_proposal(req)
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": "Invalid route. Use /generate or /save"
                }),
                status_code=404,
                mimetype="application/json"
            )

    except Exception as e:
        logger.error(f"Error in ProposalGenerator: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "message": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
