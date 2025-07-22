import os
import json
from kmeans_title_extractor import extract_title_from_pdf
from kmeans_heading_extractor import extract_headings_from_pdf

def extract_outline(pdf_path):
    """
    Extracts the title and outline (H1, H2, H3) from the given PDF file using K-means clustering and PyMuPDF.
    Returns a dict with keys: 'title' and 'outline'.
    """
    title_info = extract_title_from_pdf(pdf_path)
    title = title_info["text"]
    outline = extract_headings_from_pdf(pdf_path)
    return {
        "title": title,
        "outline": outline
    }

def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            outline = extract_outline(pdf_path)
            out_path = os.path.join(output_dir, filename[:-4] + ".json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(outline, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main() 