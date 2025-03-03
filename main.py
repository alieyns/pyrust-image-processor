"""VFX Image Processor main entry point."""

import sys
from PySide6 import QtWidgets as Widgets
from src.gui.main_window import MainWindow

__all__ = ['main']

def main() -> None:
    """Initialize and run the application."""
    app = Widgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
