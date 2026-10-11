import os
import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLabel, QFileDialog, QComboBox, QListWidget, QWidget, QMessageBox, 
    QProgressBar, QGroupBox, QTabWidget, QGridLayout, QSplashScreen
)
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor, QPixmap

from core.image_converter import ImageConverter
from version import __version__

# Resolved from this file, so the graphics are found whatever the working
# directory is, and inside a PyInstaller bundle too.
SPLASH_DURATION_MS = 2000

GRAPHICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graphics")


def resource_path(name):
    """Return the absolute path of a file in ui/graphics, with forward slashes."""
    return os.path.join(GRAPHICS_DIR, name).replace("\\", "/")


def app_icon():
    """Application icon (.ico on Windows, .png everywhere else)."""
    return QIcon(resource_path('logo.ico' if sys.platform == 'win32' else 'logo.png'))


def install_desktop_entry():
    """
    Register the app with the Linux desktop (menu entry + icon).

    Wayland desktops such as GNOME ignore the window icon set by the
    application, they only show the icon of the matching .desktop file.
    """
    try:
        data_home = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        icon_dir = os.path.join(data_home, "icons", "hicolor", "256x256", "apps")
        apps_dir = os.path.join(data_home, "applications")
        os.makedirs(icon_dir, exist_ok=True)
        os.makedirs(apps_dir, exist_ok=True)

        # The icon is copied out, a PyInstaller bundle only unpacks it temporarily
        icon_path = os.path.join(icon_dir, "imageflow.png")
        with open(resource_path("logo.png"), "rb") as f:
            icon_data = f.read()
        if not os.path.exists(icon_path) or open(icon_path, "rb").read() != icon_data:
            with open(icon_path, "wb") as f:
                f.write(icon_data)

        if getattr(sys, "frozen", False):
            command = f'"{sys.executable}"'
        else:
            command = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'

        entry = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=ImageFlow\n"
            "Comment=Offline image format converter\n"
            f"Exec={command}\n"
            f"Icon={icon_path}\n"
            "Terminal=false\n"
            "Categories=Graphics;\n"
            "StartupWMClass=ImageFlow\n"
        )
        entry_path = os.path.join(apps_dir, "ImageFlow.desktop")
        if not os.path.exists(entry_path) or open(entry_path).read() != entry:
            with open(entry_path, "w") as f:
                f.write(entry)
    except OSError as e:
        logging.warning(f"Could not register the desktop entry: {e}")


# class SplashScreen(QSplashScreen):
#     def __init__(self):
#         super().__init__()
#         # Load splash image (Make sure the file exists in the correct path)
#         pixmap = QPixmap("graphics/splash.png")  # Replace with your splash screen image
#         self.setPixmap(pixmap)
#         self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Removes the window border
#         self.show()

class StyleHelper:
    # Theme color definitions
    THEMES = {
        'dark': {
            'primary': '#38410b',      # Deep blue-grey
            'secondary': '#596711',    # Lighter blue-grey
            'accent': '#7c910f',       # Muted purple-blue
            'background': '#101010',   # Dark background
            'surface': '#242621',      # Slightly lighter than background
            'text': '#F6F6F6',         # Off-white
            'text_secondary': '#B4B4B4', # Muted text
            'success': '#4CAF50',      # Green
            'error': '#F44336',        # Red
            'warning': '#FF9800',      # Orange
            'border': '#596711'        # Border color
        },
        'light': {
            'primary': '#2E4E1A',      # Rich, earthy green (matches dark mode depth)
            'secondary': '#5F7A41',    # Softer green with warmth
            'accent': '#A3C232',       # Vibrant yet natural accent
            'background': '#FAFAF5',   # Slightly off-white for softness
            'surface': '#EFF0E8',      # Gentle contrast for UI elements
            'text': '#2C3A1F',         # Darker greenish-grey for high readability
            'text_secondary': '#6F8054', # Softer muted text
            'success': '#4CAF50',      # Consistent success green
            'error': '#D6453D',        # Slightly softened red
            'warning': '#E8A20C',      # Warmer orange for warning
            'border': '#5F7A41'        # Harmonizing border color
        }
    }

    @staticmethod
    def apply_theme(app, theme='dark'):
        """Apply the specified theme to the application."""
        colors = StyleHelper.THEMES[theme]
        
        # Set up palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['background']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['surface']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['primary']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['surface']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['secondary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors['accent']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['text']))
        
        app.setPalette(palette)
        
        # Modern stylesheet with enhanced visual hierarchy and interactions
        app.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors['background']};
            }}
            
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }}
            
            QPushButton {{
                background-color: {colors['secondary']};
                color: {colors['text']};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 100px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['accent']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['primary']};
            }}
            
            #themeToggleButton {{
                background-color: transparent;
                border: 1px solid {colors['accent']};
                min-width: 40px;
                padding: 1px 2px;
            }}
            
            QGroupBox {{
                background-color: {colors['surface']};
                border-radius: 8px;
                padding: 12px;
                margin-top: 16px;
                font-weight: bold;
                border: 1px solid {colors['border']};
            }}
            
            QGroupBox::title {{
                color: {colors['text']};
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
            }}
            
            QListWidget {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 5px;
            }}
            
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
                color: {colors['text']};
            }}
            
            QListWidget::item:selected {{
                background-color: {colors['accent']};
                color: {'#FFFFFF' if theme == 'dark' else '#FFFFFF'};
            }}
            
            QListWidget::item:hover {{
                background-color: {colors['secondary']};
            }}
            
            QComboBox {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 6px;
                min-width: 100px;
                color: {colors['text']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox::down-arrow {{
                width: 16px;
                height: 16px;
                margin-right: 6px;
                image: url("{resource_path('drk_dwn.png' if theme == 'dark' else 'lt_dwn.png')}");
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                color: {colors['text']};
                selection-background-color: {colors['accent']};
                selection-color: {'#FFFFFF' if theme == 'dark' else '#FFFFFF'};
            }}
            
            QProgressBar {{
                background-color: {colors['surface']};
                border: none;
                border-radius: 6px;
                text-align: center;
                height: 12px;
                color: {colors['text']};
            }}
            
            QProgressBar::chunk {{
                background-color: {colors['accent']};
                border-radius: 6px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                background-color: {colors['surface']};
                border-radius: 0px;
            }}
            QTabBar::tab {{
                background-color: {colors['primary']};
                color: {'#FFFFFF' if theme == 'dark' else '#FFFFFF'};
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors['accent']};
            }}
            
            QLabel {{
                color: {colors['text']};
                font-size: 14px;
                border-radius: 4px;
                padding-left: 4px;
            }}
            
            QMessageBox {{
                background-color: {colors['surface']};
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
            }}
            
            QToolTip {{
                background-color: {colors['surface']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                padding: 4px;
                border-radius: 4px;
            }}
        """)
        
class ConversionThread(QThread):
    conversion_progress = pyqtSignal(int, int)
    conversion_complete = pyqtSignal(list, list)

    def __init__(self, files, output_format, output_directory):
        super().__init__()
        self.files = files
        self.output_format = output_format
        self.output_directory = output_directory

    def run(self):
        converted_files = []
        failed_files = []
        for i, file in enumerate(self.files, 1):
            result = ImageConverter.convert_image(file, self.output_directory, self.output_format)
            if result:
                converted_files.append(result)
            else:
                failed_files.append(file)
            self.conversion_progress.emit(i, len(self.files))
        
        self.conversion_complete.emit(converted_files, failed_files)

class ImageFlowMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"ImageFlow {__version__} - Image Converter")
        self.resize(555, 910)
        self.setWindowIcon(app_icon())

        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add theme toggle button in a header section
        header_layout = QHBoxLayout()
        self.theme_toggle = QPushButton()
        self.theme_toggle.setObjectName("themeToggleButton")
        self.theme_toggle.setIcon(QIcon(resource_path('dark.png')))
        self.theme_toggle.setFixedSize(40, 40)
        self.theme_toggle.setToolTip("Toggle Dark/Light Mode")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        
        header_layout.addStretch()
        header_layout.addWidget(self.theme_toggle)
        main_layout.addLayout(header_layout)

        # Main Tabs
        self.main_tabs = QTabWidget()
        
        # Conversion Tab
        conversion_tab = QWidget()
        conversion_layout = QVBoxLayout(conversion_tab)

        # Files Group
        files_group = QGroupBox("Image Files - drag and drop files or folders here")
        files_layout = QHBoxLayout(files_group)
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

        # Images and folders can be dropped anywhere on the window
        self.setAcceptDrops(True)
        
        # File Actions Buttons
        # file_actions_layout = QVBoxLayout()
        # add_files_btn = QPushButton("Add Files")
        # add_files_btn.setIcon(QIcon('add_icon.png'))
        # remove_files_btn = QPushButton("Remove Files")
        # remove_files_btn.setIcon(QIcon('remove_icon.png'))
        
        # file_actions_layout.addWidget(add_files_btn)
        # file_actions_layout.addWidget(remove_files_btn)
        # file_actions_layout.addStretch(1)

        # files_layout.addWidget(self.files_list)
        # files_layout.addLayout(file_actions_layout)

                # File Actions Buttons
        file_actions_layout = QVBoxLayout()
        add_files_btn = QPushButton("Add Files")
        remove_files_btn = QPushButton("Remove Files")
        
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
        self.format_combo.addItems(ImageConverter.SUPPORTED_FORMATS)
        
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
        self.convert_btn = QPushButton("Convert Images")

        # Add to Conversion Layout
        conversion_layout.addWidget(files_group)
        conversion_layout.addWidget(options_group)
        conversion_layout.addWidget(self.convert_btn)
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
        self.convert_btn.clicked.connect(self.start_conversion)

        # Store current theme (main() starts the app with the dark theme)
        self.current_theme = "dark"

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        app = QApplication.instance()
        if self.current_theme == "light":
            StyleHelper.apply_theme(app, "dark")
            self.current_theme = "dark"

        else:
            StyleHelper.apply_theme(app, "light")
            self.current_theme = "light"
            
    def select_output_directory(self):
        """Select output directory for conversions."""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        # Keep the previous choice if the dialog was cancelled
        if directory:
            self.output_directory = directory
            self.output_dir_btn.setText(f"Selected: {self.output_directory}")

    def add_files(self):
        """Add image files to conversion list."""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Images", 
            "", 
            "Image Files (*.jpg *.jpeg *.png *.webp *.tiff *.tif *.bmp *.gif *.heic *.heif "
            "*.JPG *.JPEG *.PNG *.WEBP *.TIFF *.TIF *.BMP *.GIF *.HEIC *.HEIF);;All Files (*)"
        )
        self.add_paths(files)

    def add_paths(self, files):
        """Add files to the conversion list, returns how many were new."""
        added = 0
        for file in files:
            # Prevent duplicates
            if self.files_list.findItems(file, Qt.MatchFlag.MatchExactly):
                continue
            self.files_list.addItem(file)
            added += 1
        return added

    def dragEnterEvent(self, event):
        """Accept files and folders dragged from the file manager."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Add dropped images, and every image found inside dropped folders."""
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                files.extend(ImageConverter.find_images(path))
            elif os.path.isfile(path) and ImageConverter.is_image_file(path):
                files.append(path)

        added = self.add_paths(files)
        if added:
            self.progress_label.setText(f"{added} images added")
        elif files:
            self.progress_label.setText("These images are already in the list")
        else:
            self.progress_label.setText("No supported images found in what was dropped")
        event.acceptProposedAction()

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

        # Only one conversion at a time
        self.convert_btn.setEnabled(False)
        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)

        self.conversion_thread = ConversionThread(files, output_format, self.output_directory)
        self.conversion_thread.conversion_progress.connect(self.update_progress)
        self.conversion_thread.conversion_complete.connect(self.conversion_finished)
        self.conversion_thread.start()

    def update_progress(self, current, total):
        """Update conversion progress."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Converting: {current}/{total} images")

    def conversion_finished(self, converted_files, failed_files):
        """Handle conversion completion."""
        self.convert_btn.setEnabled(True)
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.progress_label.setText(f"Conversion complete. {len(converted_files)} images converted.")
        if failed_files:
            QMessageBox.warning(self, "Conversion Complete",
                                f"{len(converted_files)} images successfully converted.\n"
                                f"{len(failed_files)} could not be converted:\n"
                                + "\n".join(os.path.basename(f) for f in failed_files[:10])
                                + ("\n..." if len(failed_files) > 10 else ""))
        else:
            QMessageBox.information(self, "Conversion Complete", 
                                    f"{len(converted_files)} images successfully converted.")

    def closeEvent(self, event):
        """Let a running conversion finish before the window is destroyed."""
        if self.conversion_thread and self.conversion_thread.isRunning():
            self.conversion_thread.wait()
        super().closeEvent(event)


# def main():
#     app = QApplication(sys.argv)
#     StyleHelper.apply_theme(app,theme="dark")
#     window = ImageFlowMainWindow()
#     window.show()
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()
def main():
    if sys.platform.startswith("linux"):
        # Must match the name of the .desktop file so the desktop finds the icon,
        # and be set before the application connects to the display
        QApplication.setDesktopFileName("ImageFlow")
        install_desktop_entry()

    app = QApplication(sys.argv)
    app.setApplicationName("ImageFlow")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(app_icon())

    # The splash screen is optional, the app still starts without it
    splash = None
    splash_pixmap = QPixmap(resource_path("splash.png"))
    if not splash_pixmap.isNull():
        splash = QSplashScreen(splash_pixmap, Qt.WindowType.FramelessWindowHint)
        splash.show()
        app.processEvents()

    StyleHelper.apply_theme(app, theme="dark")
    window = ImageFlowMainWindow()

    # Keep the window inside the screen on small displays
    screen = app.primaryScreen()
    if screen:
        available = screen.availableGeometry()
        window.resize(min(window.width(), available.width() - 40),
                      min(window.height(), available.height() - 80))

    def show_window():
        window.show()
        if splash:
            splash.finish(window)

    # Startup is fast, keep the splash on screen long enough to be seen
    QTimer.singleShot(SPLASH_DURATION_MS if splash else 0, show_window)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()