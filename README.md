
# MTZ Extractor - Xiaomi MIUI Themes Extractor

This repository contains a Python script for extracting `.mtz` files, specifically designed for Xiaomi MIUI themes.  
The script allows easy access to the contents of `.mtz` theme files, making theme customization and modification much simpler.

In addition, a desktop application version is also available — a Python-based app for extracting, compressing, and managing MIUI theme files (`.mtz`).  
It is built using **CustomTkinter**, featuring a modern graphical interface with **drag-and-drop** support.

[![Download](https://img.shields.io/badge/Download%20MTZ_Extractor-v2.0-blue?style=for-the-badge&logo=windows)](https://github.com/ryshaal/mtz_extractor/releases/download/v2.0/MTZ_Extractor.exe)

<a href='https://ko-fi.com/riyhsal/5' target='_blank'><img height='40' style='border:0px;height:40px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>


## Features

- Extracts files from `.mtz` archives.
- Provides a straightforward interface to handle `.mtz` files.
- Easily modifiable to include additional processing steps.

## Requirements

This script requires Python 3.x to run. Ensure you have the necessary Python version installed on your system.

## Install Dependencies

This project uses Python's built-in modules, but there is one additional `psutil` module that needs to be installed. Run the following command to install dependencies:

```bash
pip install psutil
```

## Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ryshaal/mtz_extractor.git
   cd mtz_extractor
   ```

2. **Run the script:**
   ```bash
   python mtz_extractor.py <file_path>
   ```

   Replace `<file_path>` with the path to the `.mtz` file you want to extract.

## Example

```bash
python mtz_extractor.py example.mtz
```

This command will extract `example.mtz` and display the contents as per the script's implementation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For more details and updates, visit [GitHub Repository](https://github.com/ryshaal).
