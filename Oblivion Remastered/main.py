import os
import shutil
import datetime
import getpass
import subprocess
import logging
from pathlib import Path

# Configure logging
try:
    os.makedirs(r"C:\Windows\Logs\Oblivion_Remastered_Steam_Save_Patch", exist_ok=True)
    log_file = r"C:\Windows\Logs\Oblivion_Remastered_Steam_Save_Patch\Events.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
except Exception as e:
    print(f"Error setting up logging: {e}")
    log_file = None
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_and_print(message, level="info"):
    """Log a message and print it to the console."""
    print(message)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)

def get_user_paths():
    """Get the local and OneDrive Documents paths for the current user."""
    username = getpass.getuser()
    local_docs = Path(f"C:/Users/{username}/Documents/My Games/Oblivion Remastered")
    onedrive_docs = Path(f"C:/Users/{username}/OneDrive/Documents/My Games/Oblivion Remastered")
    return local_docs, onedrive_docs


def backup_saves(source_folder, backup_dir):
    """Backup save files to a timestamped folder."""
    if not source_folder.exists():
        log_and_print(f"No saves found in {source_folder}", "error")
        return
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(backup_dir) / f"oblivion_saves_backup_{timestamp}"
    log_and_print(f"Backing up saves from {source_folder} to {backup_path}")
    shutil.copytree(source_folder, backup_path)
    log_and_print(f"Backup completed: {backup_path}")


def create_symlink(source, target):
    """Create a symbolic link from source to target."""
    try:
        subprocess.run(
            ["mklink", "/J", str(source), str(target)],
            shell=True, check=True, capture_output=True, text=True
        )
        log_and_print(f"Symlink created: {source} -> {target}")
    except subprocess.CalledProcessError as e:
        log_and_print(f"Error creating symlink: {e.stderr}", "error")
        raise


import ctypes
import sys

def main():
    # Check for administrator privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        log_and_print("Attempting to relaunch with administrator privileges...")
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except Exception as e:
            log_and_print(f"Failed to elevate permissions: {e}", "error")
        sys.exit()

    log_and_print("Oblivion Remastered Steam Cloud Sync Fix Script")
    log_and_print("This script will create a symlink to fix save syncing issues.")
    log_and_print("Ensure you run this script as Administrator.")
    log_and_print("Backup your saves before proceeding!")

    # Get paths
    local_docs, onedrive_docs = get_user_paths()
    backup_dir = Path(f"C:/Users/{getpass.getuser()}/Desktop/Oblivion_Backups")

    # Check if folders exist
    if not onedrive_docs.exists():
        log_and_print(f"Error: OneDrive folder not found at {onedrive_docs}", "error")
        log_and_print("Ensure OneDrive is set up and contains Oblivion Remastered saves.")
        return
    if not local_docs.parent.exists():
        log_and_print(f"Error: Local Documents folder not found at {local_docs.parent}", "error")
        return

    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup saves from both locations
    log_and_print("\nBacking up save files...")
    backup_saves(local_docs, backup_dir)
    backup_saves(onedrive_docs, backup_dir)

    # Confirm with user before proceeding
    input("\nPress Enter to continue with symlink creation, or Ctrl+C to cancel...")

    # Delete local save folder if it exists
    if local_docs.exists():
        log_and_print(f"Deleting local save folder: {local_docs}")
        shutil.rmtree(local_docs, ignore_errors=True)

    # Create symlink
    log_and_print(f"\nCreating symlink from {local_docs} to {onedrive_docs}")
    create_symlink(local_docs, onedrive_docs)

    log_and_print("\nScript completed successfully!")
    log_and_print("1. Launch Steam and ensure Cloud Sync is enabled for Oblivion Remastered.")
    log_and_print("2. Test the game on all devices to verify syncing.")
    log_and_print(f"3. Backups are saved in {backup_dir}.")
    log_and_print("If issues persist, check Steam Community Discussions or contact support.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_and_print("\nScript cancelled by user.", "error")
    except Exception as e:
        log_and_print(f"\nAn error occurred: {e}", "error")
        log_and_print("Please ensure you are running this script as Administrator.")
        log_and_print("Contact support or check Steam Community Discussions for help.")
        log_and_print("See 'C:\Windows\Logs\Oblivion_Remastered_Steam_Save_Patch\Events.log' for details.")
    finally:
        log_and_print("\nPress Enter to close this window...")
        input()
        exit()