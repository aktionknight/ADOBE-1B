import fitz  # PyMuPDF
from PIL import Image
import io

def render_pdf_page(pdf_path, page_number, zoom=3.0):
    """
    Render a PDF page as a PIL Image.
    Args:
        pdf_path (str): Path to the PDF file.
        page_number (int): Zero-based page index.
        zoom (float): Zoom factor for higher resolution.
    Returns:
        PIL.Image.Image: Rendered page as an image.
    """
    doc = fitz.open(pdf_path)
    page = doc[page_number]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("ppm")
    img = Image.open(io.BytesIO(img_bytes))
    return img 