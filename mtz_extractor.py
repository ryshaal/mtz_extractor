import os
import sys
import zipfile
import shutil
import logging
import time
import threading
from typing import Set, Optional
from pathlib import Path
from itertools import cycle
import contextlib


class LoadingAnimation:
    """Class untuk menangani animasi loading di terminal"""

    def __init__(self, description: str = "Processing"):
        self.description = description
        self.is_running = False
        self.animation_thread = None
        self.animations = {
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "line": ["-", "\\", "|", "/"],
            "arrow": ["←", "↖", "↑", "↗", "→", "↘", "↓", "↙"],
            "pulse": [
                "█▁▁▁▁▁▁▁",
                "██▁▁▁▁▁▁",
                "███▁▁▁▁▁",
                "████▁▁▁▁",
                "█████▁▁▁",
                "██████▁▁",
                "███████▁",
                "████████",
            ],
        }
        self.animation_chars = self.animations["dots"]

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
        sys.stdout.write("\r" + " " * (len(self.description) + 20) + "\r")
        sys.stdout.flush()

    def _animate(self):
        """Fungsi internal untuk menjalankan animasi"""
        for char in cycle(self.animation_chars):
            if not self.is_running:
                break
            sys.stdout.write(f"\r{char} {self.description}")
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


class MTZExtractor:
    """Class untuk menangani ekstraksi file MTZ"""

    def __init__(self, allowed_extensions: Set[str] = None):
        self.allowed_extensions = allowed_extensions or {
            ".java", ".kt", ".so", ".aar", ".jar", ".mp3", ".wav",
            ".mp4", ".3gp", ".txt", ".json", ".xml", ".html", ".css",
            ".js", ".ttf", ".otf", ".png", ".jpg", ".jpeg", ".gif",
            ".webp", ".pdf", ".gradle", ".properties", ".MF", ".SF",
            ".RSA",
        }
        self.setup_logging()

    def setup_logging(self) -> None:
        """Mengatur logging ke file log"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("mtz_extractor.log", mode="w"),
            ],
        )
        logging.info("MTZ Extractor initialized")

    def validate_mtz_file(self, file_path: str) -> bool:
        """Validasi apakah file adalah MTZ"""
        if not os.path.exists(file_path):
            logging.error("File tidak ditemukan!")
            print("\n❌ File tidak ditemukan!")
            return False

        if not file_path.endswith(".mtz"):
            logging.error("File bukan format MTZ!")
            print("\n❌ File bukan format MTZ!")
            return False

        logging.info("File validasi berhasil: %s", file_path)
        return True

    def create_extract_folder(self, file_path: str) -> Optional[str]:
        """Membuat folder ekstraksi yang unik"""
        try:
            file_name = Path(file_path).stem
            base_extract_folder = Path("./extracted")
            extract_folder = base_extract_folder / file_name

            counter = 1
            while extract_folder.exists():
                extract_folder = base_extract_folder / f"{file_name}_copy{counter}"
                counter += 1

            extract_folder.mkdir(parents=True, exist_ok=True)
            logging.info("Folder ekstraksi dibuat: %s", extract_folder)
            return str(extract_folder)

        except Exception as e:
            logging.error("Gagal membuat folder ekstraksi: %s", str(e))
            print(f"\n❌ Gagal membuat folder: {str(e)}")
            return None

    def extract_mtz(self, file_path: str, extract_folder: str) -> bool:
        """Ekstraksi file MTZ ke folder"""
        try:
            with loading_animation("Mengekstrak"):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(extract_folder)
            logging.info("File berhasil diekstrak ke %s", extract_folder)
            return True
        except Exception as e:
            logging.error("Gagal ekstrak: %s", str(e))
            print(f"\n❌ Gagal ekstrak: {str(e)}")
            return False

    def process_files(self, folder: str) -> None:
        """Proses file setelah diekstrak"""
        with loading_animation("Memproses"):
            self._add_zip_extension_to_files(folder)
            self._unzip_files_to_folders(folder)
            self._cleanup_empty_folders(folder)

    def _add_zip_extension_to_files(self, folder: str) -> None:
        """Tambahkan ekstensi .zip pada file yang bukan ekstensi yang diizinkan"""
        try:
            for file_path in Path(folder).rglob("*"):
                if file_path.is_file() and file_path.suffix not in self.allowed_extensions:
                    new_path = file_path.with_suffix(file_path.suffix + ".zip")
                    file_path.rename(new_path)
                    logging.info("Ditambahkan ekstensi .zip: %s", new_path)
        except Exception as e:
            logging.error("Error menambahkan ekstensi .zip: %s", str(e))

    def _unzip_files_to_folders(self, folder: str) -> None:
        """Ekstraksi file .zip ke folder masing-masing"""
        try:
            for file_path in Path(folder).rglob("*.zip"):
                if file_path.is_file():
                    folder_path = file_path.with_suffix("")
                    folder_path.mkdir(exist_ok=True)

                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(folder_path)
                    logging.info("File .zip diekstrak: %s", folder_path)

                    file_path.unlink()  # Hapus file .zip setelah diekstrak
        except Exception as e:
            logging.error("Error mengekstrak file .zip: %s", str(e))

    def _cleanup_empty_folders(self, folder: str) -> None:
        """Hapus folder kosong"""
        try:
            for dir_path in Path(folder).rglob("*"):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logging.info("Folder kosong dihapus: %s", dir_path)
        except Exception as e:
            logging.error("Error menghapus folder kosong: %s", str(e))

    def show_completion(self, extract_folder: str):
        """Menampilkan pesan selesai"""
        os.system("cls" if os.name == "nt" else "clear")
        print("\n✨ Ekstraksi Berhasil! ✨")
        print(f"📁 Tersimpan di: {extract_folder}\n")
        logging.info("Ekstraksi selesai. Tersimpan di %s", extract_folder)


def get_user_input() -> str:
    """Fungsi untuk mendapatkan input dari user"""
    return input("Masukan lokasi file .mtz: ").strip()


def main():
    """Fungsi utama"""
    os.system("cls" if os.name == "nt" else "clear")
    print("🗂️  MTZ Extractor by Ryshall\n")

    extractor = MTZExtractor()

    try:
        file_path = get_user_input()

        if not extractor.validate_mtz_file(file_path):
            sys.exit(1)

        extract_folder = extractor.create_extract_folder(file_path)
        if not extract_folder:
            sys.exit(1)

        if not extractor.extract_mtz(file_path, extract_folder):
            sys.exit(1)

        extractor.process_files(extract_folder)
        extractor.show_completion(extract_folder)

    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print("\n⚠️ Dibatalkan!\n")
        logging.info("Proses dibatalkan oleh user.")
        sys.exit(0)
    except Exception as e:
        logging.error("Error: %s", str(e))
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
