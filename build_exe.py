import PyInstaller.__main__
import os

# Get the path to the Tesseract executable
tesseract_path = os.path.expandvars(r'%PROGRAMFILES%\Tesseract-OCR\tesseract.exe')

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--add-data', f'{tesseract_path};.',
    '--add-data', 'icon.png;.',
    '--hidden-import', 'pynput.keyboard._win32',
    '--hidden-import', 'pynput.mouse._win32',
    '--name', 'JapaneseOCR'
])