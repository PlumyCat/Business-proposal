# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project aims to create a business proposal generation system that:
- Accepts existing quotes/proposals (devis) as input
- Automatically cleans and normalizes the content, including table extraction
- Allows users to add elements from a predefined list of offers
- Generates formatted business proposals from templates

## Project Status

This is an early-stage project. The core requirements are documented in `projet.md` (in French).

## Key Requirements

1. **Input Processing**: System must accept existing business quotes and clean them automatically
2. **Table Extraction**: Extract and normalize tables from input documents
3. **Offer Integration**: Allow users to add elements from an offer list (data source flexible - could be Dataverse, blob storage, or other)
4. **Template-Based Output**: Generate proposals based on predefined templates

## Architecture

**Validated Stack:**
- **Backend:** Azure Functions (Python or TypeScript)
- **Interface:** Copilot Studio + Teams App
- **Storage:** Azure Blob Storage
- **Database:** Dataverse
- **Input Format:** Word (.docx)
- **Output Formats:** Word (.docx) + PDF
- **Authentication:** Azure AD (Entra ID)

**Azure Functions:**
- `DocumentProcessor` - Upload, extract content, and clean documents
- `OfferManager` - Retrieve offers from Dataverse
- `ProposalGenerator` - Generate Word/PDF proposals

**Dataverse Tables:**
- `Offres` - Available offers catalog
- `Propositions` - Proposal history and metadata
- `Templates` - Template management

**Copilot Studio Topics:**
- New Proposal workflow
- Document processing
- Offer selection
- Final generation
- History consultation

## Development Notes

- Primary language for project documentation is French
- The system needs to handle both "filled" quotes (renseigné) and "clean" templates
