import os
import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLabel, QFileDialog, QComboBox, QListWidget, QWidget, QMessageBox, 
    QProgressBar, QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap

from core.image_converter import ImageConverter
from database.conversion_history import ConversionHistoryDB

class StyleHelper:
    @staticmethod
    def apply_dark_theme(app):
        """Apply a dark theme to the entire application."""
        app.setStyle("Fusion")
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        app.setPalette(dark_palette)
        app.setStyleSheet("""
            QWidget {
                background-color: #353535;
                color: white;
                font-family: Arial;
            }
            QPushButton {
                background-color: #5A5A5A;
                color: white;
                border: 1px solid #707070;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #707070;
            }
            QListWidget {
                background-color: #252525;
                border: 1px solid #505050;
            }
            QProgressBar {
                border: 1px solid #707070;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #5A9AC3;
                width: 10px;
                margin: 0.5px;
            }
        """)

class ConversionHistoryDialog(QDialog):
    def __init__(self, history_db):
        super().__init__()
        self.history_db = history_db
        self.setWindowTitle("Conversion History")
        self.setGeometry(200, 200, 800, 400)

        layout = QVBoxLayout()
        
        # History Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["Source Path", "Destination Path", "Input Format", "Output Format", "Conversion Time"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.history_table)

        # Buttons
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.load_history()

    def load_history(self):
        """Load conversion history into the table."""
        history = self.history_db.get_conversion_history()
        self.history_table.setRowCount(len(history))
        
        for row, record in enumerate(history):
            for col, value in enumerate(record):
                self.history_table.setItem(row, col, QTableWidgetItem(str(value)))

    def clear_history(self):
        """Clear conversion history."""
        reply = QMessageBox.question(
            self, 'Clear History', 
            "Are you sure you want to clear all conversion history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_db.clear_history()
            self.load_history()

class ConversionThread(QThread):
    conversion_progress = pyqtSignal(int, int)
    conversion_complete = pyqtSignal(list)

    def __init__(self, files, output_format, output_directory):
        super().__init__()
        self.files = files
        self.output_format = output_format
        self.output_directory = output_directory

    def run(self):
        converted_files = []
        for i, file in enumerate(self.files, 1):
            result = ImageConverter.convert_image(file, self.output_directory, self.output_format)
            if result:
                converted_files.append(result)
            self.conversion_progress.emit(i, len(self.files))
        
        self.conversion_complete.emit(converted_files)

class ImageFlowMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImageFlow - Image Converter")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon('icon.png'))  # Add your app icon

        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')

        # Database for tracking
        self.history_db = ConversionHistoryDB()

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Main Tabs
        self.main_tabs = QTabWidget()
        
        # Conversion Tab
        conversion_tab = QWidget()
        conversion_layout = QVBoxLayout(conversion_tab)

        # Files Group
        files_group = QGroupBox("Image Files")
        files_layout = QHBoxLayout(files_group)
        self.files_list = QListWidget()
        
        # File Actions Buttons
        file_actions_layout = QVBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.setIcon(QIcon('add_icon.png'))  # Use appropriate icon
        remove_files_btn = QPushButton("Remove Files")
        remove_files_btn.setIcon(QIcon('remove_icon.png'))  # Use appropriate icon
        
        file_actions_layout.addWidget(add_files_btn)
        file_actions_layout.addWidget(remove_files_btn)
        file_actions_layout.addStretch(1)

        files_layout.addWidget(self.files_list)
        files_layout.addLayout(file_actions_layout)

        # Conversion Options
        options_group = QGroupBox("Conversion Options")
        options_layout = QGridLayout(options_group)
        
        format_label = QLabel("Output Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(list(ImageConverter.SUPPORTED_FORMATS))
        
        output_dir_label = QLabel("Output Directory:")
        self.output_dir_btn = QPushButton("Select Output Directory")
        
        options_layout.addWidget(format_label, 0, 0)
        options_layout.addWidget(self.format_combo, 0, 1)
        options_layout.addWidget(output_dir_label, 1, 0)
        options_layout.addWidget(self.output_dir_btn, 1, 1)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_label = QLabel("Ready to convert")

        # Convert Button
        convert_btn = QPushButton("Convert Images")
        convert_btn.setIcon(QIcon('convert_icon.png'))  # Use appropriate icon

        # History Button
        history_btn = QPushButton("View Conversion History")
        history_btn.setIcon(QIcon('history_icon.png'))  # Use appropriate icon

        # Add to Conversion Layout
        conversion_layout.addWidget(files_group)
        conversion_layout.addWidget(options_group)
        conversion_layout.addWidget(convert_btn)
        conversion_layout.addWidget(history_btn)
        conversion_layout.addWidget(self.progress_label)
        conversion_layout.addWidget(self.progress_bar)

        # Add Tabs
        self.main_tabs.addTab(conversion_tab, "Conversion")
        main_layout.addWidget(self.main_tabs)

        # Conversion thread
        self.conversion_thread = None
        self.output_directory = None

        # Connect signals and slots
        add_files_btn.clicked.connect(self.add_files)
        remove_files_btn.clicked.connect(self.remove_files)
        self.output_dir_btn.clicked.connect(self.select_output_directory)
        convert_btn.clicked.connect(self.start_conversion)
        history_btn.clicked.connect(self.show_history)

    def select_output_directory(self):
        """Select output directory for conversions."""
        self.output_directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if self.output_directory:
            self.output_dir_btn.setText(f"Selected: {self.output_directory}")

    def add_files(self):
        """Add image files to conversion list."""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Images", 
            "", 
            "Image Files (*.jpg *.jpeg *.png *.webp *.tiff *.bmp *.gif *.heic)"
        )
        for file in files:
            # Prevent duplicates
            if self.files_list.findItems(file, Qt.MatchFlag.MatchExactly):
                continue
            self.files_list.addItem(file)

    def remove_files(self):
        """Remove selected files from conversion list."""
        for item in self.files_list.selectedItems():
            self.files_list.takeItem(self.files_list.row(item))

    def start_conversion(self):
        """Start image conversion process."""
        files = [self.files_list.item(i).text() for i in range(self.files_list.count())]
        output_format = self.format_combo.currentText()
        
        if not files:
            QMessageBox.warning(self, "Error", "Please select files to convert")
            return

        if not self.output_directory:
            QMessageBox.warning(self, "Error", "Please select an output directory")
            return

        self.conversion_thread = ConversionThread(files, output_format, self.output_directory)
        self.conversion_thread.conversion_progress.connect(self.update_progress)
        self.conversion_thread.conversion_complete.connect(self.conversion_finished)
        self.conversion_thread.start()

    def update_progress(self, current, total):
        """Update conversion progress."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Converting: {current}/{total} images")

    def conversion_finished(self, converted_files):
        """Handle conversion completion."""
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.progress_label.setText(f"Conversion complete. {len(converted_files)} images converted.")
        QMessageBox.information(self, "Conversion Complete", 
                                f"{len(converted_files)} images successfully converted.")

    def show_history(self):
        """Show conversion history dialog."""
        history_dialog = ConversionHistoryDialog(self.history_db)
        history_dialog.exec()

def main():
    app = QApplication(sys.argv)
    StyleHelper.apply_dark_theme(app)
    window = ImageFlowMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()