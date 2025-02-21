# Cursor Pwn 0.1.0

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey)

A utility tool designed to modify device identification parameters for Cursor IDE, helping to manage and refresh device identifiers to bypass Cursor's free trial limit.

![trial](https://github.com/user-attachments/assets/f8ba5322-2933-4cc4-89e2-5c7c6662b912)

![cursor-pwn](https://github.com/user-attachments/assets/f8f61f24-1438-4029-959a-d16d16121a8d)

## Features

-   🔄 Generates new device identifiers
-   💾 Automatically backs up existing configurations
-   🛡️ Option to disable auto-updates
-   🔒 Requires administrator privileges for registry modifications
-   📊 Detailed logging and status reporting
-   🎨 Colorful CLI interface
-   ⚡ Automatic process management

## Requirements

-   Windows 10 or 11
-   Python 3.6 or higher
-   Administrator privileges
-   Cursor IDE v0.45.x or lower installed

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/cursor-device-modifier.git
cd cursor-device-modifier
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Log out of Cursor account in the IDE.
2. Run the script as Administrator:

```bash
python pwn.py
```

3. Follow the on-screen prompts
4. Restart Cursor IDE after completion

## What It Does

The tool performs the following operations:

1. Detects current Cursor version
2. Creates backups of existing configurations
3. Generates new device identifiers:
    - Machine GUID
    - SQM ID
    - Machine ID
    - Device ID
4. Updates storage configuration
5. Optionally disables auto-updates

## File Structure

```
📁 Your Cursor Directory
├── 📄 storage.json (modified)
└── 📁 backups
    └── 📄 storage.json.backup_YYYYMMDD_HHMMSS
```

## Compatibility

-   ✅ Windows 10
-   ✅ Windows 11
-   ❌ macOS
-   ❌ Linux

## Warning

This tool modifies system settings and device identifiers. Use at your own risk. Always ensure you have backups before running the tool.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring they comply with all relevant terms of service and licensing agreements.
