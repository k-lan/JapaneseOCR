import logging
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from ocr_app import JapaneseOCRApp

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    logger.debug("Starting application")
    app = QApplication(sys.argv)
    window = QMainWindow()
    ocr_app = JapaneseOCRApp()
    window.setCentralWidget(ocr_app)
    logger.debug("JapaneseOCRApp instance created")
    logger.debug("Application entering event loop")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    logger.debug("Reached the end of main.")