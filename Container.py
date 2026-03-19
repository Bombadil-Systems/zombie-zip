import sys
import os
import zipfile
import zlib
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QMessageBox, QFrame, QPushButton, QFileDialog)
from PyQt6.QtCore import Qt

CUSTOM_EXTENSION = ".cpack"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Container Tool")
        self.resize(400, 250)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Instructions Label
        self.label = QLabel("Select files to process:\n- Regular files will be PACKED\n- .cpack files will be UNPACKED")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 14px; color: #444;")
        self.layout.addWidget(self.label)
        
        # The Action Button
        self.select_button = QPushButton("Select Files...")
        self.select_button.setHeight = 50
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        self.select_button.clicked.connect(self.open_file_selector)
        self.layout.addWidget(self.select_button)

    def open_file_selector(self):
        # This opens the native OS file picker
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Pack or Unpack",
            "",
            f"All Files (*);;Custom Pack (*{CUSTOM_EXTENSION})"
        )
        
        if not files:
            return

        files_processed = 0
        for filepath in files:
            try:
                if filepath.endswith(CUSTOM_EXTENSION):
                    self.unpack_file(filepath)
                else:
                    self.pack_file(filepath)
                files_processed += 1
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to process {os.path.basename(filepath)}:\n\n{str(e)}")

        if files_processed > 0:
            QMessageBox.information(self, "Success", f"Successfully processed {files_processed} file(s).")

    # --- CORE LOGIC ---
    def pack_file(self, source_filepath):
        archive_filepath = source_filepath + CUSTOM_EXTENSION
        with open(source_filepath, 'rb') as f:
            raw_data = f.read()
            
        compressor = zlib.compressobj(level=zlib.Z_DEFAULT_COMPRESSION, wbits=-15)
        deflated_data = compressor.compress(raw_data) + compressor.flush()
        
        filename = os.path.basename(source_filepath)
        with zipfile.ZipFile(archive_filepath, 'w', compression=zipfile.ZIP_STORED) as zf:
            zf.writestr(filename, deflated_data)

    def unpack_file(self, archive_filepath):
        output_dir = os.path.dirname(archive_filepath)
        with zipfile.ZipFile(archive_filepath, 'r') as zf:
            for item in zf.namelist():
                deflated_data = zf.read(item)
                decompressor = zlib.decompressobj(wbits=-15)
                try:
                    raw_data = decompressor.decompress(deflated_data) + decompressor.flush()
                except zlib.error:
                    raise Exception(f"'{item}' is not valid DEFLATE data.")
                
                output_filepath = os.path.join(output_dir, item)
                if os.path.exists(output_filepath):
                    output_filepath += ".recovered"
                    
                with open(output_filepath, 'wb') as f:
                    f.write(raw_data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())