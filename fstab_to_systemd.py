#!/usr/bin/env python3

import os
import re
import subprocess


def fstab_to_systemd(fstab_file, unit_file_base):
    """
    Converts selected lines from an fstab file to systemd unit files.

    Args:
      fstab_file: Path to the fstab file.
      unit_file_base: Base name for the output systemd unit files.
    """
    try:
        with open(fstab_file, "r") as f:
            fstab_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: fstab file not found at {fstab_file}")
        return

    print("Found the following entries in fstab:")
    for i, line in enumerate(fstab_lines):
        print(f"{i+1}: {line.strip()}")

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
            break
        except ValueError:
            print(
                "Invalid input. Please enter line numbers, ranges (e.g., 23-26), or 'all'."
            )

    for line_num in selected_lines:
        if 0 < line_num <= len(fstab_lines):
            line = fstab_lines[line_num - 1]
            match = re.match(
                r"^(?P<device>.*?)\s+(?P<mountpoint>.*?)\s+(?P<fstype>.*?)\s+(?P<options>.*?)\s+(?P<dump>.*?)\s+(?P<passno>.*?)$",
                line,
            )
            if match:
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

                unit_file = os.path.join("/etc/systemd/system", f"{unit_file_name}")

                # Use sudo to create the file in /etc/systemd/system
                try:
                    with open(unit_file, "w") as f:
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
                except PermissionError:
                    print(f"Error: Permission denied to write to {unit_file}.")
                    print("You may need to run the script with sudo.")
                    return

                # Enable and start the unit
                try:
                    # Enable the unit (with sudo)
                    subprocess.run(
                        ["sudo", "systemctl", "enable", unit_file_name], check=True
                    )
                    print(f"Enabled unit: {unit_file_name}")

                    # Start the unit (with sudo)
                    subprocess.run(
                        ["sudo", "systemctl", "start", unit_file_name], check=True
                    )
                    print(f"Started unit: {unit_file_name}")
                except subprocess.CalledProcessError as e:
                    print(f"Error enabling or starting {unit_file_name}: {e}")

                # Comment the used line in fstab
                fstab_lines[line_num - 1] = f"# {line}"

            else:
                print(
                    f"Warning: Line {line_num} in fstab does not match expected format."
                )
        else:
            print(f"Warning: Invalid line number: {line_num}")

    # Write the modified fstab back to the file with sudo
    try:
        with open(fstab_file, "w") as f:
            f.writelines(fstab_lines)
    except PermissionError:
        print(f"Error: Permission denied to write to {fstab_file}.")
        print("You may need to run the script with sudo.")
        return


if __name__ == "__main__":
    fstab_to_systemd("/etc/fstab", "fstab_mount")
