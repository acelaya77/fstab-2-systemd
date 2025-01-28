#!/usr/bin/env python3

import re
import subprocess
from pathlib import Path


def create_unit_file(unit_file_name, line_num, device, mountpoint, fstype, options):
    """Creates a systemd mount unit file."""
    unit_file = Path("/etc/systemd/system") / unit_file_name

    try:
        # Write to the unit file
        with unit_file.open("w") as f:
            f.write(f"# {unit_file_name}\n\n")
            f.write("[Unit]\n")
            f.write(f"Description=Mount from fstab (line {line_num})\n")
            f.write("After=network.target\n\n")
            f.write("[Mount]\n")
            f.write(f"What={device}\n")
            f.write(f"Where={mountpoint}\n")
            f.write(f"Type={fstype}\n")
            f.write(f"Options={options}\n")
            f.write("TimeoutSec=15\n")
            f.write(f"ExecStartPre=/bin/mkdir -p {mountpoint}\n\n")
            f.write("[Install]\n")
            f.write("WantedBy=multi-user.target\n")

        print(f"Created unit file: {unit_file}")
    except OSError as e:
        print(f"Error writing to {unit_file}: {e}")
        return False

    return True


def enable_and_start_unit(unit_file_name):
    """Enables and starts the systemd unit."""
    try:
        # Enable the unit (with sudo)
        subprocess.run(["sudo", "systemctl", "enable", unit_file_name], check=True)
        print(f"Enabled unit: {unit_file_name}")

        # Start the unit (with sudo)
        subprocess.run(["sudo", "systemctl", "start", unit_file_name], check=True)
        print(f"Started unit: {unit_file_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error enabling or starting {unit_file_name}: {e}")
        return False

    return True


def process_fstab_line(line_num, line):
    """Processes a line from fstab and returns the relevant data."""
    match = re.match(
        r"^(?P<device>.*?)\s+(?P<mountpoint>.*?)\s+(?P<fstype>.*?)\s+(?P<options>.*?)\s+(?P<dump>.*?)\s+(?P<passno>.*?)$",
        line,
    )
    if not match:
        return None

    device = match.group("device")
    mountpoint = match.group("mountpoint")
    fstype = match.group("fstype")
    options = match.group("options")

    # Use systemd-escape to format the unit file name based on the mount point
    unit_file_name = subprocess.check_output(
        ["systemd-escape", "--suffix=mount", mountpoint], text=True
    ).strip()

    # Remove leading dash if it exists
    if unit_file_name.startswith("-"):
        unit_file_name = unit_file_name[1:]

    return unit_file_name, device, mountpoint, fstype, options


def fstab_to_systemd(fstab_file):
    """Converts selected lines from an fstab file to systemd unit files."""
    try:
        with open(fstab_file, "r") as f:
            fstab_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: fstab file not found at {fstab_file}")
        return

    print("Found the following entries in fstab:")
    for i, line in enumerate(fstab_lines):
        print(f"{i+1}: {line.strip()}")

    selected_lines = get_selected_lines(fstab_lines)

    for line_num in selected_lines:
        if 0 < line_num <= len(fstab_lines):
            line = fstab_lines[line_num - 1]
            result = process_fstab_line(line_num, line)
            if result:
                unit_file_name, device, mountpoint, fstype, options = result

                # Create the systemd unit file
                if create_unit_file(
                    unit_file_name, line_num, device, mountpoint, fstype, options
                ):
                    # Enable and start the unit
                    if enable_and_start_unit(unit_file_name):
                        # Comment the used line in fstab
                        fstab_lines[line_num - 1] = f"# {line}"
                else:
                    print(f"Failed to create unit file for {unit_file_name}")
            else:
                print(
                    f"Warning: Line {line_num} in fstab does not match expected format."
                )
        else:
            print(f"Warning: Invalid line number: {line_num}")

    # Write the modified fstab back to the file
    try:
        with open(fstab_file, "w") as f:
            f.writelines(fstab_lines)
    except PermissionError:
        print(f"Error: Permission denied to write to {fstab_file}.")
        print("You may need to run the script with sudo.")
        return


def get_selected_lines(fstab_lines):
    """Prompts user to select lines to convert."""
    while True:
        try:
            selected_lines_input = input(
                "Enter line numbers or ranges to convert (comma-separated, or 'all'): "
            )
            selected_lines = []
            for item in selected_lines_input.split(","):
                if "-" in item:
                    start, end = map(int, item.split("-"))
                    selected_lines.extend(range(start, end + 1))
                elif item.isdigit():
                    selected_lines.append(int(item))
                elif item.lower() == "all":
                    selected_lines = list(range(1, len(fstab_lines) + 1))
                    break
                else:
                    raise ValueError
            return selected_lines
        except ValueError:
            print(
                "Invalid input. Please enter line numbers, ranges (e.g., 23-26), or 'all'."
            )


if __name__ == "__main__":
    fstab_to_systemd("/etc/fstab")
