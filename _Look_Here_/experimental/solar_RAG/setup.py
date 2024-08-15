import venv
import subprocess
import sys
import os
import shutil

def remove_directory(path):
    if os.path.exists(path):
        print(f"Removing existing directory: {path}")
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Error removing directory: {e}")
            print("Please close any applications that might be using this directory and try again.")
            sys.exit(1)

def create_venv(venv_path):
    print(f"Creating virtual environment in {venv_path}...")
    try:
        remove_directory(venv_path)
        venv.create(venv_path, with_pip=True)
    except PermissionError:
        print(f"Error: Unable to create {venv_path}. You may need to run this script with administrator privileges.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while creating the virtual environment: {e}")
        sys.exit(1)

def install_requirements(venv_path):
    pip_path = os.path.join(venv_path, 'bin', 'pip') if os.name != 'nt' else os.path.join(venv_path, 'Scripts', 'pip')
    requirements_path = 'requirements.txt'
    print("Installing requirements...")
    try:
        subprocess.check_call([pip_path, 'install', '-r', requirements_path])
    except subprocess.CalledProcessError:
        print("Error: Failed to install requirements. Please check your requirements.txt file and internet connection.")
        sys.exit(1)

def main():
    venv_path = 'solar_rag_env'
    create_venv(venv_path)
    install_requirements(venv_path)
    print("\nSetup complete! To activate the environment:")
    if os.name == 'nt':  # Windows
        print(f"Run: .\\{venv_path}\\Scripts\\activate")
    else:  # macOS and Linux
        print(f"Run: source {venv_path}/bin/activate")

if __name__ == "__main__":
    main()