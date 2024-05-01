import os
import sys
from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow

if __name__ == "__main__":
    # Create the application
    app = QApplication([])

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec_())