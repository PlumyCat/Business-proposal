"""
Azure Authentication Helper
Gère l'authentification avec Azure AD pour Dataverse et autres services
"""

import os
import logging
from typing import Optional
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)


class AuthHelper:
    """Helper pour gérer l'authentification Azure AD"""

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        """
        Initialize authentication helper

        Args:
            tenant_id: Azure AD Tenant ID
            client_id: Application (client) ID
            client_secret: Client secret
        """
        self.tenant_id = tenant_id or os.getenv("DATAVERSE_TENANT_ID")
        self.client_id = client_id or os.getenv("DATAVERSE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("DATAVERSE_CLIENT_SECRET")

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError("Azure AD credentials (tenant_id, client_id, client_secret) are required")

        self._credential = None
        self._msal_app = None

    def get_credential(self) -> ClientSecretCredential:
        """
        Get Azure credential for service-to-service authentication

        Returns:
            ClientSecretCredential instance
        """
        if self._credential is None:
            self._credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            logger.info("Created Azure AD credential")

        return self._credential

    def get_access_token(self, scope: str) -> str:
        """
        Get access token for a specific scope

        Args:
            scope: OAuth scope (e.g., "https://org.crm.dynamics.com/.default")

        Returns:
            Access token string
        """
        try:
            credential = self.get_credential()
            token = credential.get_token(scope)
            logger.info(f"Acquired access token for scope: {scope}")
            return token.token

        except Exception as e:
            logger.error(f"Failed to acquire access token: {str(e)}")
            raise

    def get_dataverse_token(self, dataverse_url: Optional[str] = None) -> str:
        """
        Get access token for Dataverse API

        Args:
            dataverse_url: Dataverse URL (e.g., "https://org.crm.dynamics.com")
                          Si None, utilise DATAVERSE_URL env variable

        Returns:
            Access token string
        """
        url = dataverse_url or os.getenv("DATAVERSE_URL")

        if not url:
            raise ValueError("Dataverse URL is required")

        # Ensure URL doesn't end with /
        url = url.rstrip("/")

        # Dataverse scope format
        scope = f"{url}/.default"

        return self.get_access_token(scope)

    def get_msal_app(self) -> ConfidentialClientApplication:
        """
        Get MSAL Confidential Client Application

        Returns:
            ConfidentialClientApplication instance
        """
        if self._msal_app is None:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"

            self._msal_app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=authority
            )
            logger.info("Created MSAL application")

        return self._msal_app

    def acquire_token_for_client(self, scopes: list[str]) -> Optional[str]:
        """
        Acquire token using client credentials flow (service-to-service)

        Args:
            scopes: List of scopes

        Returns:
            Access token or None if failed
        """
        try:
            app = self.get_msal_app()
            result = app.acquire_token_for_client(scopes=scopes)

            if "access_token" in result:
                logger.info("Successfully acquired token via MSAL")
                return result["access_token"]
            else:
                error = result.get("error")
                error_desc = result.get("error_description")
                logger.error(f"MSAL token acquisition failed: {error} - {error_desc}")
                return None

        except Exception as e:
            logger.error(f"Exception during MSAL token acquisition: {str(e)}")
            raise


# Singleton instance
_auth_helper_instance: Optional[AuthHelper] = None


def get_auth_helper() -> AuthHelper:
    """
    Get singleton instance of AuthHelper

    Returns:
        AuthHelper instance
    """
    global _auth_helper_instance

    if _auth_helper_instance is None:
        _auth_helper_instance = AuthHelper()

    return _auth_helper_instance
