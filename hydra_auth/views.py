from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OAuth2ClientForm
from .hydra_client import HydraClient
from .models import OAuth2Client

hydra_client = HydraClient()

# Login, Consent, and Logout views (existing code)

def login_view(request):
    """
    Handle the login request from Ory Hydra.
    """
    # Get the login challenge from the URL
    login_challenge = request.GET.get('login_challenge')
    if not login_challenge:
        return HttpResponse('Login challenge is missing', status=400)
    
    # Fetch the login request from Hydra
    login_request = hydra_client.get_login_request(login_challenge)
    if not login_request:
        return HttpResponse('Invalid login challenge', status=400)
    
    # If user is already authenticated, accept the login request
    if login_request.skip:
        accept_response = hydra_client.accept_login_request(
            login_challenge=login_challenge,
            subject=login_request.subject,
            remember=True
        )
        return redirect(accept_response.redirect_to)
    
    # Handle form submission
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                remember = request.POST.get('remember', False) == 'on'
                
                # Accept the login request
                accept_response = hydra_client.accept_login_request(
                    login_challenge=login_challenge,
                    subject=username,
                    remember=remember
                )
                return redirect(accept_response.redirect_to)
            else:
                form.add_error(None, "Invalid username or password")
        # If form is invalid, it will be rendered with errors
    else:
        form = AuthenticationForm()
    
    return render(request, 'hydra_auth/login.html', {
        'form': form,
        'login_challenge': login_challenge
    })

def login_reject(request):
    """
    Reject the login request.
    """
    login_challenge = request.GET.get('login_challenge')
    if not login_challenge:
        return HttpResponse('Login challenge is missing', status=400)
    
    reject_response = hydra_client.reject_login_request(
        login_challenge=login_challenge,
        error="access_denied",
        error_description="The user rejected the authentication request"
    )
    
    return redirect(reject_response.redirect_to)

def consent_view(request):
    """
    Handle the consent request from Ory Hydra.
    """
    # Get the consent challenge from the URL
    consent_challenge = request.GET.get('consent_challenge')
    if not consent_challenge:
        return HttpResponse('Consent challenge is missing', status=400)
    
    # Fetch the consent request from Hydra
    consent_request = hydra_client.get_consent_request(consent_challenge)
    if not consent_request:
        return HttpResponse('Invalid consent challenge', status=400)
    
    # If the user has previously given consent and no new scopes are requested, 
    # we can skip showing the consent screen
    if consent_request.skip:
        accept_response = hydra_client.accept_consent_request(
            consent_challenge=consent_challenge,
            grant_scope=consent_request.requested_scope,
            grant_access_token_audience=consent_request.requested_access_token_audience,
            remember=True
        )
        return redirect(accept_response.redirect_to)
    
    # Handle form submission
    if request.method == 'POST':
        # Get the selected scopes from the form
        granted_scopes = request.POST.getlist('scopes')
        remember = request.POST.get('remember', False) == 'on'
        
        # Accept the consent request
        accept_response = hydra_client.accept_consent_request(
            consent_challenge=consent_challenge,
            grant_scope=granted_scopes,
            grant_access_token_audience=consent_request.requested_access_token_audience,
            remember=remember
        )
        return redirect(accept_response.redirect_to)
    
    return render(request, 'hydra_auth/consent.html', {
        'consent_challenge': consent_challenge,
        'client': consent_request.client,
        'requested_scope': consent_request.requested_scope,
        'user': consent_request.subject,
    })

def consent_reject(request):
    """
    Reject the consent request.
    """
    consent_challenge = request.GET.get('consent_challenge')
    if not consent_challenge:
        return HttpResponse('Consent challenge is missing', status=400)
    
    reject_response = hydra_client.reject_consent_request(
        consent_challenge=consent_challenge,
        error="access_denied",
        error_description="The user rejected the consent request"
    )
    
    return redirect(reject_response.redirect_to)

def logout_view(request):
    """
    Handle the logout request from Ory Hydra.
    """
    # Get the logout challenge from the URL
    logout_challenge = request.GET.get('logout_challenge')
    if not logout_challenge:
        return HttpResponse('Logout challenge is missing', status=400)
    
    # Fetch the logout request from Hydra
    logout_request = hydra_client.get_logout_request(logout_challenge)
    if not logout_request:
        return HttpResponse('Invalid logout challenge', status=400)
    
    # Handle form submission
    if request.method == 'POST':
        # Get the user's decision from the form
        if 'confirm' in request.POST:
            # Log the user out of the Django session
            logout(request)
            
            # Accept the logout request
            accept_response = hydra_client.accept_logout_request(logout_challenge)
            return redirect(accept_response.redirect_to)
        else:
            # Reject the logout request
            reject_response = hydra_client.reject_logout_request(
                logout_challenge=logout_challenge,
                error="access_denied",
                error_description="The user rejected the logout request"
            )
            return redirect(reject_response.redirect_to)
    
    return render(request, 'hydra_auth/logout.html', {
        'logout_challenge': logout_challenge,
        'subject': logout_request.subject,
        'session_id': logout_request.sid,
    })

def logout_reject(request):
    """
    Reject the logout request.
    """
    logout_challenge = request.GET.get('logout_challenge')
    if not logout_challenge:
        return HttpResponse('Logout challenge is missing', status=400)
    
    reject_response = hydra_client.reject_logout_request(
        logout_challenge=logout_challenge,
        error="access_denied",
        error_description="The user rejected the logout request"
    )
    
    return redirect(reject_response.redirect_to)

# OAuth2 Client Management views

@login_required
def client_list(request):
    """
    List all OAuth2 clients.
    """
    # Fetch clients from Hydra
    hydra_clients = hydra_client.list_oauth2_clients()
    
    # Convert Hydra clients to Django model instances
    clients = []
    for hc in hydra_clients:
        # Create or update local model
        client_model, created = OAuth2Client.objects.update_or_create(
            client_id=hc.client_id,
            defaults={
                'client_name': hc.client_name or '',
                'client_secret': hc.client_secret,
            }
        )
        
        # Update other fields
        if hc.redirect_uris:
            client_model.set_redirect_uris_list(hc.redirect_uris)
        if hc.grant_types:
            client_model.set_grant_types_list(hc.grant_types)
        if hc.response_types:
            client_model.set_response_types_list(hc.response_types)
        client_model.scope = hc.scope or ''
        client_model.token_endpoint_auth_method = hc.token_endpoint_auth_method or 'client_secret_basic'
        if hc.audience:
            client_model.set_audience_list(hc.audience)
        client_model.client_uri = hc.client_uri
        client_model.logo_uri = hc.logo_uri
        if hc.contacts:
            client_model.set_contacts_list(hc.contacts)
        client_model.tos_uri = hc.tos_uri
        client_model.policy_uri = hc.policy_uri
        client_model.jwks_uri = hc.jwks_uri
        client_model.allow_cors_requests = hc.allow_cors_requests or False
        
        # Save the updated model
        client_model.save()
        clients.append(client_model)
    
    return render(request, 'hydra_auth/client_list.html', {
        'clients': clients
    })

@login_required
def client_create(request):
    """
    Create a new OAuth2 client.
    """
    if request.method == 'POST':
        form = OAuth2ClientForm(request.POST)
        if form.is_valid():
            # Create a new client model instance but don't save it yet
            client = form.save(commit=False)
            
            # Convert form data to Hydra client format
            client_data = client.to_hydra_dict()
            
            # Create client in Hydra
            hydra_response = hydra_client.create_oauth2_client(client_data)
            
            if hydra_response:
                # Update the model with data from Hydra response
                client.client_id = hydra_response.client_id
                client.client_secret = hydra_response.client_secret
                client.save()
                
                messages.success(request, f"Client '{client.client_name}' created successfully.")
                return redirect('client_list')
            else:
                messages.error(request, "Failed to create client in Hydra.")
    else:
        form = OAuth2ClientForm()
    
    return render(request, 'hydra_auth/client_form.html', {
        'form': form,
        'title': 'Create OAuth2 Client',
        'submit_text': 'Create Client'
    })

@login_required
def client_update(request, client_id):
    """
    Update an existing OAuth2 client.
    """
    # Get the client from Hydra
    hydra_client_obj = hydra_client.get_oauth2_client(client_id)
    if not hydra_client_obj:
        messages.error(request, f"Client with ID '{client_id}' not found.")
        return redirect('client_list')
    
    # Get or create the local model instance
    client, created = OAuth2Client.objects.get_or_create(
        client_id=client_id,
        defaults={'client_name': hydra_client_obj.client_name or ''}
    )
    
    # Update the local model with data from Hydra
    if created or request.method != 'POST':
        client = OAuth2Client.from_hydra_client(hydra_client_obj)
        client.save()
    
    if request.method == 'POST':
        form = OAuth2ClientForm(request.POST, instance=client)
        if form.is_valid():
            # Update the model but don't save it yet
            updated_client = form.save(commit=False)
            
            # Convert form data to Hydra client format
            client_data = updated_client.to_hydra_dict()
            
            # Update client in Hydra
            hydra_response = hydra_client.update_oauth2_client(client_id, client_data)
            
            if hydra_response:
                # Save the updated model
                updated_client.save()
                
                messages.success(request, f"Client '{updated_client.client_name}' updated successfully.")
                return redirect('client_list')
            else:
                messages.error(request, "Failed to update client in Hydra.")
    else:
        form = OAuth2ClientForm(instance=client)
    
    return render(request, 'hydra_auth/client_form.html', {
        'form': form,
        'title': 'Update OAuth2 Client',
        'submit_text': 'Update Client',
        'client': client
    })

@login_required
def client_delete(request, client_id):
    """
    Delete an OAuth2 client.
    """
    # Get the client from the database
    client = get_object_or_404(OAuth2Client, client_id=client_id)
    
    if request.method == 'POST':
        # Delete the client from Hydra
        if hydra_client.delete_oauth2_client(client_id):
            # Delete the client from the database
            client.delete()
            messages.success(request, f"Client '{client.client_name}' deleted successfully.")
        else:
            messages.error(request, f"Failed to delete client '{client.client_name}' from Hydra.")
        
        return redirect('client_list')
    
    return render(request, 'hydra_auth/client_confirm_delete.html', {
        'client': client
    })
