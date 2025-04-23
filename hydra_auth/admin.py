from django.contrib import admin
from .models import OAuth2Client
from .hydra_client import HydraClient
from django.contrib import messages
from .forms import OAuth2ClientAdminForm

class OAuth2ClientAdmin(admin.ModelAdmin):
    form = OAuth2ClientAdminForm
    list_display = ('client_id', 'client_name', 'token_endpoint_auth_method', 'created_at', 'updated_at')
    search_fields = ('client_id', 'client_name')
    list_filter = ('token_endpoint_auth_method', 'allow_cors_requests')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('client_id', 'client_name', 'client_secret')
        }),
        ('Authentication', {
            'fields': ('token_endpoint_auth_method',)
        }),
        ('URIs', {
            'fields': ('redirect_uris_text',)
        }),
        ('Permissions', {
            'fields': ('grant_types_list', 'response_types_list', 'scope')
        }),
        ('Additional Settings', {
            'fields': ('audience_text', 'contacts_text', 'allow_cors_requests')
        }),
        ('Client URIs', {
            'fields': ('client_uri', 'logo_uri', 'tos_uri', 'policy_uri', 'jwks_uri'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to synchronize with Hydra when saving from admin.
        """
        hydra_client = HydraClient()
        client_data = obj.to_hydra_dict()
        
        if change:  # Update existing client
            hydra_response = hydra_client.update_oauth2_client(obj.client_id, client_data)
            if hydra_response:
                super().save_model(request, obj, form, change)
                messages.success(request, f"Client '{obj.client_name}' updated successfully in Hydra.")
            else:
                messages.error(request, f"Failed to update client '{obj.client_name}' in Hydra.")
        else:  # Create new client
            hydra_response = hydra_client.create_oauth2_client(client_data)
            if hydra_response:
                # Update with generated ID and secret if needed
                obj.client_id = hydra_response.client_id
                obj.client_secret = hydra_response.client_secret
                super().save_model(request, obj, form, change)
                messages.success(request, f"Client '{obj.client_name}' created successfully in Hydra.")
            else:
                messages.error(request, f"Failed to create client '{obj.client_name}' in Hydra.")
    
    def delete_model(self, request, obj):
        """
        Override delete_model to synchronize with Hydra when deleting from admin.
        """
        hydra_client = HydraClient()
        if hydra_client.delete_oauth2_client(obj.client_id):
            super().delete_model(request, obj)
            messages.success(request, f"Client '{obj.client_name}' deleted successfully from Hydra.")
        else:
            messages.error(request, f"Failed to delete client '{obj.client_name}' from Hydra.")
    
    def delete_queryset(self, request, queryset):
        """
        Override delete_queryset to synchronize with Hydra when bulk deleting from admin.
        """
        hydra_client = HydraClient()
        for obj in queryset:
            if hydra_client.delete_oauth2_client(obj.client_id):
                messages.success(request, f"Client '{obj.client_name}' deleted successfully from Hydra.")
            else:
                messages.error(request, f"Failed to delete client '{obj.client_name}' from Hydra.")
        
        super().delete_queryset(request, queryset)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make client_id readonly when editing an existing client.
        """
        if obj:  # Editing an existing object
            return self.readonly_fields + ('client_id',)
        return self.readonly_fields
    
    def sync_with_hydra(self, request, queryset):
        """
        Custom admin action to synchronize selected clients with Hydra.
        """
        hydra_client = HydraClient()
        success_count = 0
        error_count = 0
        
        for obj in queryset:
            client_data = obj.to_hydra_dict()
            hydra_response = hydra_client.update_oauth2_client(obj.client_id, client_data)
            
            if hydra_response:
                success_count += 1
            else:
                error_count += 1
        
        if success_count > 0:
            messages.success(request, f"Successfully synchronized {success_count} client(s) with Hydra.")
        
        if error_count > 0:
            messages.error(request, f"Failed to synchronize {error_count} client(s) with Hydra.")
    
    sync_with_hydra.short_description = "Synchronize selected clients with Hydra"
    
    actions = ['sync_with_hydra']

# Register the model with the admin site
admin.site.register(OAuth2Client, OAuth2ClientAdmin)
