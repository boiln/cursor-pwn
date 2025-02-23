from __future__ import annotations

import ctypes
import getpass
import hashlib
import json
import os
import platform
import shutil
import sys
import time
import uuid
import winreg
from pathlib import Path

import colorama
import psutil
from colorama import Fore, Style

colorama.init()

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
NC = Style.RESET_ALL

LOGO = """
    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
"""


def print_banner():
    """Print the application banner."""
    print(LOGO)
    print(f"{BLUE}================================{NC}")
    print(f"{GREEN}   Cursor Device ID Modifier Tool          {NC}")
    print(f"{BLUE}================================{NC}")
    print("")


def get_cursor_version():
    """Get the installed Cursor version."""
    try:
        alt_path = os.path.join(
            os.environ["LOCALAPPDATA"],
            "cursor",
            "resources",
            "app",
            "package.json",
        )

        if os.path.exists(alt_path):
            with open(alt_path, encoding="utf-8") as f:
                package_json = json.load(f)
                if package_json.get("version"):
                    print(
                        f"{GREEN}[INFO]{NC} Current Cursor version: v{package_json['version']}",
                    )
                    return package_json["version"]

        print(f"{YELLOW}[WARNING]{NC} Could not detect Cursor version")
        print(f"{YELLOW}[TIP]{NC} Please ensure Cursor is properly installed")
        return None

    except Exception as e:
        print(f"{RED}[ERROR]{NC} Failed to get Cursor version: {e!s}")
        return None


def check_admin():
    """Check if the script is running with admin privileges."""
    try:
        return os.getuid() == 0
    except AttributeError:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except AttributeError:
            return False


def update_machine_guid():
    """Update the MachineGuid in Windows Registry."""
    try:
        # Check for admin privileges
        if not check_admin():
            print(f"{RED}[ERROR]{NC} Please run this script as Administrator")
            return False

        # Registry path
        registry_path = r"SOFTWARE\Microsoft\Cryptography"

        try:
            # Get current MachineGuid
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                registry_path,
                0,
                winreg.KEY_READ,
            ) as key:
                current_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                print(f"{GREEN}[INFO]{NC} Current registry value:")
                print("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography")
                print(f"    MachineGuid    REG_SZ    {current_guid}")

        except Exception as e:
            print(f"{RED}[ERROR]{NC} Could not read current MachineGuid: {e!s}")
            return False

        new_guid = str(uuid.uuid4())

        try:
            # Update registry
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                registry_path,
                0,
                winreg.KEY_WRITE,
            ) as key:
                winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)

            # Verify update
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                registry_path,
                0,
                winreg.KEY_READ,
            ) as key:
                verify_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                if verify_guid != new_guid:
                    raise Exception(
                        "Verification failed: Updated value does not match expected value",
                    )

            print(f"{GREEN}[INFO]{NC} Registry updated successfully:")
            print("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography")
            print(f"    MachineGuid    REG_SZ    {new_guid}")
            return True

        except Exception as e:
            print(f"{RED}[ERROR]{NC} Failed to update registry: {e!s}")
            return False

    except Exception as e:
        print(f"{RED}[ERROR]{NC} Error while processing registry: {e!s}")
        return False


def disable_auto_update():
    """Disable Cursor auto-update functionality."""
    updater_path = os.path.join(os.environ["LOCALAPPDATA"], "cursor-updater")

    try:
        # Remove existing directory if it exists
        if os.path.exists(updater_path):
            if os.path.isfile(updater_path):
                os.remove(updater_path)
            else:
                shutil.rmtree(updater_path)
            print(f"{GREEN}[INFO]{NC} Successfully deleted cursor-updater directory")

        # Create blocking file
        with open(updater_path, "w") as f:
            pass

        # Set read-only attribute
        os.chmod(updater_path, 0o444)  # Read-only for all users

        print(f"{GREEN}[INFO]{NC} Successfully disabled auto-update")
        return True

    except Exception as e:
        print(f"{RED}[ERROR]{NC} Failed to disable auto-update: {e!s}")
        return False


def generate_machine_id():
    """Generate a new machine ID hash."""
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()


def generate_uuid():
    """Generate a new UUID."""
    return str(uuid.uuid4()).upper()


def check_path_exists(path_parts):
    """Check if each directory in the path exists.
    Returns tuple (bool, str) - (success, error_message)
    """
    if len(path_parts) > 0 and path_parts[0].endswith(":"):
        current_path = Path(path_parts[0] + "\\" + path_parts[1])
        remaining_parts = path_parts[2:]
    else:
        current_path = Path(path_parts[0])
        remaining_parts = path_parts[1:]

    for part in remaining_parts:
        current_path = current_path / part
        if not current_path.exists():
            return False, f"Path not found: {current_path}"

    return True, ""


def close_cursor_processes():
    """Close all running Cursor processes and verify they're closed."""
    cursor_processes = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if "cursor.exe" in proc.info["name"].lower():
                cursor_processes.append(proc)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not cursor_processes:
        print(f"{GREEN}[INFO]{NC} No running Cursor processes found")
        return True

    print(
        f"{GREEN}[INFO]{NC} Found {len(cursor_processes)} Cursor processes running, attempting to close...",
    )

    # First try graceful termination
    for proc in cursor_processes:
        try:
            proc.terminate()
        except psutil.NoSuchProcess:
            continue

    # Wait up to 5 seconds for processes to terminate
    time.sleep(2)

    # Check if any processes remain and force kill if necessary
    remaining_processes = []
    for proc in cursor_processes:
        try:
            if proc.is_running():
                remaining_processes.append(proc)
        except psutil.NoSuchProcess:
            continue

    if remaining_processes:
        print(
            f"{YELLOW}[WARNING]{NC} Some processes didn't close gracefully, forcing termination...",
        )
        for proc in remaining_processes:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                continue

    # Final verification
    time.sleep(1)
    for proc in psutil.process_iter(["name"]):
        try:
            if "cursor.exe" in proc.info["name"].lower():
                print(f"{RED}[ERROR]{NC} Failed to close all Cursor processes!")
                return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    print(f"{GREEN}[INFO]{NC} All Cursor processes have been closed successfully")
    return True


def update_storage_file():
    """Update the Cursor storage file with new device IDs."""
    if platform.system() != "Windows" or int(platform.version().split(".")[0]) < 10:
        print(f"{RED}[ERROR]{NC} This script only supports Windows 10 and 11")
        return False

    try:
        print_banner()

        # First close all Cursor processes
        if not close_cursor_processes():
            print(
                f"{RED}[ERROR]{NC} Unable to close all Cursor processes, please close them manually and try again",
            )
            return False

        # Get current username
        current_user = getpass.getuser()

        path_parts = [
            "C:\\",
            "Users",
            current_user,
            "AppData",
            "Roaming",
            "Cursor",
            "User",
            "globalStorage",
            "storage.json",
        ]

        # Create backup directory
        backup_dir = os.path.join(os.path.dirname(os.path.join(*path_parts)), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Check each directory in the path
        success, error_message = check_path_exists(path_parts[:-1])  # Exclude file name
        if not success:
            print(f"{RED}[ERROR]{NC} {error_message}")
            return False

        # Construct complete file path
        file_path = Path(*path_parts)

        # Check if the file exists
        if not file_path.is_file():
            print(f"{RED}[ERROR]{NC} Configuration file not found: {file_path}")
            return False

        # Create backup
        backup_name = f"storage.json.backup_{time.strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.copy2(file_path, backup_path)
        print(f"{GREEN}[INFO]{NC} Created configuration backup: {backup_path}")

        # Read existing file
        with open(file_path, encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(f"{RED}[ERROR]{NC} Invalid configuration file format")
                return False

        # Store original data for comparison
        original_data = data.copy()

        # Update IDs
        if "telemetry.sqmId" in data:
            data["telemetry.sqmId"] = "{" + generate_uuid() + "}"

        if "telemetry.machineId" in data:
            data["telemetry.machineId"] = generate_machine_id()

        if "telemetry.devDeviceId" in data:
            data["telemetry.devDeviceId"] = str(uuid.uuid4())

        if "telemetry.macMachineId" in data:
            data["telemetry.macMachineId"] = generate_machine_id()

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print(f"\n{GREEN}[INFO]{NC} File updated successfully: {file_path}")
        print(f"\n{GREEN}[INFO]{NC} Updated configuration:")
        telemetry_keys = [
            "telemetry.sqmId",
            "telemetry.machineId",
            "telemetry.devDeviceId",
            "telemetry.macMachineId",
        ]

        for key in telemetry_keys:
            if key in original_data and key in data:
                print(f"\n{key}:")
                print(f"  Old: {original_data[key]}")
                print(f"  New: {data[key]}")

        update_machine_guid()

        print(f"\n{YELLOW}[QUESTION]{NC} Do you want to disable Cursor auto-update?")
        print("0) No - Keep default settings")
        print("1) Yes - Disable auto-update")
        choice = input("Enter option (0): ").strip() or "0"

        if choice == "1":
            disable_auto_update()

        print(f"\n{GREEN}[INFO]{NC} Cursor IDs have been successfully modified!")
        print(f"\n{GREEN}[INFO]{NC} File structure:")
        print(f"{BLUE}{os.path.dirname(file_path)}{NC}")
        print("├── storage.json (modified)")
        print("└── backups")

        backup_files = os.listdir(backup_dir)
        if backup_files:
            for backup_file in backup_files:
                print(f"    └── {backup_file}")
        else:
            print("    └── (empty)")

        print(f"\n{GREEN}================================{NC}")
        print(f"{GREEN}================================{NC}")
        print(
            f"\n{GREEN}[INFO]{NC} Please restart Cursor to apply the new configuration",
        )

        return True

    except Exception as e:
        print(f"{RED}[ERROR]{NC} An error occurred: {e!s}")
        return False


if __name__ == "__main__":
    # Set console output encoding to UTF-8
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    update_storage_file()
    input("\nPress Enter to exit...")
