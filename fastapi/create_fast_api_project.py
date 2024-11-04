import os
import sys
import venv
import subprocess
from pathlib import Path
import platform
from fastApi_templates import (
    COMMON_FILES,
    USECASE_FILES,
    TEST_FILES,
    MAIN_APP_TEMPLATE,
    SETUP_TEMPLATE,
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

def create_project_structure(project_name: str):
    """Create the complete project structure"""
    base_path = Path(project_name)
    
    # Create directory structure
    directories = [
        base_path / "src" / "common",
        base_path / "src" / "usecase1",
        base_path / "src" / "usecase2",
        base_path / "tests" / "test_usecase1",
        base_path / "tests" / "test_usecase2",
    ]
    
    print("Creating project structure...")
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "__init__.py").touch()

    # Create common module files
    print("Creating common module files...")
    for filename, content in COMMON_FILES.items():
        create_file_with_content(base_path / "src" / "common" / filename, content)

    # Create usecase files
    print("Creating usecase files...")
    for usecase in ["usecase1", "usecase2"]:
        for filename, content in USECASE_FILES.items():
            create_file_with_content(base_path / "src" / usecase / filename, content)

    # Create test files
    print("Creating test files...")
    for filename, content in TEST_FILES.items():
        create_file_with_content(base_path / "tests" / filename, content)

    # Create test files for each usecase
    for usecase in ["usecase1", "usecase2"]:
        test_content = f'''import pytest
from fastapi.testclient import TestClient

def test_{usecase}_create_item(client):
    response = client.post(
        "/{usecase}/items/",
        json={{"name": "test item", "description": "test description"}}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test item"
'''
        create_file_with_content(base_path / "tests" / f"test_{usecase}" / "test_routes.py", test_content)

    # Create main application files
    print("Creating main application files...")
    create_file_with_content(base_path / "main.py", MAIN_APP_TEMPLATE)
    create_file_with_content(base_path / "setup.py", SETUP_TEMPLATE.format(project_name=project_name))
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
    run_command(f'"{pip_path}" install -e .', cwd=base_path)

    return activate_script

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_project.py project_name")
        sys.exit(1)
    
    project_name = sys.argv[1]
    print(f"Creating new project: {project_name}")
    
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

To run the application:
cd {project_name}
python main.py

Your API will be available at http://localhost:8000
API documentation will be at http://localhost:8000/docs

To run tests:
pytest

Happy coding! 🚀
""")
    except Exception as e:
        print(f"Error creating project: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
