#!/bin/bash

# Exit script if any command fails
set -e

# Function to echo in green color for success messages
echo_success() {
    echo -e "\033[0;32m$1\033[0m"
}

# Function to echo in yellow color for progress messages
echo_progress() {
    echo -e "\033[0;33m$1\033[0m"
}

# Update package manager and install ffmpeg, npm, awscli
echo_progress "Setting up ffmpeg..."
apt-get update
apt-get install -y ffmpeg npm awscli tree

# Setup Backend
echo_progress "Setting up backend..."
python -m venv env || { echo "Failed to create virtual environment"; exit 1; }
source env/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
python -m pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }
pip install -r requirements.txt || { echo "Failed to install backend requirements"; exit 1; }

# Django Migrations (commented out, uncomment if needed)
# python manage.py migrate || { echo "Django migrate command failed"; exit 1; }

# Create superuser and Profile non-interactively
echo "from django.contrib.auth import get_user_model; from auth.models import Profile; User = get_user_model(); admin_user = User.objects.create_superuser('admin', 'admin@admin.com', '123'); Profile.objects.create(user=admin_user, phone_number='123456789', address='Admin Address')" | python manage.py shell || { echo "Failed to create superuser and profile"; exit 1; }
echo_success "Superuser and Profile created successfully."
echo_success "Done setting up backend."

# Setup Frontend
echo_progress "Setting up frontend..."
cd frontend || { echo "Failed to change directory to frontend"; exit 1; }
npm install || { echo "npm install failed"; exit 1; }
echo_success "Done setting up frontend."

cd .. # Go back to the root directory

echo_success "Project is ready"
