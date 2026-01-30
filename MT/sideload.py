#!/usr/bin/env python3

import os
import sys
import time
import subprocess

# Colors
ORANGE = "\033[38;5;208m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
RESET = "\033[0m"
DIM = "\033[2m"

def check_device_mode():
    """Checks if device is connected in Sideload or Recovery mode."""
    print(f"{DIM}[*] Checking device connection...{RESET}")
    try:
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
        if "sideload" in result.stdout:
            return "sideload"
        elif "recovery" in result.stdout:
            return "recovery"
        elif "device" in result.stdout:
            return "system"
        else:
            return None
    except Exception:
        return None

def wipe_data_twrp():
    """Attempts to wipe data using TWRP command line."""
    print(f"\n{ORANGE}► Attempting to Format Data (TWRP)...{RESET}")
    try:
        # Check logic: Cannot run shell commands in 'sideload' mode
        mode = check_device_mode()
        if mode == "sideload":
            print(f"{RED}⚠ Cannot Format Data while already in Sideload Mode.{RESET}")
            print(f"{DIM}Please Format Data manually from the Recovery menu after installation.{RESET}")
            time.sleep(2)
        else:
            # Try TWRP wipe command
            subprocess.run("adb shell twrp wipe data", shell=True)
            subprocess.run("adb shell twrp wipe cache", shell=True)
            print(f"{GREEN}✓ Wipe command sent.{RESET}")
            print(f"{DIM}If you are not in Sideload mode yet, please select 'Apply Update from ADB' on your phone now.{RESET}")
            input(f"\nPress {GREEN}Enter{RESET} when device is in Sideload mode...")
    except Exception as e:
        print(f"{RED}✗ Wipe Failed: {e}{RESET}")

def main():
    target_extension = ".zip"
    result_paths = []

    print(f"\n{ORANGE}► ADB Sideload Tool{RESET}")
    print(f"{DIM}Searching for .zip files in internal storage...{RESET}")

    # --- Scanning Logic (Copied from miflashf) ---
    for root, dirs, files in os.walk("/sdcard"):
        # Skip Android folder and hidden folders to save time
        if "Android" in root or "/." in root:
            continue

        zip_files = [f for f in files if f.endswith(target_extension)]
        for f in zip_files:
            result_paths.append(os.path.join(root, f))

    if not result_paths:
        print(f"\n{RED}✗ No .zip files found on the device!{RESET}")
        print(f"{DIM}Please download a Recovery ROM zip and try again.{RESET}\n")
        sys.exit(1)

    # --- Display List ---
    for i, result in enumerate(result_paths, start=1):
        # Display simplified name for readability
        print(f"\n {GREEN}{i}{RESET} - {result}")

    # --- User Selection ---
    selected_index = 0
    while True:
        try:
            choice = input(f"\nEnter your {GREEN}choice{RESET}: ").strip()
            selected_index = int(choice)
            if 1 <= selected_index <= len(result_paths):
                break
            else:
                print(f"\nInvalid choice! Select between 1 and {len(result_paths)}")
        except ValueError:
            print("\nInvalid input! Please enter a number.")

    selected_file = result_paths[selected_index - 1]
    
    # Drag-drop cleanup (just in case logic persists)
    selected_file = selected_file.replace("'", "").replace('"', "")

    print(f"\n{DIM}{'━'*40}{RESET}")
    print(f"Selected: {ORANGE}{os.path.basename(selected_file)}{RESET}")
    print(f"{DIM}{'━'*40}{RESET}")

    # --- Format Data / Clean Flash Logic ---
    print(f"\nDo you want to {RED}Format Data{RESET} (Clean Flash)?")
    print(f"{DIM}(Recommended for changing ROMs){RESET}")
    
    while True:
        wipe_choice = input(f"Type {GREEN}'y'{RESET} for Yes or {GREEN}'n'{RESET} for No: ").strip().lower()
        
        if wipe_choice == 'y':
            wipe_data_twrp()
            break
        elif wipe_choice == 'n':
            print(f"\n{ORANGE}► Dirty Flash / Update Selected.{RESET}")
            break
        else:
            print("Invalid input.")

    # --- Execution ---
    print(f"\n{ORANGE}► Starting Sideload...{RESET}")
    print(f"{DIM}Ensure 'Apply Update from ADB' is active on device.{RESET}\n")
    
    try:
        # Checking if device is actually connected before running command
        subprocess.run("adb wait-for-device", shell=True)
        
        # Run Sideload
        subprocess.run(f"adb sideload \"{selected_file}\"", shell=True)
        
        print(f"\n{GREEN}✓ Process Finished.{RESET}")
        
    except KeyboardInterrupt:
        print(f"\n\n{RED}✗ Operation Cancelled.{RESET}")
    except Exception as e:
        print(f"\n{RED}✗ Error: {e}{RESET}")

if __name__ == "__main__":
    main()
