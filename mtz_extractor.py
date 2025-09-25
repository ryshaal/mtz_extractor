import os
import sys
import zipfile
import shutil
import logging
import time
import platform
import psutil 
import threading
import random
from typing import Set, Optional
from pathlib import Path
from itertools import cycle
import contextlib
from datetime import datetime


class ColorText:
    """Class for handling text colors in terminal"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def blue(text: str) -> str:
        return f"{ColorText.BLUE}{text}{ColorText.END}"

    @staticmethod
    def green(text: str) -> str:
        return f"{ColorText.GREEN}{text}{ColorText.END}"

    @staticmethod
    def red(text: str) -> str:
        return f"{ColorText.RED}{text}{ColorText.END}"

    @staticmethod
    def yellow(text: str) -> str:
        return f"{ColorText.YELLOW}{text}{ColorText.END}"

    @staticmethod
    def cyan(text: str) -> str:
        return f"{ColorText.CYAN}{text}{ColorText.END}"

    @staticmethod
    def bold(text: str) -> str:
        return f"{ColorText.BOLD}{text}{ColorText.END}"


class LoadingAnimation:
    """Class for handling loading animations in terminal with smooth effects"""

    def __init__(self, description: str = "Processing"):
        self.description = description
        self.is_running = False
        self.animation_thread = None
        self.progress = 0
        self.animations = {
            "smooth_bar": [
                "▰▱▱▱▱▱▱▱▱▱",
                "▰▰▱▱▱▱▱▱▱▱",
                "▰▰▰▱▱▱▱▱▱▱",
                "▰▰▰▰▱▱▱▱▱▱",
                "▰▰▰▰▰▱▱▱▱▱",
                "▰▰▰▰▰▰▱▱▱▱",
                "▰▰▰▰▰▰▰▱▱▱",
                "▰▰▰▰▰▰▰▰▱▱",
                "▰▰▰▰▰▰▰▰▰▱",
                "▰▰▰▰▰▰▰▰▰▰",
            ],
            "wave": ["≋", "≈", "≋", "≈", "≋"],
            "spinner": ["◜", "◠", "◝", "◞", "◡", "◟"],
            "pulse": ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
        }
        self.colors = [
            ColorText.BLUE,
            ColorText.CYAN,
            ColorText.GREEN,
            ColorText.YELLOW,
        ]
        self.current_color = random.choice(self.colors)
        self.animation_chars = self.animations["smooth_bar"]

    def start(self):
        """Start loading animation"""
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def stop(self):
        """Stop loading animation"""
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        sys.stdout.write("\r" + " " * (len(self.description) + 30) + "\r")
        sys.stdout.flush()

    def _animate(self):
        """Internal function to run animation with smooth effects"""
        while self.is_running:
            for frame in self.animation_chars:
                if not self.is_running:
                    break
                animation = f"{self.current_color}{frame}{ColorText.END}"
                sys.stdout.write(f"\r{animation} {self.description} ")
                sys.stdout.flush()
                time.sleep(0.1)


@contextlib.contextmanager
def loading_animation(description: str = "Processing"):
    """Context manager for loading animation"""
    spinner = LoadingAnimation(description)
    spinner.start()
    try:
        yield spinner
    finally:
        spinner.stop()


class MTZExtractor:
    """Class for handling MTZ file extraction"""

    def __init__(self, allowed_extensions: Set[str] = None):
        self.allowed_extensions = allowed_extensions or {
            ".java", ".kt", ".so", ".aar", ".jar", ".mp3", ".wav",
            ".mp4", ".3gp", ".txt", ".json", ".xml", ".html", ".css",
            ".js", ".ttf", ".otf", ".png", ".jpg", ".jpeg", ".gif",
            ".webp", ".pdf", ".gradle", ".properties", ".MF", ".SF",
            ".RSA",
        }
        self.setup_logging()
        self.stats = {
            "start_time": None,
            "total_files": 0,
            "total_size": 0,
            "extracted_size": 0,
        }

    def setup_logging(self) -> None:
        """Set up logging to log file"""
        log_folder = Path("logs")
        log_folder.mkdir(exist_ok=True)
        
        """Set up to display system info and logging"""
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        """Get memory information"""
        memory_info = psutil.virtual_memory()

        """Get date data and set location to save log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_folder / f"compression_{timestamp}.log"
        
        """Determine extract_folder based on Python file execution location"""
        extract_folder = os.path.dirname(os.path.abspath(__file__))  
        """Use __file__ if inside script"""
        """If in interactive environment, use os.getcwd()"""
        """extract_folder = os.getcwd()"""
        

        self.logger = logging.getLogger(f'MTZExtractor_{timestamp}')
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        """Add handler to logger"""
        self.logger.addHandler(file_handler)
        
        """Ensure log doesn't duplicate to root logger"""
        self.logger.propagate = False

        """Fill log file"""
        self.logger.info("MTZ Extractor initialized")
        self.logger.info(f"System Info: {platform.system()} {platform.release()}")
        self.logger.info(f"CPU Architecture: {platform.machine()}")
        self.logger.info(f"Process ID: {os.getpid()}")
        self.logger.info(f"Memory Info: Total={memory_info.total / (1024 ** 3):.2f} GB, "
            f"Used={memory_info.used / (1024 ** 3):.2f} GB, "
            f"Available={memory_info.available / (1024 ** 3):.2f} GB, "
            f"Percentage={memory_info.percent}%")
        self.logger.info(f"Python Version: {platform.python_version()}")
        self.logger.info("Timestamp: %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.logger.info(f"Log file created at: {log_file}")
        self.logger.info(f"Extracted: {extract_folder}")


    def print_banner(self):
        """Display application banner"""
        banner = f"""
{ColorText.cyan('╔═════════════════════════════════════════╗')}
{ColorText.cyan('║')}        {ColorText.bold(' MTZ Extractor v2.0   ')}           {ColorText.cyan('║')}
{ColorText.cyan('║')}      {ColorText.yellow('       BY Ryhshall           ')}      {ColorText.cyan('║')}
{ColorText.cyan('╚═════════════════════════════════════════╝')}
"""
        print(banner)

    def format_size(self, size: int) -> str:
        """Format file size in readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def validate_mtz_file(self, file_path: str) -> bool:
        """Validate if file is MTZ"""
        if not os.path.exists(file_path):
            print(f"\n{ColorText.red('❌ File not found!')}")
            return False

        if not file_path.endswith(".mtz"):
            print(f"\n{ColorText.red('❌ File is not MTZ format!')}")
            return False

        return True

    def create_extract_folder(self, file_path: str) -> Optional[str]:
        """Create unique extraction folder"""
        try:
            file_name = Path(file_path).stem
            base_extract_folder = Path("./extracted")
            extract_folder = base_extract_folder / file_name

            counter = 1
            while extract_folder.exists():
                extract_folder = base_extract_folder / f"{file_name}_copy{counter}"
                counter += 1

            extract_folder.mkdir(parents=True, exist_ok=True)
            return str(extract_folder)

        except Exception as e:
            print(f"\n{ColorText.red(f'❌ Failed to create folder: {str(e)}')}")
            return None

    def extract_mtz(self, file_path: str, extract_folder: str) -> bool:
        """Extract MTZ file to folder"""
        try:
            self.stats["start_time"] = time.time()
            self.stats["total_size"] = os.path.getsize(file_path)

            with loading_animation(
                f"Extracting {ColorText.yellow(os.path.basename(file_path))} ({self.format_size(self.stats['total_size'])})"
            ):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(extract_folder)
                    self.stats["total_files"] = len(zip_ref.namelist())
            return True
        except Exception as e:
            print(f"\n{ColorText.red(f'❌ Extraction failed: {str(e)}')}")
            return False

    def process_files(self, folder: str) -> None:
        """Process files after extraction"""
        with loading_animation(f"Processing {ColorText.yellow(os.path.basename(folder))}"):
            self._add_zip_extension_to_files(folder)
            self._unzip_files_to_folders(folder)
            self._cleanup_empty_folders(folder)
            self.stats["extracted_size"] = self.calculate_folder_size(folder)

    def calculate_folder_size(self, folder: str) -> int:
        """Calculate total folder size"""
        total_size = 0
        for dirpath, _, filenames in os.walk(folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def _add_zip_extension_to_files(self, folder: str) -> None:
        """Add .zip extension to files that are not allowed extensions"""
        for file_path in Path(folder).rglob("*"):
            if file_path.is_file() and file_path.suffix not in self.allowed_extensions:
                new_path = file_path.with_suffix(file_path.suffix + ".zip")
                file_path.rename(new_path)

    def _unzip_files_to_folders(self, folder: str) -> None:
        """Extract .zip files to their respective folders"""
        for file_path in Path(folder).rglob("*.zip"):
            if file_path.is_file():
                folder_path = file_path.with_suffix("")
                folder_path.mkdir(exist_ok=True)

                try:
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(folder_path)
                    file_path.unlink()
                except Exception:
                    continue

    def _cleanup_empty_folders(self, folder: str) -> None:
        """Remove empty folders"""
        for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
            if not dirnames and not filenames:
                try:
                    os.rmdir(dirpath)
                except OSError:
                    continue

    def show_completion(self, extract_folder: str):
        """Display completion message with statistics"""
        os.system("cls" if os.name == "nt" else "clear")
        completion_time = time.time() - self.stats["start_time"]
        expansion_ratio = (
            (self.stats["extracted_size"] / self.stats["total_size"]) * 100
            if self.stats["total_size"] > 0
            else 0
        )

        print(f"\n{ColorText.green('✨ Extraction Successful! ✨')}")
        print(f"\n{ColorText.cyan('📊 Extraction Statistics:')}")
        print(f"├─ Total files: {ColorText.yellow(str(self.stats['total_files']))}")
        print(
            f"├─ Original size: {ColorText.yellow(self.format_size(self.stats['total_size']))}"
        )
        print(
            f"├─ Final size: {ColorText.yellow(self.format_size(self.stats['extracted_size']))}"
        )
        print(f"├─ Expansion ratio: {ColorText.yellow(f'{expansion_ratio:.1f}%')}")
        print(f"├─ Processing time: {ColorText.yellow(f'{completion_time:.1f} seconds')}")
        print(f"└─ Location: {ColorText.yellow(extract_folder)}\n")


def get_user_input() -> str:
    """Function to get input from user"""
    return input(
        f"{ColorText.cyan('📂')} Enter MTZ file location: "
    ).strip()


def main():
    """Main function"""
    os.system("cls" if os.name == "nt" else "clear")
    extractor = MTZExtractor()
    extractor.print_banner()

    try:
        file_path = get_user_input()

        if not extractor.validate_mtz_file(file_path):
            sys.exit(1)

        extract_folder = extractor.create_extract_folder(file_path)
        if not extract_folder:
            sys.exit(1)

        print(f"\n{ColorText.cyan('⏳')} Starting extraction process...\n")

        if not extractor.extract_mtz(file_path, extract_folder):
            sys.exit(1)

        extractor.process_files(extract_folder)
        extractor.show_completion(extract_folder)

    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"\n{ColorText.yellow('⚠️ Cancelled!')}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{ColorText.red('❌ Error:')} {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()