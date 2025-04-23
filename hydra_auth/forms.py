from django import forms

from .models import OAuth2Client


class OAuth2ClientAdminForm(forms.ModelForm):
    """
    Custom form for OAuth2Client in the admin interface.
    """
    GRANT_TYPE_CHOICES = [
        ('authorization_code', 'Authorization Code'),
        ('implicit', 'Implicit'),
        ('client_credentials', 'Client Credentials'),
        ('refresh_token', 'Refresh Token'),
    ]
    
    RESPONSE_TYPE_CHOICES = [
        ('code', 'Code'),
        ('token', 'Token'),
        ('id_token', 'ID Token'),
        ('id_token token', 'ID Token + Token'),
    ]
    
    # Convert comma-separated fields to multi-select fields
    grant_types_list = forms.MultipleChoiceField(
        choices=GRANT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grant Types"
    )
    
    response_types_list = forms.MultipleChoiceField(
        choices=RESPONSE_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Response Types"
    )
    
    # Convert comma-separated fields to textarea with line breaks
    redirect_uris_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        label="Redirect URIs",
        help_text="Enter one URI per line"
    )
    
    audience_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="Audience",
        help_text="Enter one audience per line"
    )
    
    contacts_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="Contacts",
        help_text="Enter one email per line"
    )
    
    class Meta:
        model = OAuth2Client
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance:
            # Convert comma-separated values to lists for multi-select fields
            if instance.grant_types:
                self.initial['grant_types_list'] = instance.get_grant_types_list()
            
            if instance.response_types:
                self.initial['response_types_list'] = instance.get_response_types_list()
            
            # Convert comma-separated values to newline-separated for textareas
            if instance.redirect_uris:
                self.initial['redirect_uris_text'] = '\n'.join(instance.get_redirect_uris_list())
            
            if instance.audience:
                self.initial['audience_text'] = '\n'.join(instance.get_audience_list())
            
            if instance.contacts:
                self.initial['contacts_text'] = '\n'.join(instance.get_contacts_list())
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Convert multi-select fields back to comma-separated strings
        if 'grant_types_list' in cleaned_data:
            cleaned_data['grant_types'] = ','.join(cleaned_data.get('grant_types_list', []))
        
        if 'response_types_list' in cleaned_data:
            cleaned_data['response_types'] = ','.join(cleaned_data.get('response_types_list', []))
        
        # Convert newline-separated textareas back to comma-separated strings
        if 'redirect_uris_text' in cleaned_data:
            uris = cleaned_data.get('redirect_uris_text', '')
            cleaned_data['redirect_uris'] = ','.join([uri.strip() for uri in uris.split('\n') if uri.strip()])
        
        if 'audience_text' in cleaned_data:
            audiences = cleaned_data.get('audience_text', '')
            cleaned_data['audience'] = ','.join([aud.strip() for aud in audiences.split('\n') if aud.strip()])
        
        if 'contacts_text' in cleaned_data:
            contacts = cleaned_data.get('contacts_text', '')
            cleaned_data['contacts'] = ','.join([contact.strip() for contact in contacts.split('\n') if contact.strip()])
        
        return cleaned_data
