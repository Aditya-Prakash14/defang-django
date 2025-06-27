#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting E-learning Platform deployment..."

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create media directories
echo "📂 Creating media directories..."
mkdir -p media/profile_pictures
mkdir -p media/course_thumbnails
mkdir -p media/lesson_videos
mkdir -p media/lesson_materials
mkdir -p media/certificates
mkdir -p media/certificate_templates

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('✅ Admin user already exists')
EOF

# Create default certificate template
echo "🏆 Setting up certificate template..."
python manage.py shell << EOF
from certificates.models import CertificateTemplate
if not CertificateTemplate.objects.exists():
    CertificateTemplate.objects.create(
        name='Default Template',
        description='Default certificate template',
        is_default=True,
        is_active=True
    )
    print('✅ Default certificate template created')
else:
    print('✅ Certificate template already exists')
EOF

echo "✅ Setup completed successfully!"
echo "🌐 Starting Gunicorn server..."

# Start Gunicorn
exec gunicorn defang_sample.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile -
