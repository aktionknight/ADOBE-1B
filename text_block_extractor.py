import fitz

def extract_text_blocks(pdf_path):
    """
    Extracts text blocks and their features from all pages of a PDF using PyMuPDF.
    Returns a list of dicts: {page, text, font_size, bbox, font, flags}
    """
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for b in page.get_text("dict")['blocks']:
            if 'lines' not in b:
                continue
            for line in b['lines']:
                for span in line['spans']:
                    blocks.append({
                        'page': page_num,
                        'text': span['text'].strip(),
                        'font_size': span['size'],
                        'bbox': span['bbox'],
                        'font': span['font'],
                        'flags': span['flags'],
                        'origin': (span['bbox'][0], span['bbox'][1])
                    })
    return blocks 