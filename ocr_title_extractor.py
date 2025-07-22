from PIL import Image
import pytesseract


def extract_title_from_image(image):
    """
    Extract the most prominent text block (likely the title) from a PIL Image using OCR.
    Args:
        image (PIL.Image.Image): The image to process.
    Returns:
        str: The extracted title text.
    """
    # Run OCR with layout info
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    n_boxes = len(data['level'])
    # Find the largest text (by height) near the top of the page
    candidates = []
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if not text:
            continue
        # Use height as a proxy for prominence
        height = data['height'][i]
        top = data['top'][i]
        left = data['left'][i]
        candidates.append({
            'text': text,
            'height': height,
            'top': top,
            'left': left
        })
    # Sort by height (desc), then by top (asc)
    candidates = sorted(candidates, key=lambda x: (-x['height'], x['top']))
    # Take the largest block(s) near the top
    if not candidates:
        return ""
    max_height = candidates[0]['height']
    # Allow a small tolerance for similar-sized text
    prominent = [c for c in candidates if c['height'] >= max_height * 0.9 and c['top'] < image.height * 0.5]
    # Join all prominent blocks in reading order (left to right, then top to bottom)
    prominent = sorted(prominent, key=lambda x: (x['top'], x['left']))
    title = ' '.join([c['text'] for c in prominent])
    return title.strip() 