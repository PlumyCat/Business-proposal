"""
Dataverse Client
Gère les opérations CRUD avec Dataverse (Power Platform)
"""

import os
import logging
import requests
from typing import Optional, Dict, List, Any
from .auth_helper import get_auth_helper

logger = logging.getLogger(__name__)


class DataverseClient:
    """Client pour interagir avec Dataverse API"""

    def __init__(self, dataverse_url: Optional[str] = None):
        """
        Initialize Dataverse client

        Args:
            dataverse_url: Dataverse URL (e.g., "https://org.crm.dynamics.com")
                          Si None, utilise la variable d'environnement DATAVERSE_URL
        """
        self.dataverse_url = (dataverse_url or os.getenv("DATAVERSE_URL", "")).rstrip("/")

        if not self.dataverse_url:
            raise ValueError("Dataverse URL is required")

        self.api_url = f"{self.dataverse_url}/api/data/v9.2"
        self.auth_helper = get_auth_helper()

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authentication token

        Returns:
            Dictionary of headers
        """
        token = self.auth_helper.get_dataverse_token(self.dataverse_url)

        return {
            "Authorization": f"Bearer {token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "return=representation"
        }

    def create_record(self, entity_set: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record in Dataverse

        Args:
            entity_set: Entity set name (e.g., "cr_offres")
            data: Record data as dictionary

        Returns:
            Created record with ID
        """
        try:
            url = f"{self.api_url}/{entity_set}"
            headers = self._get_headers()

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Created record in {entity_set}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create record in {entity_set}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise

    def get_record(self, entity_set: str, record_id: str, select: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a record by ID

        Args:
            entity_set: Entity set name
            record_id: Record GUID
            select: List of columns to select

        Returns:
            Record data
        """
        try:
            url = f"{self.api_url}/{entity_set}({record_id})"

            if select:
                url += f"?$select={','.join(select)}"

            headers = self._get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            logger.info(f"Retrieved record {record_id} from {entity_set}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get record {record_id} from {entity_set}: {str(e)}")
            raise

    def query_records(
        self,
        entity_set: str,
        filter_query: Optional[str] = None,
        select: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        top: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query records with OData filters

        Args:
            entity_set: Entity set name
            filter_query: OData filter string (e.g., "cr_actif eq true")
            select: List of columns to select
            order_by: Column to order by
            top: Max number of records to return

        Returns:
            List of records
        """
        try:
            url = f"{self.api_url}/{entity_set}"
            params = []

            if filter_query:
                params.append(f"$filter={filter_query}")
            if select:
                params.append(f"$select={','.join(select)}")
            if order_by:
                params.append(f"$orderby={order_by}")
            if top:
                params.append(f"$top={top}")

            if params:
                url += "?" + "&".join(params)

            headers = self._get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            result = response.json()
            records = result.get("value", [])

            logger.info(f"Queried {len(records)} records from {entity_set}")
            return records

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query records from {entity_set}: {str(e)}")
            raise

    def update_record(self, entity_set: str, record_id: str, data: Dict[str, Any]) -> bool:
        """
        Update an existing record

        Args:
            entity_set: Entity set name
            record_id: Record GUID
            data: Updated data

        Returns:
            True if successful
        """
        try:
            url = f"{self.api_url}/{entity_set}({record_id})"
            headers = self._get_headers()

            response = requests.patch(url, json=data, headers=headers)
            response.raise_for_status()

            logger.info(f"Updated record {record_id} in {entity_set}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update record {record_id} in {entity_set}: {str(e)}")
            raise

    def delete_record(self, entity_set: str, record_id: str) -> bool:
        """
        Delete a record

        Args:
            entity_set: Entity set name
            record_id: Record GUID

        Returns:
            True if successful
        """
        try:
            url = f"{self.api_url}/{entity_set}({record_id})"
            headers = self._get_headers()

            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            logger.info(f"Deleted record {record_id} from {entity_set}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete record {record_id} from {entity_set}: {str(e)}")
            raise

    # Convenience methods for specific tables

    def get_offers(self, active_only: bool = True, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of offers from cr_offres table

        Args:
            active_only: Only return active offers
            category: Filter by category

        Returns:
            List of offers
        """
        filters = []

        if active_only:
            filters.append("cr_actif eq true")

        if category:
            filters.append(f"cr_categorie eq '{category}'")

        filter_query = " and ".join(filters) if filters else None

        return self.query_records(
            entity_set="cr_offres",
            filter_query=filter_query,
            order_by="cr_nom asc"
        )

    def get_uploaded_file(self, file_id: Optional[str] = None, filename: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get uploaded file info from cr_uploads_temp table

        Args:
            file_id: File ID
            filename: Original filename

        Returns:
            Upload record or None
        """
        if file_id:
            filter_query = f"cr_file_id eq '{file_id}'"
        elif filename:
            filter_query = f"cr_original_filename eq '{filename}'"
        else:
            # Get most recent upload
            records = self.query_records(
                entity_set="cr_uploads_temp",
                order_by="cr_upload_date desc",
                top=1
            )
            return records[0] if records else None

        records = self.query_records(
            entity_set="cr_uploads_temp",
            filter_query=filter_query
        )

        return records[0] if records else None

    def create_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new proposal in cr_propositions table

        Args:
            proposal_data: Proposal data

        Returns:
            Created proposal record
        """
        return self.create_record("cr_propositions", proposal_data)


# Singleton instance
_dataverse_client_instance: Optional[DataverseClient] = None


def get_dataverse_client() -> DataverseClient:
    """
    Get singleton instance of DataverseClient

    Returns:
        DataverseClient instance
    """
    global _dataverse_client_instance

    if _dataverse_client_instance is None:
        _dataverse_client_instance = DataverseClient()

    return _dataverse_client_instance
