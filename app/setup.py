#!/usr/bin/env python3
"""
Setup script for E-learning Platform
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_platform():
    """Setup the E-learning Platform"""
    
    print("🚀 Setting up E-learning Platform")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'defang_sample.settings')
    django.setup()
    
    # Run migrations
    print("🔄 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Collect static files
    print("🔄 Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected")
    except Exception as e:
        print(f"⚠️  Static files collection failed: {e}")
        # This is not critical for development
    
    # Create media directories
    media_dirs = ['media/profile_pictures', 'media/course_thumbnails', 'media/lesson_videos', 
                  'media/lesson_materials', 'media/certificates', 'media/certificate_templates']
    
    for dir_path in media_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("✅ Media directories created")
    
    # Run tests
    print("🔄 Running tests...")
    try:
        execute_from_command_line(['manage.py', 'test', '--verbosity=1'])
        print("✅ All tests passed")
    except Exception as e:
        print(f"⚠️  Some tests failed: {e}")
        # Continue setup even if tests fail
    
    print("\n" + "=" * 50)
    print("🎉 E-learning Platform setup completed!")
    print("\n📋 Next Steps:")
    print("1. Create a superuser:")
    print("   python manage.py createsuperuser")
    print("\n2. Start the development server:")
    print("   python manage.py runserver")
    print("\n3. Access the platform:")
    print("   - API Root: http://localhost:8000/api/")
    print("   - Admin Panel: http://localhost:8000/admin/")
    print("   - API Documentation: See api_documentation.md")
    print("\n4. Test the API:")
    print("   python integration_tests.py")
    
    return True

if __name__ == "__main__":
    success = setup_platform()
    sys.exit(0 if success else 1)
