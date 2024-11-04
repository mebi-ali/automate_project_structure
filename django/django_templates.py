# Django project templates
SETTINGS_TEMPLATE = '''from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'usecase1.apps.Usecase1Config',
    'usecase2.apps.Usecase2Config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
'''

URLS_TEMPLATE = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/usecase1/', include('usecase1.urls')),
    path('api/v1/usecase2/', include('usecase2.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''

WSGI_TEMPLATE = '''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
'''

ASGI_TEMPLATE = '''import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
'''

MANAGE_TEMPLATE = '''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''

APP_MODELS_TEMPLATE = '''from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Item(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
'''

APP_SERIALIZERS_TEMPLATE = '''from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
'''

APP_VIEWS_TEMPLATE = '''from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(is_active=True)
'''

APP_URLS_TEMPLATE = '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

router = DefaultRouter()
router.register('items', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
'''

APP_ADMIN_TEMPLATE = '''from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
'''

APP_TESTS_TEMPLATE = '''from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Item

class ItemTests(APITestCase):
    def setUp(self):
        self.item_data = {
            'name': 'Test Item',
            'description': 'Test Description',
            'is_active': True
        }
        
    def test_create_item(self):
        url = reverse('item-list')
        response = self.client.post(url, self.item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Item.objects.get().name, 'Test Item')
'''

REQUIREMENTS_TEMPLATE = '''Django>=4.2.0,<5.0.0
djangorestframework>=3.14.0,<4.0.0
django-cors-headers>=4.0.0,<5.0.0
djangorestframework-simplejwt>=5.2.0,<6.0.0
python-dotenv>=1.0.0,<2.0.0
pytest>=7.3.1,<8.0.0
pytest-django>=4.5.2,<5.0.0
'''

ENV_TEMPLATE = '''DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
'''

GITIGNORE_TEMPLATE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Virtual Environment
venv/
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
'''

README_TEMPLATE = '''# {project_name}

A Django REST Framework project with a clean architecture and best practices.

## Features

- Django REST Framework
- JWT Authentication
- Modular app structure
- API versioning
- CORS support
- Testing setup
- Environment configuration

## Project Structure

{project_name}/
├── config/             # Project configuration
├── usecase1/          # First app
├── usecase2/          # Second app
├── manage.py          # Django management script
├── requirements.txt   # Project dependencies
└── .env              # Environment variables

## Setup

1. Create virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run migrations:

    ```bash
    python manage.py migrate
    ```

4. Create superuser:

    ```bash
    python manage.py createsuperuser
    ```

5. Run the development server:

    ```bash
    python manage.py runserver
    ```

## API Endpoints

- Admin interface: http://localhost:8000/admin/
- API v1: http://localhost:8000/api/v1/
- Swagger Documentation: http://localhost:8000/api/schema/swagger-ui/
- ReDoc Documentation: http://localhost:8000/api/schema/redoc/

## Testing

Run tests with:

    ```bash
    python manage.py test
    ```

Run tests with coverage:

    ```bash
    coverage run manage.py test
    coverage report
    ```

## Development

1. Make migrations:

    ```bash
    python manage.py makemigrations
    ```

2. Apply migrations:

    ```bash
    python manage.py migrate
    ```

3. Create new app:

    ```bash
    python manage.py startapp new_app
    ```

## Project Commands

### Data Management

    ```bash
    # Create database backup
    python manage.py dumpdata > backup.json

    # Load data from backup
    python manage.py loaddata backup.json

    # Clear database
    python manage.py flush
    ```

### Static Files

    ```bash
    # Collect static files
    python manage.py collectstatic

    # Clear static files
    python manage.py collectstatic --clear
    ```

## Deployment Checklist

1. Update `ALLOWED_HOSTS` in settings
2. Set `DEBUG = False` in production
3. Configure production database
4. Set up static files serving
5. Configure HTTPS
6. Set up proper email backend
7. Configure caching
8. Set up monitoring

## Environment Variables

Create a `.env` file in the project root:

    ```bash
    DEBUG=True
    SECRET_KEY=your-secret-key-here
    DATABASE_URL=sqlite:///db.sqlite3
    ALLOWED_HOSTS=localhost,127.0.0.1
    ```

## Dependencies

- Django
- Django REST Framework
- Django CORS Headers
- Django REST Framework SimpleJWT
- Python Dotenv
- Pytest Django
- Coverage

## License

This project is licensed under the MIT License.
'''

