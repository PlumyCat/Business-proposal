"""
Azure Functions App - Python Programming Model V2
Entry point for all functions
"""

import azure.functions as func
import logging

# Import handlers
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions'))

from DocumentProcessor.clean_quote import clean_quote
from DocumentProcessor.delete_template import delete_template
from DocumentProcessor.cleanup_expired import cleanup_expired
from DocumentProcessor.get_sas_url import get_sas_url
from DocumentProcessor.list_templates import list_general_templates
from DocumentProcessor.list_user_templates import list_user_templates
from DocumentProcessor.list_user_documents import list_created_documents
from ProposalGenerator.prepare_template import prepare_template
from ProposalGenerator.add_offer_line import add_offer_line
from ProposalGenerator.delete_offer_line import delete_offer_line
from ProposalGenerator.set_customer_info import set_customer_info
from ProposalGenerator.generate_final import generate_final_proposal

# Create function app instance
app = func.FunctionApp()

# Configure logging
logging.basicConfig(level=logging.INFO)


# ============================================================================
# DOCUMENT PROCESSING ENDPOINTS
# ============================================================================

@app.route(route="document/clean-quote", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def clean_quote_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Clean old quote - Empty tables only
    """
    return clean_quote(req)


@app.route(route="document/delete", methods=["DELETE"], auth_level=func.AuthLevel.FUNCTION)
def delete_template_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Delete a template or document from blob storage
    """
    return delete_template(req)


@app.route(route="document/cleanup-expired", methods=["DELETE"], auth_level=func.AuthLevel.FUNCTION)
def cleanup_expired_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Cleanup expired documents (older than 24h by default)
    """
    return cleanup_expired(req)


@app.route(route="document/get-sas-url", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def get_sas_url_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate SAS URL for downloading a document (expires in 24h by default)
    """
    return get_sas_url(req)


@app.route(route="template/list-general", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def list_general_templates_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    List all available general templates (in general/ folder)
    """
    return list_general_templates(req)


@app.route(route="template/list-user", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def list_user_templates_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    List user's personal templates (working files in word-templates)
    """
    return list_user_templates(req)


@app.route(route="document/list-created", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def list_created_documents_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    List user's created documents (final files in word-documents)
    """
    return list_created_documents(req)


# ============================================================================
# PROPOSAL GENERATION ENDPOINTS
# ============================================================================

@app.route(route="proposal/prepare-template", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def prepare_template_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Prepare template - creates temp_working.docx from general template
    """
    return prepare_template(req)


@app.route(route="proposal/set-customer-info", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def set_customer_info_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Set customer success info (name, tel, email) in working document
    """
    return set_customer_info(req)


@app.route(route="proposal/add-offer-line", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def add_offer_line_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Add a single offer line to the working document
    Bot reads offers from Dataverse and calls this for each offer
    """
    return add_offer_line(req)


@app.route(route="proposal/delete-offer-line", methods=["DELETE"], auth_level=func.AuthLevel.FUNCTION)
def delete_offer_line_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Delete a single offer line from the working document
    If table becomes empty, deletes the entire table
    """
    return delete_offer_line(req)


@app.route(route="proposal/generate", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def generate_proposal_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate final proposal (Word + PDF) from temp_working.docx
    Returns SAS URLs with 24h expiration
    """
    return generate_final_proposal(req)
