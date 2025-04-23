#!/bin/bash

# This script tests the OAuth2 client management in Django admin

echo "Testing OAuth2 client management in Django admin..."

# Create a test user for Django admin if it doesn't exist
echo "Creating test superuser..."
cd /home/ubuntu/ory_django_auth
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"

# Make migrations for the OAuth2Client model
echo "Making migrations for the OAuth2Client model..."
python manage.py makemigrations
python manage.py migrate

# Run the Django development server in the background
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 5

echo "Server started with PID: $SERVER_PID"
echo ""
echo "You can now test the OAuth2 client management in Django admin by:"
echo ""
echo "1. Accessing the Django admin interface at: http://localhost:8000/admin/"
echo "2. Login with username 'admin' and password 'adminpassword'"
echo "3. Navigate to 'Hydra_auth > OAuth2 clients'"
echo "4. Create, view, update, and delete OAuth2 clients through the admin interface"
echo ""
echo "To stop the server, run: kill $SERVER_PID"
echo ""
echo "Note: For full testing, you'll need to have Hydra running as configured in docker-compose.yml"
