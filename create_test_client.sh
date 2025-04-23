#!/bin/bash

# This script creates a test OAuth 2.0 client in Ory Hydra
# and tests the authentication flow

# Wait for Hydra to be ready
echo "Waiting for Hydra to be ready..."
sleep 10

# Create a test client
echo "Creating test OAuth client..."
docker-compose exec hydra \
  hydra create client \
  --endpoint http://localhost:4445 \
  --id test-client \
  --secret test-secret \
  --grant-type authorization_code,refresh_token \
  --response-type code,id_token \
  --scope openid,offline,email,profile \
  --redirect-uri http://localhost:8000/callback \
  --token-endpoint-auth-method client_secret_basic

echo "Test client created successfully!"
echo ""
echo "To test the authentication flow, run the following command:"
echo ""
echo "docker-compose exec hydra \\"
echo "  hydra perform authorization-code \\"
echo "  --client-id test-client \\"
echo "  --client-secret test-secret \\"
echo "  --endpoint http://localhost:4444/ \\"
echo "  --port 8000 \\"
echo "  --scope openid,offline,email,profile"
echo ""
echo "This will start the OAuth 2.0 flow and redirect you to the login page."
echo "After successful login and consent, you will receive the authorization code."
