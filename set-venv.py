from typing import Union
from pathlib import Path
from subprocess import run, check_output, STDOUT, CalledProcessError
from shutil import rmtree, disk_usage
from sys import exit


WHITE = '07'
GREEN = '0A'
RED = '0C'

def set_color(color: str) -> None:
    run(['color', color], shell=True)


try:
    set_color(WHITE)

    def get_python_version(python_path: Path) -> Union[str, None]:
        try:
            output = check_output([str(python_path), '--version'], stderr=STDOUT, text=True)
            return output.strip().split(' ')[1].replace('.', str())
        except CalledProcessError:
            return None

    python_paths = {
        '3.11': Path(r'C:\Program Files\Python311\python.exe'),
        '3.12': Path(r'C:\Program Files\Python312\python.exe')
    }

    python_versions = {version: get_python_version(path) for version, path in python_paths.items()}

    while True:
        input_python_version = str(input(f'\n[question] Which Python version do you want to use? (available: {", ".join(python_versions.values())}): ')).strip()
        if input_python_version in python_versions.values():
            break

        print('[error] Invalid Python version! Please choose from the available versions above.')

    auto_install_packages = str(input('[question] Do you want to install packages from the requirements.txt file? (press Enter to say "yes" or type anything else to say "no"): ')).strip()
    if not auto_install_packages:
        auto_install_packages = True
    else:
        auto_install_packages = False

    selected_python_path = None

    venv_path = Path('.venv')

    if venv_path.exists():
        print('[info] Deleting the current virtual environment...')
        rmtree(venv_path, ignore_errors=True)

    print('[info] Creating a new virtual environment...')
    selected_python_path = next(path for version, path in python_paths.items() if python_versions[version] == input_python_version)
    run([str(selected_python_path), '-m', 'venv', str(venv_path)], check=True)

    print('[info] Activating the virtual environment...')
    run([str(venv_path / 'Scripts' / 'activate.bat')], check=True)

    if auto_install_packages:
        venv_path_source_size = disk_usage(venv_path).used
        requirements_file = Path('requirements.txt')

        if requirements_file.exists():
            with open(requirements_file, 'r') as file:
                if not file.read().strip():
                    print(f'[warning] The requirements file is empty! No packages to install.')
                else:
                    print('[info] Installing packages from requirements.txt file...')
                    run([str(venv_path / 'Scripts' / 'pip.exe'), 'install', '-r', str(requirements_file)], check=True)
                    venv_path_new_size = disk_usage(venv_path).used
                    print(f'[success] The packages were successfully installed and took up {(venv_path_new_size - venv_path_source_size) / 1024 / 1024:.2f} MB of space. (total: {venv_path_new_size / 1024 / 1024:.2f} MB)')
        else:
            print('[warning] The requirements file does not exist! Creating an empty requirements.txt file for you...')
            requirements_file.touch(exist_ok=True)
    else:
        print('[info] Skipping the installation of packages from requirements.txt file...')

    set_color(GREEN)
    print('[success] Your virtual environment is ready! Exiting...')
    exit(0)
except Exception as e:
    set_color(RED)
    print(f'[error] An unexpected error occurred: {e}')
    exit(1)
