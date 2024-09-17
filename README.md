# Japanese OCR Tool

This application allows users to capture Japanese text from their screen using OCR technology. It supports both vertical and horizontal text orientations.

Icon credit to Mina

## Features

- Screen capture with customizable selection area
- OCR for Japanese text
- Automatic clipboard copying of recognized text
- Support for both vertical and horizontal text orientations (TODO)

## Installation

1. Python 3.7+ required
2. Install Tesseract OCR on your system:
   - For macOS:
     ```
     brew install tesseract
     brew install tesseract-lang
     ```
   - For Windows:
     Download and install from https://github.com/UB-Mannheim/tesseract/wiki
     Ensure you select "Japanese" during installation
3. Clone this repository
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```
5. Verify Tesseract installation:
   ```
   tesseract --list-langs
   ```
   Ensure 'jpn' is in the list of available languages

## Usage

### For Python users:
Run the application:
```
python ocr_app.py
```
Press `Ctrl+P` to draw a rectangle over the text you want to OCR.
The text will be automatically copied to your clipboard.
