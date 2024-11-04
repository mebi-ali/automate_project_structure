import os
import sys
import venv
import subprocess
from pathlib import Path
import platform
from django_templates import (
    SETTINGS_TEMPLATE,
    URLS_TEMPLATE,
    WSGI_TEMPLATE,
    ASGI_TEMPLATE,
    MANAGE_TEMPLATE,
    APP_MODELS_TEMPLATE,
    APP_SERIALIZERS_TEMPLATE,
    APP_VIEWS_TEMPLATE,
    APP_URLS_TEMPLATE,
    APP_ADMIN_TEMPLATE,
    APP_TESTS_TEMPLATE,
    REQUIREMENTS_TEMPLATE,
    ENV_TEMPLATE,
    GITIGNORE_TEMPLATE,
    README_TEMPLATE
)

def run_command(command, cwd=None):
    """Run a command and return its output"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def create_and_activate_venv(project_path: Path):
    """Create and activate virtual environment"""
    venv_path = project_path / "venv"
    print("Creating virtual environment...")
    venv.create(venv_path, with_pip=True)
    
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"

    return str(activate_script), str(python_path), str(pip_path)

def create_file_with_content(file_path: Path, content: str):
    """Helper function to create a file with content"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

def create_django_app(project_path: Path, app_name: str):
    """Create a Django app with all necessary files"""
    app_path = project_path / app_name
    app_path.mkdir(exist_ok=True)
    
    # Create app files
    create_file_with_content(app_path / "__init__.py", "")
    create_file_with_content(app_path / "models.py", APP_MODELS_TEMPLATE)
    create_file_with_content(app_path / "serializers.py", APP_SERIALIZERS_TEMPLATE)
    create_file_with_content(app_path / "views.py", APP_VIEWS_TEMPLATE)
    create_file_with_content(app_path / "urls.py", APP_URLS_TEMPLATE)
    create_file_with_content(app_path / "admin.py", APP_ADMIN_TEMPLATE)
    create_file_with_content(app_path / "tests.py", APP_TESTS_TEMPLATE)
    
    # Create migrations directory
    (app_path / "migrations").mkdir(exist_ok=True)
    create_file_with_content(app_path / "migrations" / "__init__.py", "")

def create_project_structure(project_name: str):
    """Create the complete project structure"""
    base_path = Path(project_name)
    
    # Create project directories
    config_path = base_path / "config"
    config_path.mkdir(parents=True, exist_ok=True)
    
    # Create config files
    create_file_with_content(config_path / "__init__.py", "")
    create_file_with_content(config_path / "settings.py", SETTINGS_TEMPLATE)
    create_file_with_content(config_path / "urls.py", URLS_TEMPLATE)
    create_file_with_content(config_path / "wsgi.py", WSGI_TEMPLATE)
    create_file_with_content(config_path / "asgi.py", ASGI_TEMPLATE)
    
    # Create manage.py
    create_file_with_content(base_path / "manage.py", MANAGE_TEMPLATE)
    os.chmod(base_path / "manage.py", 0o755)  # Make manage.py executable
    
    # Create apps
    create_django_app(base_path, "usecase1")
    create_django_app(base_path, "usecase2")
    
    # Create project files
    create_file_with_content(base_path / "requirements.txt", REQUIREMENTS_TEMPLATE)
    create_file_with_content(base_path / ".env", ENV_TEMPLATE)
    create_file_with_content(base_path / ".gitignore", GITIGNORE_TEMPLATE)
    create_file_with_content(base_path / "README.md", README_TEMPLATE.format(project_name=project_name))
    
    # Initialize git repository
    print("Initializing git repository...")
    run_command("git init", cwd=base_path)
    
    # Create and activate virtual environment
    print("Setting up virtual environment...")
    activate_script, python_path, pip_path = create_and_activate_venv(base_path)
    
    # Install dependencies
    print("Installing dependencies...")
    run_command(f'"{pip_path}" install --upgrade pip', cwd=base_path)
    run_command(f'"{pip_path}" install -r requirements.txt', cwd=base_path)
    
    # Initialize Django project
    print("Initializing Django project...")
    run_command(f'"{python_path}" manage.py migrate', cwd=base_path)
    
    return activate_script

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_django_project.py project_name")
        sys.exit(1)
    
    project_name = sys.argv[1]
    print(f"Creating new Django project: {project_name}")
    
    try:
        activate_script = create_project_structure(project_name)
        
        if platform.system() == "Windows":
            activate_cmd = activate_script
        else:
            activate_cmd = f"source {activate_script}"

        print(f"""
Project {project_name} created successfully!

Your virtual environment has been created and dependencies installed.

To activate the virtual environment:
{activate_cmd}

To run the development server:
cd {project_name}
python manage.py runserver

Your API will be available at:
- Admin interface: http://localhost:8000/admin/
- API v1: http://localhost:8000/api/v1/
- API Documentation: http://localhost:8000/api/schema/swagger-ui/

Happy coding! 🚀
""")
    except Exception as e:
        print(f"Error creating project: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
