
# MTZ Extractor

This Python script, named `mtz_extractor.py`, is designed to extract `.mtz` files. It provides functionality to open, read, and process `.mtz` file formats.
This repository contains a Python script for extracting .mtz files, specifically designed for Xiaomi MIUI themes. The script enables easy access to the contents of .mtz theme files, making it convenient for customization and theme modification. Terminal commands use Indonesian.

## Features

- Extracts files from `.mtz` archives.
- Provides a straightforward interface to handle `.mtz` files.
- Easily modifiable to include additional processing steps.

## Requirements

This script requires Python 3.x to run. Ensure you have the necessary Python version installed on your system.

## Install Dependencies

Proyek ini menggunakan modul-modul built-in Python, namun ada satu modul tambahan `psutil` yang perlu diinstal. Jalankan perintah berikut untuk menginstal dependensi:

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
