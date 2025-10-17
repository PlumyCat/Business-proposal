"""
ProposalGenerator Azure Function
Handles template preparation and proposal generation (Word + PDF)
"""

import json
import logging
import azure.functions as func
from .prepare_template import prepare_template
from .generate_proposal import generate_proposal
from .generate_simple import generate_proposal_simple
from .save_proposal import save_proposal

# Setup logging
logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main entry point for ProposalGenerator function

    Endpoints:
    - POST /api/proposal/prepare-template - Prepare template with customer success info
    - POST /api/proposal/generate - Generate proposal (Word + PDF) - Version simplifiée
    - POST /api/proposal/generate-full - Generate proposal (Word + PDF) - Version complète (legacy)
    - POST /api/proposal/save - Save proposal metadata to Dataverse (optional)
    """
    logger.info('ProposalGenerator function triggered')

    # Route to appropriate handler based on route
    route = req.route_params.get('action')

    try:
        if route == 'prepare-template':
            return prepare_template(req)
        elif route == 'generate':
            # Version simplifiée par défaut
            return generate_proposal_simple(req)
        elif route == 'generate-full':
            # Version complète (legacy)
            return generate_proposal(req)
        elif route == 'save':
            return save_proposal(req)
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": "Invalid route. Use /prepare-template, /generate, /generate-full, or /save"
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
