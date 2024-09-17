from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QApplication, QWidget, QRubberBand
from PyQt6.QtGui import QIcon, QScreen, QAction, QKeySequence, QColor, QPainter
from PyQt6.QtCore import Qt, QRect, QThread, pyqtSignal
from pynput import keyboard
import mss
import pytesseract
import pyperclip
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KeyboardListener(QThread):
    hotkey_pressed = pyqtSignal()
    
    def run(self):
        with keyboard.GlobalHotKeys({'<ctrl>+p': self.emit_hotkey}) as h:
            h.join()

    def emit_hotkey(self):
        self.hotkey_pressed.emit()

    def stop(self):
        self.terminate()
        self.wait()

class JapaneseOCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.check_tesseract_installation()
        self.setupSystemTray()
        self.setupKeyboardListener()
        self.setupQuitShortcut()

    def check_tesseract_installation(self):
        try:
            languages = pytesseract.get_languages()
            if 'jpn' not in languages:
                raise RuntimeError("Japanese language data not found for Tesseract")
        except pytesseract.TesseractNotFoundError:
            print("Tesseract is not installed or not in the system PATH")
        except RuntimeError as e:
            print(f"Tesseract error: {str(e)}")

    def initUI(self):
        self.setWindowTitle('Japanese OCR')
        self.setGeometry(100, 100, 300, 200)

    def setupSystemTray(self):
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        tray_menu = QMenu()
        tray_menu.addAction("Capture", self.captureScreen)
        quit_action = tray_menu.addAction("Quit", self.quit_application)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setupKeyboardListener(self):
        self.keyboard_listener = KeyboardListener()
        self.keyboard_listener.hotkey_pressed.connect(self.captureScreen)
        self.keyboard_listener.start()

    def setupQuitShortcut(self):
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.quit_application)
        self.addAction(quit_action)

    def quit_application(self):
        logger.debug("Quitting application")
        self.keyboard_listener.stop()
        self.tray_icon.hide()
        QApplication.quit()
        QApplication.processEvents()  # Process any remaining events
        logger.debug("Successfully quit application")
        sys.exit(0)  # Force exit the application

    def captureScreen(self):
        logger.debug("captureScreen method called")
        screen = QApplication.primaryScreen()
        logger.debug("Creating ScreenshotSelector")
        self.selector = ScreenshotSelector()
        self.selector.setGeometry(screen.geometry())
        self.selector.screenshot_taken.connect(self.processScreenshot)
        self.selector.cancelled.connect(self.onCaptureCancelled)
        logger.debug("Showing ScreenshotSelector")
        self.selector.show()
        logger.debug("ScreenshotSelector show() called")
        
        QApplication.setActiveWindow(self.selector)
        self.selector.activateWindow()
        self.selector.raise_()

    def processScreenshot(self, image_path):
        logger.debug(f"Processing screenshot: {image_path}")
        text = self.performOCR(image_path)
        self.copyToClipboard(text)
        print("Text copied to clipboard")
        self.selector.deleteLater()  # Schedule the selector for deletion

    def onCaptureCancelled(self):
        logger.debug("Screenshot capture cancelled")
        self.selector.deleteLater()  # Schedule the selector for deletion

    def performOCR(self, image_path):
        text = pytesseract.image_to_string(image_path, lang='jpn')
        return text

    def copyToClipboard(self, text):
        pyperclip.copy(text)

    def closeEvent(self, event):
        self.keyboard_listener.stop()
        self.tray_icon.hide()
        event.accept()

class ScreenshotSelector(QWidget):
    screenshot_taken = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("ScreenshotSelector initialized")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.BypassWindowManagerHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")  # Make it more transparent
        self.rubberband = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = None
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)  # Enable mouse tracking
        logger.debug("ScreenshotSelector setup complete")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()

    def mousePressEvent(self, event):
        logger.debug(f"Mouse press event in ScreenshotSelector at {event.pos()}")
        self.origin = event.pos()
        self.rubberband.setGeometry(QRect(self.origin, self.origin))
        self.rubberband.show()
        event.accept()  # Explicitly accept the event

    def mouseMoveEvent(self, event):
        logger.debug(f"Mouse move event in ScreenshotSelector at {event.pos()}")
        if self.origin:
            self.rubberband.setGeometry(QRect(self.origin, event.pos()).normalized())
        event.accept()  # Explicitly accept the event

    def mouseReleaseEvent(self, event):
        logger.debug(f"Mouse release event in ScreenshotSelector at {event.pos()}")
        if self.origin:
            rect = QRect(self.origin, event.pos()).normalized()
            self.screenshot(rect)
        event.accept()  # Explicitly accept the event

    def screenshot(self, rect):
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        pixmap.save("screenshot.png")
        self.screenshot_taken.emit("screenshot.png")
        self.close()

    def paintEvent(self, event):
        logger.debug("Paint event in ScreenshotSelector")
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 50))  # Semi-transparent overlay
        super().paintEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = JapaneseOCRApp()
    app.exec()