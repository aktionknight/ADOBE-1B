import numpy as np
from sklearn.cluster import KMeans
from text_block_extractor import extract_text_blocks

def extract_title_from_pdf(pdf_path, y_threshold_ratio=0.35):
    """
    Extract the title from page 0 by grouping all text blocks with the same font size and font as the largest text block at the top.
    Allow for multi-line titles with spacing. Returns a dict: {"text": title, "bbox": [x0, y0, x1, y1]}.
    """
    blocks = extract_text_blocks(pdf_path)
    # Only consider page 0
    page0_blocks = [b for b in blocks if b['page'] == 0 and len(b['text']) > 2]
    if not page0_blocks:
        return {"text": "", "bbox": None}
    # Find the largest font size at the top of the page (within y_threshold_ratio)
    min_y = min(b['bbox'][1] for b in page0_blocks)
    max_y = max(b['bbox'][3] for b in page0_blocks)
    y_threshold = min_y + (max_y - min_y) * y_threshold_ratio
    top_blocks = [b for b in page0_blocks if b['bbox'][1] <= y_threshold]
    if not top_blocks:
        top_blocks = page0_blocks
    # Find the most common (font_size, font) among top_blocks
    from collections import Counter
    font_pairs = [(b['font_size'], b['font']) for b in top_blocks]
    if not font_pairs:
        return {"text": "", "bbox": None}
    (title_size, title_font), _ = Counter(font_pairs).most_common(1)[0]
    # Group all blocks on page 0 with this font size and font
    title_blocks = [b for b in page0_blocks if abs(b['font_size'] - title_size) < 0.1 and b['font'] == title_font]
    # Sort by y-position (top to bottom), then x (left to right)
    title_blocks = sorted(title_blocks, key=lambda b: (b['origin'][1], b['origin'][0]))
    # Allow for multi-line titles with spacing (not too strict)
    if not title_blocks:
        return {"text": "", "bbox": None}
    # Group lines that are reasonably close vertically (allowing for spacing)
    grouped = []
    current_group = [title_blocks[0]]
    for prev, curr in zip(title_blocks, title_blocks[1:]):
        vertical_gap = curr['origin'][1] - prev['origin'][1]
        if vertical_gap < (title_size * 2.5):  # Allow up to 2.5x font size as gap
            current_group.append(curr)
        else:
            grouped.append(current_group)
            current_group = [curr]
    grouped.append(current_group)
    # Take the first group as the title
    title_group = grouped[0]
    title_text = ' '.join([b['text'] for b in title_group]).strip()
    # Compute bounding box for the title
    x0 = min(b['bbox'][0] for b in title_group)
    y0 = min(b['bbox'][1] for b in title_group)
    x1 = max(b['bbox'][2] for b in title_group)
    y1 = max(b['bbox'][3] for b in title_group)
    return {"text": title_text, "bbox": [x0, y0, x1, y1]} 