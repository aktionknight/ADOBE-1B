from PIL import Image
import pytesseract

def extract_headings_from_image(image, page_number):
    """
    Extract heading candidates (H1, H2, H3) from a PIL Image using OCR.
    Args:
        image (PIL.Image.Image): The image to process.
        page_number (int): The 1-based page number.
    Returns:
        list: List of dicts with keys: 'level', 'text', 'page'.
    """
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    n_boxes = len(data['level'])
    # Group words by line number
    lines = {}
    for i in range(n_boxes):
        text = data['text'][i].strip()
        conf_val = data['conf'][i]
        try:
            conf = int(conf_val)
        except (ValueError, TypeError):
            conf = -1
        if not text or conf < 70:
            continue
        line_num = data['line_num'][i]
        if line_num not in lines:
            lines[line_num] = {
                'words': [],
                'height': data['height'][i],
                'top': data['top'][i],
                'left': data['left'][i]
            }
        lines[line_num]['words'].append(text)
        # Use the max height for the line
        lines[line_num]['height'] = max(lines[line_num]['height'], data['height'][i])
    # Now process lines as heading candidates
    candidates = []
    for line in lines.values():
        line_text = ' '.join(line['words']).strip()
        if len(line_text) < 8:
            continue
        candidates.append({
            'text': line_text,
            'height': line['height'],
            'top': line['top'],
            'left': line['left']
        })
    if not candidates:
        return []
    # Find unique heights and sort descending
    unique_heights = sorted(set(c['height'] for c in candidates), reverse=True)
    # Assign levels: largest = H1, next = H2, next = H3
    level_map = {}
    for idx, h in enumerate(unique_heights[:3]):
        level_map[h] = f"H{idx+1}"
    headings = []
    for c in candidates:
        if c['height'] in level_map:
            headings.append({
                'level': level_map[c['height']],
                'text': c['text'],
                'page': page_number
            })
    return headings 