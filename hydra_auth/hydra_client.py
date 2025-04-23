"""
Ory Hydra client configuration and utility functions.
"""


import ory_client
from django.conf import settings


class HydraClient:
    """
    Client for interacting with Ory Hydra OAuth2 server.
    """
    
    def __init__(self):
        # Configure the Ory Hydra Admin API client
        self.admin_configuration = ory_client.Configuration(
            host=settings.HYDRA_ADMIN_URL
        )
        self.admin_api = ory_client.ApiClient(self.admin_configuration)
        self.oauth2_api = ory_client.OAuth2Api(self.admin_api)
        
        # Configure the Ory Hydra Public API client
        self.public_configuration = ory_client.Configuration(
            host=settings.HYDRA_PUBLIC_URL
        )
        self.public_api = ory_client.ApiClient(self.public_configuration)
        
    # Login, Consent, and Logout methods
    
    def get_login_request(self, login_challenge):
        """
        Get login request information from Hydra.
        """
        try:
            return self.oauth2_api.get_oauth2_login_request(login_challenge)
        except ory_client.ApiException as e:
            print(f"Exception when calling get_oauth2_login_request: {e}")
            return None
    
    def accept_login_request(self, login_challenge, subject, remember=False, remember_for=3600):
        """
        Accept a login request.
        """
        try:
            body = ory_client.AcceptOAuth2LoginRequest(
                subject=subject,
                remember=remember,
                remember_for=remember_for
            )
            return self.oauth2_api.accept_oauth2_login_request(
                login_challenge=login_challenge,
                accept_oauth2_login_request=body
            )
        except ory_client.ApiException as e:
            print(f"Exception when calling accept_oauth2_login_request: {e}")
            return None
    
    def reject_login_request(self, login_challenge, error="access_denied", error_description="The resource owner denied the request"):
        """
        Reject a login request.
        """
        try:
            body = ory_client.RejectOAuth2Request(
                error=error,
                error_description=error_description
            )
            return self.oauth2_api.reject_oauth2_login_request(
                login_challenge=login_challenge,
                reject_oauth2_request=body
            )
        except ory_client.ApiException as e:
            print(f"Exception when calling reject_oauth2_login_request: {e}")
            return None
    
    def get_consent_request(self, consent_challenge):
        """
        Get consent request information from Hydra.
        """
        try:
            return self.oauth2_api.get_oauth2_consent_request(consent_challenge)
        except ory_client.ApiException as e:
            print(f"Exception when calling get_oauth2_consent_request: {e}")
            return None
    
    def accept_consent_request(self, consent_challenge, grant_scope, grant_access_token_audience=None, remember=False, remember_for=3600):
        """
        Accept a consent request.
        """
        try:
            body = ory_client.AcceptOAuth2ConsentRequest(
                grant_scope=grant_scope,
                grant_access_token_audience=grant_access_token_audience,
                remember=remember,
                remember_for=remember_for
            )
            return self.oauth2_api.accept_oauth2_consent_request(
                consent_challenge=consent_challenge,
                accept_oauth2_consent_request=body
            )
        except ory_client.ApiException as e:
            print(f"Exception when calling accept_oauth2_consent_request: {e}")
            return None
    
    def reject_consent_request(self, consent_challenge, error="access_denied", error_description="The resource owner denied the request"):
        """
        Reject a consent request.
        """
        try:
            body = ory_client.RejectOAuth2Request(
                error=error,
                error_description=error_description
            )
            return self.oauth2_api.reject_oauth2_consent_request(
                consent_challenge=consent_challenge,
                reject_oauth2_request=body
            )
        except ory_client.ApiException as e:
            print(f"Exception when calling reject_oauth2_consent_request: {e}")
            return None
    
    def get_logout_request(self, logout_challenge):
        """
        Get logout request information from Hydra.
        """
        try:
            return self.oauth2_api.get_oauth2_logout_request(logout_challenge)
        except ory_client.ApiException as e:
            print(f"Exception when calling get_oauth2_logout_request: {e}")
            return None
    
    def accept_logout_request(self, logout_challenge):
        """
        Accept a logout request.
        """
        try:
            return self.oauth2_api.accept_oauth2_logout_request(logout_challenge)
        except ory_client.ApiException as e:
            print(f"Exception when calling accept_oauth2_logout_request: {e}")
            return None
    
    def reject_logout_request(self, logout_challenge, error="access_denied", error_description="The resource owner denied the request"):
        """
        Reject a logout request.
        """
        try:
            body = ory_client.RejectOAuth2Request(
                error=error,
                error_description=error_description
            )
            return self.oauth2_api.reject_oauth2_logout_request(
                logout_challenge=logout_challenge,
                reject_oauth2_request=body
            )
        except ory_client.ApiException as e:
            print(f"Exception when calling reject_oauth2_logout_request: {e}")
            return None
    
    # OAuth2 Client Management methods
    
    def list_oauth2_clients(self, limit=25, offset=0):
        """
        List all OAuth2 clients.
        """
        try:
            return self.oauth2_api.list_oauth2_clients(limit=limit, offset=offset)
        except ory_client.ApiException as e:
            print(f"Exception when calling list_oauth2_clients: {e}")
            return []
    
    def get_oauth2_client(self, client_id):
        """
        Get a specific OAuth2 client by ID.
        """
        try:
            return self.oauth2_api.get_oauth2_client(id=client_id)
        except ory_client.ApiException as e:
            print(f"Exception when calling get_oauth2_client: {e}")
            return None
    
    def create_oauth2_client(self, client_data):
        """
        Create a new OAuth2 client.
        
        Args:
            client_data (dict): Dictionary containing client data with the following keys:
                - client_id (optional): Client ID (if not provided, one will be generated)
                - client_name: Human-readable name
                - client_secret (optional): Client secret (if not provided, one will be generated)
                - redirect_uris: List of allowed redirect URIs
                - grant_types: List of allowed grant types
                - response_types: List of allowed response types
                - scope: Space-separated list of allowed scopes
                - token_endpoint_auth_method: Client authentication method
                - audience (optional): List of allowed audiences
                - client_uri (optional): Client URI
                - logo_uri (optional): Logo URI
                - contacts (optional): List of contact emails
                - tos_uri (optional): Terms of service URI
                - policy_uri (optional): Policy URI
                - jwks_uri (optional): JWKS URI
                - allow_cors_requests (optional): Whether to allow CORS requests
        
        Returns:
            OAuth2Client: The created OAuth2 client or None if an error occurred
        """
        try:
            # Create OAuth2Client object from client_data
            oauth2_client = ory_client.OAuth2Client(
                client_id=client_data.get('client_id'),
                client_name=client_data.get('client_name'),
                client_secret=client_data.get('client_secret'),
                redirect_uris=client_data.get('redirect_uris', []),
                grant_types=client_data.get('grant_types', []),
                response_types=client_data.get('response_types', []),
                scope=client_data.get('scope', ''),
                token_endpoint_auth_method=client_data.get('token_endpoint_auth_method', 'client_secret_basic'),
                audience=client_data.get('audience', []),
                client_uri=client_data.get('client_uri'),
                logo_uri=client_data.get('logo_uri'),
                contacts=client_data.get('contacts', []),
                tos_uri=client_data.get('tos_uri'),
                policy_uri=client_data.get('policy_uri'),
                jwks_uri=client_data.get('jwks_uri'),
                allow_cors_requests=client_data.get('allow_cors_requests', False)
            )
            
            return self.oauth2_api.create_oauth2_client(oauth2_client=oauth2_client)
        except ory_client.ApiException as e:
            print(f"Exception when calling create_oauth2_client: {e}")
            return None
    
    def update_oauth2_client(self, client_id, client_data):
        """
        Update an existing OAuth2 client.
        
        Args:
            client_id (str): ID of the client to update
            client_data (dict): Dictionary containing updated client data
                (see create_oauth2_client for details)
        
        Returns:
            OAuth2Client: The updated OAuth2 client or None if an error occurred
        """
        try:
            # Create OAuth2Client object from client_data
            oauth2_client = ory_client.OAuth2Client(
                client_id=client_id,
                client_name=client_data.get('client_name'),
                client_secret=client_data.get('client_secret'),
                redirect_uris=client_data.get('redirect_uris', []),
                grant_types=client_data.get('grant_types', []),
                response_types=client_data.get('response_types', []),
                scope=client_data.get('scope', ''),
                token_endpoint_auth_method=client_data.get('token_endpoint_auth_method', 'client_secret_basic'),
                audience=client_data.get('audience', []),
                client_uri=client_data.get('client_uri'),
                logo_uri=client_data.get('logo_uri'),
                contacts=client_data.get('contacts', []),
                tos_uri=client_data.get('tos_uri'),
                policy_uri=client_data.get('policy_uri'),
                jwks_uri=client_data.get('jwks_uri'),
                allow_cors_requests=client_data.get('allow_cors_requests', False)
            )
            
            return self.oauth2_api.update_oauth2_client(id=client_id, oauth2_client=oauth2_client)
        except ory_client.ApiException as e:
            print(f"Exception when calling update_oauth2_client: {e}")
            return None
    
    def delete_oauth2_client(self, client_id):
        """
        Delete an OAuth2 client.
        
        Args:
            client_id (str): ID of the client to delete
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.oauth2_api.delete_oauth2_client(id=client_id)
            return True
        except ory_client.ApiException as e:
            print(f"Exception when calling delete_oauth2_client: {e}")
            return False
