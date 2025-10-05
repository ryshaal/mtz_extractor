import os
import sys
import zipfile
import shutil
import logging
import time
import platform
import psutil
import threading
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from typing import Set, Optional
from pathlib import Path
from datetime import datetime


class MTZExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MTZ Extractor v2.0")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Colors
        self.bg_color = "#1a1a2e"
        self.secondary_bg = "#16213e"
        self.accent_color = "#0f3460"
        self.highlight_color = "#00d4ff"
        self.text_color = "#eaeaea"
        self.success_color = "#00ff88"
        self.error_color = "#ff4757"
        
        self.root.configure(bg=self.bg_color)
        
        # Initialize extractor
        self.extractor = MTZExtractor()
        self.selected_file = None
        self.is_processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg=self.secondary_bg, height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="MTZ EXTRACTOR",
            font=("Segoe UI", 28, "bold"),
            bg=self.secondary_bg,
            fg=self.highlight_color
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="BY RYHSHALL",
            font=("Segoe UI", 10),
            bg=self.secondary_bg,
            fg=self.text_color
        )
        subtitle_label.pack()
        
        # Main Content Frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # File Selection Section
        file_frame = tk.Frame(content_frame, bg=self.accent_color, relief=tk.FLAT)
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_label = tk.Label(
            file_frame,
            text="📂 Select MTZ File",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg=self.text_color
        )
        file_label.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        # File path display
        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = tk.Label(
            file_frame,
            textvariable=self.file_path_var,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg="#aaaaaa",
            anchor=tk.W,
            wraplength=700
        )
        file_path_label.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Buttons Frame
        button_frame = tk.Frame(file_frame, bg=self.accent_color)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.browse_btn = tk.Button(
            button_frame,
            text="Browse File",
            command=self.browse_file,
            font=("Segoe UI", 10, "bold"),
            bg=self.highlight_color,
            fg=self.bg_color,
            activebackground="#00b8d4",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.extract_btn = tk.Button(
            button_frame,
            text="Extract MTZ",
            command=self.start_extraction,
            font=("Segoe UI", 10, "bold"),
            bg=self.success_color,
            fg=self.bg_color,
            activebackground="#00e676",
            activeforeground=self.bg_color,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.extract_btn.pack(side=tk.LEFT)
        
        # Progress Section
        progress_frame = tk.Frame(content_frame, bg=self.accent_color, relief=tk.FLAT)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        progress_label = tk.Label(
            progress_frame,
            text="⏳ Progress",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg=self.text_color
        )
        progress_label.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=self.secondary_bg,
            background=self.highlight_color,
            darkcolor=self.highlight_color,
            lightcolor=self.highlight_color,
            bordercolor=self.accent_color,
            thickness=25
        )
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style="Custom.Horizontal.TProgressbar",
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to extract")
        status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg=self.text_color
        )
        status_label.pack(anchor=tk.W, padx=15, pady=(0, 15))
        
        # Log Section
        log_frame = tk.Frame(content_frame, bg=self.accent_color, relief=tk.FLAT)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_label = tk.Label(
            log_frame,
            text="📋 Extraction Log",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg=self.text_color
        )
        log_label.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg=self.secondary_bg,
            fg=self.text_color,
            relief=tk.FLAT,
            height=10,
            wrap=tk.WORD,
            insertbackground=self.highlight_color
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.log_text.insert(tk.END, "Welcome to MTZ Extractor v2.0\n")
        self.log_text.insert(tk.END, f"System: {platform.system()} {platform.release()}\n")
        self.log_text.insert(tk.END, f"Ready to extract MTZ files...\n\n")
        self.log_text.config(state=tk.DISABLED)
    
    def log_message(self, message, level="INFO"):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "SUCCESS":
            prefix = "✓"
        elif level == "ERROR":
            prefix = "✗"
        elif level == "WARNING":
            prefix = "⚠"
        else:
            prefix = "•"
            
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MTZ File",
            filetypes=[("MTZ Files", "*.mtz"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path_var.set(file_path)
            self.extract_btn.config(state=tk.NORMAL)
            self.log_message(f"File selected: {os.path.basename(file_path)}")
    
    def start_extraction(self):
        if not self.selected_file or self.is_processing:
            return
        
        self.is_processing = True
        self.extract_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)
        
        # Run extraction in separate thread
        thread = threading.Thread(target=self.extract_process)
        thread.daemon = True
        thread.start()
    
    def extract_process(self):
        try:
            # Validate file
            self.status_var.set("Validating file...")
            self.progress_var.set(10)
            
            if not self.extractor.validate_mtz_file(self.selected_file):
                self.log_message("Invalid MTZ file!", "ERROR")
                self.reset_ui()
                return
            
            self.log_message("File validation successful", "SUCCESS")
            
            # Create extract folder
            self.status_var.set("Creating extraction folder...")
            self.progress_var.set(20)
            
            extract_folder = self.extractor.create_extract_folder(self.selected_file)
            if not extract_folder:
                self.log_message("Failed to create extraction folder!", "ERROR")
                self.reset_ui()
                return
            
            self.log_message(f"Extraction folder: {extract_folder}", "SUCCESS")
            
            # Extract MTZ
            self.status_var.set("Extracting MTZ file...")
            self.progress_var.set(40)
            self.log_message("Starting extraction process...")
            
            if not self.extractor.extract_mtz(self.selected_file, extract_folder):
                self.log_message("Extraction failed!", "ERROR")
                self.reset_ui()
                return
            
            self.log_message(f"Extracted {self.extractor.stats['total_files']} files", "SUCCESS")
            self.progress_var.set(70)
            
            # Process files
            self.status_var.set("Processing extracted files...")
            self.log_message("Processing files...")
            
            self.extractor.process_files(extract_folder)
            self.progress_var.set(90)
            
            # Complete
            self.status_var.set("Extraction completed!")
            self.progress_var.set(100)
            
            # Show statistics
            completion_time = time.time() - self.extractor.stats["start_time"]
            self.log_message("=" * 50, "INFO")
            self.log_message("EXTRACTION COMPLETED!", "SUCCESS")
            self.log_message(f"Total files: {self.extractor.stats['total_files']}")
            self.log_message(f"Original size: {self.extractor.format_size(self.extractor.stats['total_size'])}")
            self.log_message(f"Final size: {self.extractor.format_size(self.extractor.stats['extracted_size'])}")
            self.log_message(f"Processing time: {completion_time:.1f} seconds")
            self.log_message(f"Location: {extract_folder}")
            self.log_message("=" * 50, "INFO")
            
            # Open folder
            if platform.system() == "Windows":
                os.startfile(extract_folder)
            elif platform.system() == "Darwin":
                os.system(f"open '{extract_folder}'")
            else:
                os.system(f"xdg-open '{extract_folder}'")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}", "ERROR")
        finally:
            self.reset_ui()
    
    def reset_ui(self):
        self.is_processing = False
        self.extract_btn.config(state=tk.NORMAL if self.selected_file else tk.DISABLED)
        self.browse_btn.config(state=tk.NORMAL)


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
        self.stats = {
            "start_time": None,
            "total_files": 0,
            "total_size": 0,
            "extracted_size": 0,
        }

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
            return False
        if not file_path.endswith(".mtz"):
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
        except Exception:
            return None

    def extract_mtz(self, file_path: str, extract_folder: str) -> bool:
        """Extract MTZ file to folder"""
        try:
            self.stats["start_time"] = time.time()
            self.stats["total_size"] = os.path.getsize(file_path)

            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_folder)
                self.stats["total_files"] = len(zip_ref.namelist())
            return True
        except Exception:
            return False

    def process_files(self, folder: str) -> None:
        """Process files after extraction"""
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


def main():
    root = tk.Tk()
    app = MTZExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
