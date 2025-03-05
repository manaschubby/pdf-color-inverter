import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io
import os
import sys
import argparse
import concurrent.futures
from tqdm import tqdm

def process_page(args):
    """Process a single page in parallel"""
    document, page_num, dpi, quality = args

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

    # Return relevant info for output
    return {
        'page_num': page_num,
        'img_bytes': img_bytes,
        'rect': page.rect,
        'annots': list(page.annots())
    }

def invert_pdf_colors(input_pdf_path, output_folder, dpi=300, quality=95, threads=10):
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

        # Prepare arguments for parallel processing
        page_count = len(document)
        process_args = [(document, i, dpi, quality) for i in range(page_count)]

        # Process pages in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            # Use tqdm for a progress bar
            results = list(tqdm(
                executor.map(process_page, process_args),
                total=page_count,
                desc="Inverting pages"
            ))

        # Sort results by page number to maintain order
        results.sort(key=lambda x: x['page_num'])

        # Create output PDF from processed pages
        for result in results:
            # Create new page in output PDF
            new_page = output_pdf.new_page(width=result['rect'].width, height=result['rect'].height)

            # Insert inverted image into the new page
            new_page.insert_image(
                fitz.Rect(0, 0, result['rect'].width, result['rect'].height),
                stream=result['img_bytes']
            )

            # Copy annotations
            for annot in result['annots']:
                new_page.insert_annot(annot.rect, annot)

        # Copy outlines (table of contents)
        toc = document.get_toc()
        output_pdf.set_toc(toc)

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
    parser.add_argument('--threads', type=int, default=10,
                        help='Number of parallel threads to use (default: 10)')

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

    # Validate threads parameter
    if args.threads < 1:
        print("Error: Number of threads must be at least 1")
        sys.exit(1)

    # Process the PDF
    invert_pdf_colors(args.input_pdf, args.output_folder, dpi, quality, args.threads)

if __name__ == "__main__":
    main()
