#!/bin/bash

# This script tests the OAuth2 client management functionality

echo "Testing OAuth2 client management functionality..."

# Create a test user for Django admin if it doesn't exist
echo "Creating test superuser..."
cd /home/ubuntu/ory_django_auth
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"

# Run the Django development server in the background
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 5

echo "Server started with PID: $SERVER_PID"
echo ""
echo "You can now test the OAuth2 client management functionality by:"
echo ""
echo "1. Accessing the client management interface at: http://localhost:8000/hydra/clients/"
echo "2. Login with username 'admin' and password 'adminpassword'"
echo "3. Create, view, update, and delete OAuth2 clients"
echo ""
echo "To stop the server, run: kill $SERVER_PID"
echo ""
echo "Note: For full testing, you'll need to have Hydra running as configured in docker-compose.yml"
