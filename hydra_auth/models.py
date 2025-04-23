from django.db import models

class OAuth2Client(models.Model):
    """
    Model to represent an OAuth2 client in the database.
    This model stores a local representation of clients managed through Hydra.
    """
    client_id = models.CharField(max_length=255, primary_key=True)
    client_name = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    redirect_uris = models.TextField(help_text="Comma-separated list of redirect URIs")
    grant_types = models.TextField(help_text="Comma-separated list of grant types", blank=True)
    response_types = models.TextField(help_text="Comma-separated list of response types", blank=True)
    scope = models.TextField(help_text="Space-separated list of scopes", blank=True)
    token_endpoint_auth_method = models.CharField(
        max_length=50,
        default="client_secret_basic",
        choices=[
            ("client_secret_basic", "Client Secret Basic"),
            ("client_secret_post", "Client Secret Post"),
            ("private_key_jwt", "Private Key JWT"),
            ("none", "None"),
        ]
    )
    audience = models.TextField(help_text="Comma-separated list of audiences", blank=True)
    client_uri = models.URLField(blank=True, null=True)
    logo_uri = models.URLField(blank=True, null=True)
    contacts = models.TextField(help_text="Comma-separated list of contact emails", blank=True)
    tos_uri = models.URLField(blank=True, null=True, help_text="Terms of service URI")
    policy_uri = models.URLField(blank=True, null=True, help_text="Policy URI")
    jwks_uri = models.URLField(blank=True, null=True, help_text="JSON Web Key Set URI")
    allow_cors_requests = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.client_name} ({self.client_id})"
    
    def get_redirect_uris_list(self):
        """Convert comma-separated redirect URIs to list"""
        if not self.redirect_uris:
            return []
        return [uri.strip() for uri in self.redirect_uris.split(',')]
    
    def set_redirect_uris_list(self, uris_list):
        """Convert list of redirect URIs to comma-separated string"""
        self.redirect_uris = ','.join(uris_list)
    
    def get_grant_types_list(self):
        """Convert comma-separated grant types to list"""
        if not self.grant_types:
            return []
        return [gt.strip() for gt in self.grant_types.split(',')]
    
    def set_grant_types_list(self, grant_types_list):
        """Convert list of grant types to comma-separated string"""
        self.grant_types = ','.join(grant_types_list)
    
    def get_response_types_list(self):
        """Convert comma-separated response types to list"""
        if not self.response_types:
            return []
        return [rt.strip() for rt in self.response_types.split(',')]
    
    def set_response_types_list(self, response_types_list):
        """Convert list of response types to comma-separated string"""
        self.response_types = ','.join(response_types_list)
    
    def get_audience_list(self):
        """Convert comma-separated audiences to list"""
        if not self.audience:
            return []
        return [aud.strip() for aud in self.audience.split(',')]
    
    def set_audience_list(self, audience_list):
        """Convert list of audiences to comma-separated string"""
        self.audience = ','.join(audience_list)
    
    def get_contacts_list(self):
        """Convert comma-separated contacts to list"""
        if not self.contacts:
            return []
        return [contact.strip() for contact in self.contacts.split(',')]
    
    def set_contacts_list(self, contacts_list):
        """Convert list of contacts to comma-separated string"""
        self.contacts = ','.join(contacts_list)
    
    def to_hydra_dict(self):
        """
        Convert model instance to dictionary for Hydra API.
        """
        return {
            'client_id': self.client_id,
            'client_name': self.client_name,
            'client_secret': self.client_secret,
            'redirect_uris': self.get_redirect_uris_list(),
            'grant_types': self.get_grant_types_list(),
            'response_types': self.get_response_types_list(),
            'scope': self.scope,
            'token_endpoint_auth_method': self.token_endpoint_auth_method,
            'audience': self.get_audience_list(),
            'client_uri': self.client_uri,
            'logo_uri': self.logo_uri,
            'contacts': self.get_contacts_list(),
            'tos_uri': self.tos_uri,
            'policy_uri': self.policy_uri,
            'jwks_uri': self.jwks_uri,
            'allow_cors_requests': self.allow_cors_requests,
        }
    
    @classmethod
    def from_hydra_client(cls, hydra_client):
        """
        Create a model instance from a Hydra client object.
        """
        client = cls(
            client_id=hydra_client.client_id,
            client_name=hydra_client.client_name or '',
            client_secret=hydra_client.client_secret,
        )
        
        # Set redirect URIs
        if hydra_client.redirect_uris:
            client.set_redirect_uris_list(hydra_client.redirect_uris)
        
        # Set grant types
        if hydra_client.grant_types:
            client.set_grant_types_list(hydra_client.grant_types)
        
        # Set response types
        if hydra_client.response_types:
            client.set_response_types_list(hydra_client.response_types)
        
        # Set scope
        client.scope = hydra_client.scope or ''
        
        # Set token endpoint auth method
        client.token_endpoint_auth_method = hydra_client.token_endpoint_auth_method or 'client_secret_basic'
        
        # Set audience
        if hydra_client.audience:
            client.set_audience_list(hydra_client.audience)
        
        # Set URIs
        client.client_uri = hydra_client.client_uri
        client.logo_uri = hydra_client.logo_uri
        client.tos_uri = hydra_client.tos_uri
        client.policy_uri = hydra_client.policy_uri
        client.jwks_uri = hydra_client.jwks_uri
        
        # Set contacts
        if hydra_client.contacts:
            client.set_contacts_list(hydra_client.contacts)
        
        # Set CORS
        client.allow_cors_requests = hydra_client.allow_cors_requests or False
        
        return client
