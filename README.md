# FSTAB to Systemd Unit Conversion Script

This Python script helps automate the process of converting specific entries from an `/etc/fstab` file into systemd mount unit files. These unit files are used to mount devices and network shares via systemd on Linux systems.

## Features

- Convert selected lines from `/etc/fstab` to systemd unit files.
- Automatically create unit files with appropriate configurations based on the fstab entry.
- Supports enabling and starting systemd units after they are created.
- Provides an interactive interface to select which entries to convert.
- Amends the fstab file to comment out the converted lines.

## Prerequisites

- Python 3.x
- `systemd-escape` command (part of the systemd package)
- Access to `sudo` for creating systemd unit files and modifying `/etc/fstab`.

## Installation

1. Clone the repository or download the script file:

   ```bash
   git clone https://github.com/acelaya77/fstab-2-systemd.git
   cd fstab-2-systemd
   ```

2. (Optional) Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install any required Python packages (if applicable):

   ```bash
    pip install -r requirements.txt
   ```

## Usage

1. **Run the script** with your desired fstab file:

   ```bash
    python3 fstab_to_systemd.py /etc/fstab
   ```

2. **Interactive Input**:

   - The script will display all the entries in your `/etc/fstab` file.
   - You can select specific lines by entering line numbers or ranges, or type `all` to select everything.

3. The script will:

   - Create systemd unit files for the selected fstab entries.
   - Automatically enable and start the corresponding units.
   - Comment out the used entries in `/etc/fstab` to prevent re-conversion.

4. **Important Notes**:
   - You must have `sudo` privileges to create systemd unit files and modify `/etc/fstab`.
   - The script assumes the `/etc/fstab` file is formatted correctly and contains mountable entries.

## Example Output

Upon running the script, the following will happen:

```bash
Found the following entries in fstab:
1: /dev/sda1 /mnt/data ext4 defaults 0 0
2: 192.168.1.100:/mnt/nfs /mnt/nfs nfs defaults 0 0

Enter line numbers or ranges to convert (comma-separated, or 'all'): 1
Created unit file: /etc/systemd/system/mnt-data.mount
Enabled unit: mnt-data.mount
Started unit: mnt-data.mount
```

In the example above:

- The script lists all entries in the `fstab` file.
- The user selects line `1` for conversion.
- A systemd unit file (`mnt-data.mount`) is created, enabled, and started.

## Troubleshooting

- **Permission Errors**: If you encounter permission errors (e.g., `Permission denied`), make sure you have the necessary `sudo` privileges to create systemd unit files and modify `/etc/fstab`. You might need to run the script as an elevated user:

  ```bash
  sudo python3 fstab_to_systemd.py /etc/fstab
  ```

- **No such file or directory**: Ensure that the fstab file and mount points are correct and exist in the system.

- **Missing Dependencies**: If the `systemd-escape` command is not found, you may need to install systemd or update your system. On most Linux distributions, you can install systemd using:

  ```bash
  sudo apt-get install systemd
  ```

- **Rewriting History in `/etc/fstab`**: When using this script, the original entries in `/etc/fstab` will be commented out to avoid future issues with duplicate entries. If you need to restore the original fstab, simply uncomment the lines in the `/etc/fstab` file.

## License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/licenses/MIT) file for details.

## Acknowledgements

- This project uses systemd for managing mounts and mounts from `/etc/fstab`.
- Special thanks to the open-source community for maintaining and improving systemd.
- Thanks to contributors and testers who provided valuable feedback.
