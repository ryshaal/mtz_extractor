import os
import zipfile
import shutil
import logging
import time
import threading
import sys
import random
from typing import Optional, List
from pathlib import Path
from itertools import cycle
import contextlib
from datetime import datetime


class ColorText:
    """Class untuk menangani warna text di terminal"""

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
    """Class untuk menangani animasi loading di terminal dengan efek smooth"""

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
        """Memulai animasi loading"""
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def stop(self):
        """Menghentikan animasi loading"""
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        sys.stdout.write("\r" + " " * (len(self.description) + 30) + "\r")
        sys.stdout.flush()

    def _animate(self):
        """Fungsi internal untuk menjalankan animasi dengan efek smooth"""
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
    """Context manager untuk animasi loading"""
    spinner = LoadingAnimation(description)
    spinner.start()
    try:
        yield spinner
    finally:
        spinner.stop()


class MTZCompressor:
    """Class untuk menangani kompresi file MTZ"""

    def __init__(self):
        self.setup_logging()
        self.stats = {
            "start_time": None,
            "total_files": 0,
            "total_size": 0,
            "compressed_size": 0,
        }

    def setup_logging(self) -> None:
        log_folder = Path("logs")
        log_folder.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_folder / f"compression_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, mode="w"),
            ],
        )

    def print_banner(self):
        """Menampilkan banner aplikasi"""
        banner = f"""
{ColorText.cyan('╔═════════════════════════════════════════╗')}
{ColorText.cyan('║')}          {ColorText.bold(' MTZ Packing v2.0   ')}           {ColorText.cyan('║')}
{ColorText.cyan('║')}      {ColorText.yellow('       BY Ryhshall           ')}      {ColorText.cyan('║')}
{ColorText.cyan('╚═════════════════════════════════════════╝')}
"""
        print(banner)

    def validate_folder(self, folder_path: str) -> bool:
        if not os.path.exists(folder_path):
            print(f"\n{ColorText.red('❌ Folder tidak ditemukan!')}")
            return False

        if not os.path.isdir(folder_path):
            print(f"\n{ColorText.red('❌ Path bukan folder!')}")
            return False

        return True

    def calculate_size(self, path: str) -> int:
        """Menghitung ukuran folder/file"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total

    def format_size(self, size: int) -> str:
        """Format ukuran file dalam bentuk yang mudah dibaca"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def zip_folder(self, folder_path: str) -> Optional[str]:
        try:
            folder_size = self.calculate_size(folder_path)
            with loading_animation(
                f"Mengompres {ColorText.yellow(os.path.basename(folder_path))} ({self.format_size(folder_size)})"
            ):
                zip_path = f"{folder_path}.zip"
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zipf:
                    for root, dirs, files in os.walk(folder_path):
                        if os.path.basename(root) in ["wallpaper", "preview"]:
                            continue

                        if not files and not dirs:
                            arcname = os.path.relpath(root, folder_path) + "/"
                            zipf.write(root, arcname)
                        else:
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, folder_path)
                                zipf.write(file_path, arcname)
                                self.stats["total_files"] += 1
                                self.stats["total_size"] += os.path.getsize(file_path)

            return zip_path
        except Exception as e:
            logging.error(f"Error compressing folder: {str(e)}")
            return None

    def verify_zip(self, zip_path: str) -> bool:
        with loading_animation(
            f"Memverifikasi {ColorText.yellow(os.path.basename(zip_path))}"
        ):
            try:
                with zipfile.ZipFile(zip_path, "r") as zipf:
                    corrupt_file = zipf.testzip()
                    if corrupt_file is not None:
                        logging.error(f"File corrupt: {corrupt_file}")
                        return False
                    return True
            except Exception as e:
                logging.error(f"Error verifying ZIP: {str(e)}")
                return False

    def remove_zip_extension(self, folder_path: str) -> None:
        with loading_animation(
            f"Menghapus ekstensi ZIP dari {ColorText.yellow(os.path.basename(folder_path))}"
        ):
            try:
                folder_path = os.path.abspath(folder_path)
                for filename in os.listdir(folder_path):
                    if filename.endswith(".zip"):
                        old_path = os.path.join(folder_path, filename)
                        new_path = os.path.join(folder_path, filename[:-4])
                        os.rename(old_path, new_path)
                        logging.info(f"Renamed: {old_path} to {new_path}")
            except Exception as e:
                logging.error(f"Error removing ZIP extensions: {str(e)}")

    def create_mtz(self, folder_path: str) -> bool:
        with loading_animation(f"Membuat file {ColorText.yellow('MTZ')}"):
            try:
                folder_path = os.path.abspath(folder_path)
                mtz_path = folder_path + ".mtz"

                with zipfile.ZipFile(mtz_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, folder_path)
                            zf.write(full_path, rel_path)
                            logging.info(f"Added to MTZ: {rel_path}")

                if os.path.exists(mtz_path):
                    self.stats["compressed_size"] = os.path.getsize(mtz_path)
                    shutil.rmtree(folder_path)
                    return True
                return False
            except Exception as e:
                logging.error(f"Error creating MTZ: {str(e)}")
                return False

    def show_completion(self, folder_path: str):
        """Menampilkan pesan selesai dengan statistik"""
        os.system("cls" if os.name == "nt" else "clear")
        mtz_path = folder_path + ".mtz"

        completion_time = time.time() - self.stats["start_time"]
        compression_ratio = (
            (self.stats["compressed_size"] / self.stats["total_size"]) * 100
            if self.stats["total_size"] > 0
            else 0
        )

        print(f"\n{ColorText.green('✨ Packing Berhasil! ✨')}")
        print(f"\n{ColorText.cyan('📊 Statistik Packing:')}")
        print(f"├─ Total file: {ColorText.yellow(str(self.stats['total_files']))}")
        print(
            f"├─ Ukuran awal: {ColorText.yellow(self.format_size(self.stats['total_size']))}"
        )
        print(
            f"├─ Ukuran akhir: {ColorText.yellow(self.format_size(self.stats['compressed_size']))}"
        )
        print(f"├─ Rasio kompresi: {ColorText.yellow(f'{compression_ratio:.1f}%')}")
        print(f"├─ Waktu proses: {ColorText.yellow(f'{completion_time:.1f} detik')}")
        print(f"└─ File MTZ: {ColorText.yellow(mtz_path)}\n")


def get_user_input() -> str:
    """Fungsi untuk mendapatkan input dari user"""
    return input(
        f"{ColorText.cyan('📂')} Masukkan alamat folder yang akan dipacking: "
    ).strip()


def main():
    """Fungsi utama"""
    os.system("cls" if os.name == "nt" else "clear")
    compressor = MTZCompressor()
    compressor.print_banner()

    try:
        main_folder = get_user_input()

        if not compressor.validate_folder(main_folder):
            sys.exit(1)

        print(f"\n{ColorText.cyan('🔄')} Memulai proses kompresi...\n")
        compressor.stats["start_time"] = time.time()

        # Step 1: Kompresi folder ke ZIP
        for folder in os.listdir(main_folder):
            folder_path = os.path.join(main_folder, folder)

            if folder in ["wallpaper", "preview"]:
                logging.info(f"Mengabaikan folder: {folder}")
                continue

            if os.path.isdir(folder_path):
                zip_path = compressor.zip_folder(folder_path)
                if zip_path and compressor.verify_zip(zip_path):
                    shutil.rmtree(folder_path)
                    print(f"{ColorText.green('✓')} {folder}")
                    logging.info(f"Folder berhasil dikompres: {folder}")

        # Step 2: Hapus ekstensi ZIP
        compressor.remove_zip_extension(main_folder)

        # Step 3: Buat file MTZ
        if compressor.create_mtz(main_folder):
            compressor.show_completion(main_folder)
        else:
            print(f"\n{ColorText.red('❌ Gagal membuat file MTZ!')}\n")
            sys.exit(1)

    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"\n{ColorText.yellow('⚠️ Dibatalkan!')}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{ColorText.red('❌ Error:')} {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
