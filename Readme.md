# PDF Color Inverter

A Python tool to invert colors in PDF files, creating a dark mode version of documents.

## Description

This tool converts standard PDFs into inverted color versions, making them easier to read in low-light conditions or for users who prefer dark mode. It processes each page of the PDF, inverts the colors, and creates a new PDF with the inverted colors while maintaining the original document structure.

## Features

- Inverts colors of all pages in a PDF document
- Maintains original PDF dimensions and layout
- Configurable output quality (DPI and compression)
- High-quality output by default
- Quick low-quality option for faster processing
- Progress tracking during conversion
- Error handling and validation

## Prerequisites

Before running this tool, make sure you have Python 3.x installed and the following dependencies:

```bash
pip install PyMuPDF Pillow
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/pdf-color-inverter.git
cd pdf-color-inverter
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage (high quality):
```bash
python main.py input.pdf
```

With custom output folder:
```bash
python main.py input.pdf --output-folder custom_folder
```

Low quality for faster processing:
```bash
python main.py input.pdf --low-quality
```

Custom quality settings:
```bash
python main.py input.pdf --dpi 400 --quality 100
```

### Arguments

- `input_pdf`: Path to the input PDF file (required)
- `--output-folder`: Custom output folder path (optional, defaults to "output")
- `--dpi`: Resolution for rendering (72-600, default: 300)
- `--quality`: Image compression quality (1-100, default: 95)
- `--low-quality`: Use low quality preset (150 DPI, 75% quality)

## Quality Settings

The tool provides several ways to control output quality:

1. **Default High Quality**
   - DPI: 300
   - Quality: 95%
   - Best for most use cases

2. **Custom Quality**
   - DPI: 72-600 (higher = better quality, larger file)
   - Quality: 1-100 (higher = better quality, larger file)

3. **Low Quality Preset**
   - DPI: 150
   - Quality: 75%
   - Faster processing, smaller files

## Output

The inverted PDF will be saved in the output folder with "inverted_" prefix:
```
output/
└── inverted_input.pdf
```

## Examples

Converting with default high quality:
```bash
python main.py documents/sample.pdf
```

Using low quality preset:
```bash
python main.py documents/sample.pdf --low-quality
```

Maximum quality settings:
```bash
python main.py documents/sample.pdf --dpi 600 --quality 100
```

Custom quality with specific output location:
```bash
python main.py documents/sample.pdf --output-folder converted_pdfs --dpi 400 --quality 90
```

## Tips

- Use default settings for the best balance of quality and file size
- Use `--low-quality` for quick previews or when file size is a concern
- Higher DPI values (>300) are recommended for documents with small text
- Quality values above 95 usually provide minimal visible improvement
- Consider storage space when processing large PDFs with high quality settings
