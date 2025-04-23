# Django Ory Hydra Authentication Implementation

This project implements a Django application that integrates with Ory Hydra for OAuth 2.0 and OpenID Connect authentication flows. It provides endpoints for login, consent, and logout that work with Ory Hydra's authentication and authorization processes, as well as Django admin integration for OAuth2 client management.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing the Authentication Flow](#testing-the-authentication-flow)
- [OAuth2 Client Management in Django Admin](#oauth2-client-management-in-django-admin)
- [API Endpoints](#api-endpoints)
- [Implementation Details](#implementation-details)
- [Troubleshooting](#troubleshooting)

## Overview

[Ory Hydra](https://www.ory.sh/hydra/) is an OAuth 2.0 and OpenID Connect provider that implements the OAuth 2.0 authorization framework and the OpenID Connect Core 1.0 specification. This Django application serves as a login, consent, and logout provider for Ory Hydra, handling the user authentication and consent flows.

The application implements the following features:
- **Authentication Flow**: Login, consent, and logout endpoints for OAuth2/OIDC flows
- **OAuth2 Client Management**: Complete CRUD interface for managing OAuth2 clients through Django's admin interface

## Project Structure

```
ory_django_auth/
├── Dockerfile                  # Docker configuration for the Django app
├── create_test_client.sh       # Script to create a test OAuth client
├── docker-compose.yml          # Docker Compose configuration
├── hydra-config/               # Ory Hydra configuration
│   └── hydra.yml               # Hydra configuration file
├── hydra_auth/                 # Django app for Hydra integration
│   ├── admin.py                # Django admin configuration for OAuth2 clients
│   ├── forms.py                # Forms for OAuth2 client management
│   ├── hydra_client.py         # Ory Hydra client implementation
│   ├── models.py               # Models for OAuth2 clients
│   ├── templates/              # HTML templates
│   │   └── hydra_auth/         
│   │       ├── consent.html    # Consent page template
│   │       ├── login.html      # Login page template
│   │       └── logout.html     # Logout page template
│   ├── urls.py                 # URL routing for the app
│   └── views.py                # View functions for login, consent, logout
├── manage.py                   # Django management script
├── ory_auth/                   # Django project settings
│   ├── settings.py             # Django settings
│   └── urls.py                 # Main URL routing
├── requirements.txt            # Python dependencies
├── test_admin_integration.sh   # Script to test admin integration
└── todo.md                     # Project task list
```

## Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.10 or higher (for local development)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ory_django_auth
   ```

2. Build and start the containers:
   ```
   docker-compose up -d
   ```

3. Create a test client:
   ```
   chmod +x create_test_client.sh
   ./create_test_client.sh
   ```

## Configuration

### Django Settings

The Django application is configured in `ory_auth/settings.py`. The Ory Hydra configuration is set through environment variables:

```python
# Ory Hydra Configuration
HYDRA_ADMIN_URL = os.environ.get('HYDRA_ADMIN_URL', 'http://localhost:4445')
HYDRA_PUBLIC_URL = os.environ.get('HYDRA_PUBLIC_URL', 'http://localhost:4444')
```

### Ory Hydra Configuration

Ory Hydra is configured in `hydra-config/hydra.yml`. The key settings are:

```yaml
urls:
  self:
    issuer: http://localhost:4444
  consent: http://localhost:8000/hydra/consent
  login: http://localhost:8000/hydra/login
  logout: http://localhost:8000/hydra/logout
```

These URLs tell Hydra where to redirect users for login, consent, and logout flows.

### Docker Compose

The `docker-compose.yml` file configures both the Django application and Ory Hydra:

```yaml
services:
  hydra:
    image: oryd/hydra:v2.1.1
    ports:
      - "4444:4444" # Public port
      - "4445:4445" # Admin port
    # ...

  django:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HYDRA_ADMIN_URL=http://hydra:4445
      - HYDRA_PUBLIC_URL=http://localhost:4444
    # ...
```

## Running the Application

1. Start the services:
   ```
   docker-compose up -d
   ```

2. Create a Django superuser (for accessing the admin interface):
   ```
   docker-compose exec django python manage.py createsuperuser
   ```

3. Access the application at http://localhost:8000
   Access the admin interface at http://localhost:8000/admin/

## Testing the Authentication Flow

1. Run the test script to create a test OAuth client:
   ```
   ./create_test_client.sh
   ```

2. Start the OAuth flow with the following command:
   ```
   docker-compose exec hydra \
     hydra perform authorization-code \
     --client-id test-client \
     --client-secret test-secret \
     --endpoint http://localhost:4444/ \
     --port 8000 \
     --scope openid,offline,email,profile
   ```

3. This will open a browser window and start the authentication flow:
   - You will be redirected to the login page
   - After successful login, you will see the consent page
   - After granting consent, you will receive an authorization code
   - The test command will exchange the code for tokens

## OAuth2 Client Management in Django Admin

The application integrates OAuth2 client management directly into Django's admin interface, allowing you to create, read, update, and delete clients using Django's familiar admin UI.

### Accessing the Admin Interface

1. Ensure the application is running
2. Navigate to http://localhost:8000/admin/
3. Log in with your Django admin credentials
4. Click on "OAuth2 clients" under the "HYDRA_AUTH" section

### Client Management Features

- **List View**: View all registered OAuth2 clients with key information
- **Create View**: Register new OAuth2 clients with customizable settings
- **Edit View**: Modify existing client configurations
- **Delete View**: Remove clients that are no longer needed
- **Bulk Actions**: Perform actions on multiple clients at once
- **Synchronization**: Manual synchronization with Hydra using the "Synchronize selected clients with Hydra" action

### Client Properties

The admin interface allows you to configure the following properties:

- **Basic Information**:
  - Client ID (auto-generated if not provided)
  - Client Name
  - Client Secret (auto-generated if not provided)

- **Authentication**:
  - Token Endpoint Auth Method (how the client authenticates)

- **URIs**:
  - Redirect URIs (one per line)

- **Permissions**:
  - Grant Types (authorization_code, implicit, client_credentials, refresh_token)
  - Response Types (code, token, id_token, id_token token)
  - Scope (space-separated list of scopes)

- **Additional Settings**:
  - Audience (one per line)
  - Contacts (one per line)
  - Allow CORS Requests

- **Client URIs**:
  - Client URI
  - Logo URI
  - Terms of Service URI
  - Policy URI
  - JWKS URI

### Hydra Synchronization

All changes made through the admin interface are automatically synchronized with Hydra:

- **Creating clients**: When you create a client in the admin, it's also created in Hydra
- **Updating clients**: When you update a client in the admin, it's also updated in Hydra
- **Deleting clients**: When you delete a client in the admin, it's also deleted from Hydra
- **Manual synchronization**: You can manually synchronize selected clients with Hydra using the admin action

### Testing Admin Integration

To test the admin integration:

```
chmod +x test_admin_integration.sh
./test_admin_integration.sh
```

This script will:
1. Create a test admin user if one doesn't exist
2. Make migrations for the OAuth2Client model
3. Start the Django development server
4. Provide instructions for accessing and testing the admin interface

## API Endpoints

### Authentication Flow Endpoints

- **Login Endpoint**
  - **URL**: `/hydra/login`
  - **Method**: GET/POST
  - **Query Parameters**: `login_challenge` - The login challenge from Hydra
  - **Description**: Handles user authentication and accepts or rejects login requests

- **Consent Endpoint**
  - **URL**: `/hydra/consent`
  - **Method**: GET/POST
  - **Query Parameters**: `consent_challenge` - The consent challenge from Hydra
  - **Description**: Displays requested scopes and allows users to grant or deny access

- **Logout Endpoint**
  - **URL**: `/hydra/logout`
  - **Method**: GET/POST
  - **Query Parameters**: `logout_challenge` - The logout challenge from Hydra
  - **Description**: Handles user logout requests

## Implementation Details

### Hydra Client

The `HydraClient` class in `hydra_auth/hydra_client.py` provides methods for interacting with the Ory Hydra API:

```python
class HydraClient:
    def __init__(self):
        # Configure the Ory Hydra Admin API client
        self.admin_configuration = ory_client.Configuration(
            host=settings.HYDRA_ADMIN_URL
        )
        # ...
    
    # Authentication flow methods
    def get_login_request(self, login_challenge):
        # Get login request information from Hydra
        # ...
    
    def accept_login_request(self, login_challenge, subject, remember=False, remember_for=3600):
        # Accept a login request
        # ...
    
    # OAuth2 client management methods
    def list_oauth2_clients(self, limit=25, offset=0):
        # List all OAuth2 clients
        # ...
    
    def create_oauth2_client(self, client_data):
        # Create a new OAuth2 client
        # ...
    
    def update_oauth2_client(self, client_id, client_data):
        # Update an existing OAuth2 client
        # ...
    
    def delete_oauth2_client(self, client_id):
        # Delete an OAuth2 client
        # ...
```

### Models

The `OAuth2Client` model in `hydra_auth/models.py` represents an OAuth2 client in the database:

```python
class OAuth2Client(models.Model):
    client_id = models.CharField(max_length=255, primary_key=True)
    client_name = models.CharField(max_length=255)
    # Other fields...
    
    def to_hydra_dict(self):
        # Convert model instance to dictionary for Hydra API
        # ...
    
    @classmethod
    def from_hydra_client(cls, hydra_client):
        # Create a model instance from a Hydra client object
        # ...
```

### Admin Integration

The `OAuth2ClientAdmin` class in `hydra_auth/admin.py` configures the Django admin interface for OAuth2 clients:

```python
class OAuth2ClientAdmin(admin.ModelAdmin):
    form = OAuth2ClientAdminForm
    list_display = ('client_id', 'client_name', 'token_endpoint_auth_method', 'created_at', 'updated_at')
    search_fields = ('client_id', 'client_name')
    list_filter = ('token_endpoint_auth_method', 'allow_cors_requests')
    
    def save_model(self, request, obj, form, change):
        # Synchronize with Hydra when saving from admin
        # ...
    
    def delete_model(self, request, obj):
        # Synchronize with Hydra when deleting from admin
        # ...
    
    def sync_with_hydra(self, request, queryset):
        # Custom admin action to synchronize selected clients with Hydra
        # ...
```

### Custom Admin Form

The `OAuth2ClientAdminForm` in `hydra_auth/forms.py` provides a user-friendly interface for managing OAuth2 clients:

```python
class OAuth2ClientAdminForm(forms.ModelForm):
    # Convert comma-separated fields to multi-select fields
    grant_types_list = forms.MultipleChoiceField(
        choices=GRANT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grant Types"
    )
    
    # Convert comma-separated fields to textarea with line breaks
    redirect_uris_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        label="Redirect URIs",
        help_text="Enter one URI per line"
    )
    
    # Other form fields...
```

### Views

The views in `hydra_auth/views.py` handle the authentication flows:

- `login_view`: Authenticates users and accepts or rejects login requests
- `consent_view`: Displays requested scopes and allows users to grant or deny access
- `logout_view`: Handles user logout requests

## Troubleshooting

### Common Issues

1. **Connection refused to Hydra**:
   - Ensure Hydra is running: `docker-compose ps`
   - Check Hydra logs: `docker-compose logs hydra`

2. **Invalid login/consent challenge**:
   - Verify the challenge parameter in the URL
   - Check Hydra logs for error messages

3. **Redirect URI mismatch**:
   - Ensure the client's redirect URI matches the one used in the request

4. **Admin synchronization issues**:
   - Check that Hydra's admin API is accessible
   - Look for error messages in the Django admin interface
   - Verify the HYDRA_ADMIN_URL environment variable is correct

### Debugging

To enable debug logging, set the `log.level` to `debug` in `hydra-config/hydra.yml` and restart the services:

```yaml
log:
  level: debug
  format: json
```

You can view the logs with:
```
docker-compose logs -f
```
