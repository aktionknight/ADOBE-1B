import numpy as np
from sklearn.cluster import KMeans
from text_block_extractor import extract_text_blocks
import re
from collections import Counter

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def merge_multiline_headings(headings):
    merged = []
    prev = None
    for h in headings:
        if prev and h['page'] == prev['page'] and h['level'] == prev['level'] and abs(h['page'] - prev['page']) < 2:
            prev['text'] += ' ' + h['text']
        else:
            if prev:
                merged.append(prev)
            prev = h.copy()
    if prev:
        merged.append(prev)
    return merged

def extract_headings_from_pdf(pdf_path, n_levels=3):
    """
    Globally group and sort all heading candidates by font size (and font) within the PDF.
    Assign H1/H2/H3 based on the top 3 largest font sizes that are not body text, regardless of page.
    Do not require each page to have all heading levels. Only cluster within the current PDF.
    Returns a list of dicts: {level, text, page}
    """
    blocks = extract_text_blocks(pdf_path)
    # Only consider pages > 0 and ignore table blocks (block type 5 in PyMuPDF, if available)
    blocks = [b for b in blocks if b['page'] > 0 and len(b['text']) > 8 and not (hasattr(b, 'type') and b['type'] == 5)]
    if not blocks:
        return []
    # Get all unique (font_size, font) pairs and their counts
    font_pairs = [(b['font_size'], b['font']) for b in blocks]
    font_counter = Counter(font_pairs)
    # Assume the most common font size is body text, exclude it
    most_common_pair, _ = font_counter.most_common(1)[0]
    heading_pairs = [pair for pair, _ in font_counter.most_common() if pair != most_common_pair]
    # Take the top n_levels largest font sizes (not body text)
    heading_pairs = sorted(heading_pairs, key=lambda x: -x[0])[:n_levels]
    # Map each heading pair to a level
    level_map = {pair: f"H{i+1}" for i, pair in enumerate(heading_pairs)}
    # Assign levels to blocks
    headings = []
    seen = set()
    for b in sorted(blocks, key=lambda x: (x['page'], x['origin'][1])):
        pair = (b['font_size'], b['font'])
        if pair not in level_map:
            continue
        text = clean_text(b['text'])
        if len(text) < 8 or len(text) > 120:
            continue
        if text.lower() in seen:
            continue
        seen.add(text.lower())
        words = text.split()
        cap_ratio = sum(1 for w in words if w.istitle()) / max(1, len(words))
        if cap_ratio < 0.5 and not re.match(r'^(\d+\.|[A-Z][A-Za-z0-9\- ]+:?)', text):
            continue
        headings.append({
            'level': level_map[pair],
            'text': text,
            'page': b['page']
        })
    # Merge multi-line headings
    headings = merge_multiline_headings(headings)
    return headings 