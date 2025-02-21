import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io
import os
import sys
import argparse

def invert_pdf_colors(input_pdf_path, output_folder, dpi=300, quality=95):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Generate output filename
    input_filename = os.path.basename(input_pdf_path)
    output_filename = f"inverted_{input_filename}"
    output_pdf_path = os.path.join(output_folder, output_filename)

    try:
        # Open the input PDF
        document = fitz.open(input_pdf_path)
        # Create a new PDF to store the inverted pages
        output_pdf = fitz.open()

        print(f"Processing {input_filename}...")

        for page_num in range(len(document)):
            print(f"Inverting page {page_num + 1}/{len(document)}")
            # Extract the page
            page = document.load_page(page_num)

            # Get the zoom factors to achieve the desired DPI
            zoom = dpi / 72  # 72 is the base DPI
            matrix = fitz.Matrix(zoom, zoom)

            # Render the page as an image (pixmap) with higher resolution
            pix = page.get_pixmap(matrix=matrix)

            # Convert the pixmap to a PIL Image
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Invert the image colors
            inverted_img = ImageOps.invert(img.convert("RGB"))

            # Convert PIL image to bytes with specified quality
            img_bytes = io.BytesIO()
            inverted_img.save(img_bytes, format='PNG', optimize=True, quality=quality)
            img_bytes = img_bytes.getvalue()

            # Create new page in output PDF
            new_page = output_pdf.new_page(width=page.rect.width, height=page.rect.height)

            # Insert inverted image into the new page
            new_page.insert_image(
                fitz.Rect(0, 0, page.rect.width, page.rect.height),
                stream=img_bytes
            )

        # Save the output PDF
        output_pdf.save(output_pdf_path, garbage=4, deflate=True)
        print(f"Successfully created inverted PDF: {output_pdf_path}")

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        sys.exit(1)
    finally:
        # Close the documents
        document.close()
        output_pdf.close()

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Invert colors of a PDF file')
    parser.add_argument('input_pdf', help='Path to the input PDF file')
    parser.add_argument('--output-folder', default='output',
                        help='Output folder path (default: output)')
    parser.add_argument('--dpi', type=int, default=300,
                        help='DPI for rendering (default: 300). Higher values give better quality but larger files')
    parser.add_argument('--quality', type=int, default=95,
                        help='Image quality (1-100, default: 95). Higher values give better quality but larger files')
    parser.add_argument('--low-quality', action='store_true',
                        help='Use low quality settings (equivalent to --dpi 150 --quality 75)')

    # Parse arguments
    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file '{args.input_pdf}' does not exist")
        sys.exit(1)

    if not args.input_pdf.lower().endswith('.pdf'):
        print("Error: Input file must be a PDF")
        sys.exit(1)

    # Set quality settings
    if args.low_quality:
        dpi = 150
        quality = 75
    else:
        dpi = args.dpi
        quality = args.quality

    # Validate quality parameters
    if not (1 <= quality <= 100):
        print("Error: Quality must be between 1 and 100")
        sys.exit(1)

    if not (72 <= dpi <= 600):
        print("Error: DPI must be between 72 and 600")
        sys.exit(1)

    # Process the PDF
    invert_pdf_colors(args.input_pdf, args.output_folder, dpi, quality)

if __name__ == "__main__":
    main()
