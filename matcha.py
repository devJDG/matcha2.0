import fitz  # PyMuPDF
import difflib
import os
from datetime import datetime
from collections import Counter

def extract_text_with_positions(pdf_path):
    """
    Extracts text and its bounding box positions from a PDF document.
    Returns a list of lists, where each inner list contains (page_num, x0, y0, x1, y1, word) tuples for that page.
    """
    doc = fitz.open(pdf_path)
    pages_content = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        words = page.get_text("words")
        # Ensure words are stripped and non-empty
        page_words = [(page_num, w[0], w[1], w[2], w[3], w[4].strip()) for w in words if w[4].strip()]
        if page_words:
            pages_content.append(page_words)
    doc.close()
    return pages_content

def exempt_words_by_page_count(words_info, num_pages):
    """
    Identifies words that are repeated exactly num_pages times (case-insensitive, stripped).
    :param words_info: List of word information (page_num, x0, y0, x1, y1, word_string).
    :param num_pages: Integer, total number of pages in the document.
    :return: Set of normalized words to exempt.
    """
    normalized_words = [w[5].strip().lower() for w in words_info]
    word_counts = Counter(normalized_words)
    return {word for word, count in word_counts.items() if count == num_pages}

def create_annotated_pdfs(old_pdf_path, new_pdf_path, output_folder="annotated_pdfs"):
    """
    Compares two PDFs, identifies differences, and creates annotated versions.
    Words that appear exactly once per page in the original document are exempted
    from being highlighted.
    """
    print("Extracting text from Old PDF...")
    words_old_raw = extract_text_with_positions(old_pdf_path)
    print("Extracting text from New PDF...")
    words_new_raw = extract_text_with_positions(new_pdf_path)

    flat_words_old_raw = [word for page in words_old_raw for word in page]
    flat_words_new_raw = [word for page in words_new_raw for word in page]

    num_pages_old = len(words_old_raw)
    num_pages_new = len(words_new_raw)

    # Determine exempted words based on their count across all pages
    exempt_old = exempt_words_by_page_count(flat_words_old_raw, num_pages_old)
    exempt_new = exempt_words_by_page_count(flat_words_new_raw, num_pages_new)

    # Filter out exempted words before comparison and annotation
    # This means the difflib.SequenceMatcher will only compare non-exempt words
    words_old_filtered = [
        word_info for word_info in flat_words_old_raw
        if word_info[5].strip().lower() not in exempt_old
    ]
    words_new_filtered = [
        word_info for word_info in flat_words_new_raw
        if word_info[5].strip().lower() not in exempt_new
    ]

    # Create sequences of word strings for difflib comparison
    seq_old = [w[5] for w in words_old_filtered]
    seq_new = [w[5] for w in words_new_filtered]

    matcher = difflib.SequenceMatcher(None, seq_old, seq_new, autojunk=False)
    opcodes = matcher.get_opcodes()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # --- Annotate Old PDF ---
    doc_old = fitz.open(old_pdf_path)
    print("Annotating Old PDF...")
    for tag, i1, i2, j1, j2 in opcodes:
        # i1, i2 refer to indices in words_old_filtered
        if tag == 'delete':
            for k in range(i1, i2):
                word_info = words_old_filtered[k]
                page_num, x0, y0, x1, y1, word = word_info
                page = doc_old.load_page(int(page_num))
                highlight = page.add_highlight_annot(fitz.Rect(x0, y0, x1, y1))
                highlight.set_colors(stroke=[1, 0.65, 0.65])  # Red for deletions
                highlight.update()
        elif tag == 'replace':
            for k in range(i1, i2):
                word_info = words_old_filtered[k]
                page_num, x0, y0, x1, y1, word = word_info
                page = doc_old.load_page(int(page_num))
                highlight = page.add_highlight_annot(fitz.Rect(x0, y0, x1, y1))
                highlight.set_colors(stroke=[1, 0.83, 0.5])  # Orange for replacements (old part)
                highlight.update()

    output_old_path = os.path.join(output_folder, f"annotated_OLD_{os.path.basename(old_pdf_path)}")
    doc_old.save(output_old_path, garbage=4, deflate=True, clean=True)
    print(f"Saved annotated old PDF to: {output_old_path}")
    doc_old.close()

    # --- Annotate New PDF ---
    doc_new = fitz.open(new_pdf_path)
    print("Annotating New PDF...")
    for tag, i1, i2, j1, j2 in opcodes:
        # j1, j2 refer to indices in words_new_filtered
        if tag == 'insert':
            for k in range(j1, j2):
                word_info = words_new_filtered[k]
                page_num, x0, y0, x1, y1, word = word_info
                page = doc_new.load_page(int(page_num))
                highlight = page.add_highlight_annot(fitz.Rect(x0, y0, x1, y1))
                highlight.set_colors(stroke=[0.65, 1, 0.65])  # Green for insertions
                highlight.update()
        elif tag == 'replace':
            for k in range(j1, j2):
                word_info = words_new_filtered[k]
                page_num, x0, y0, x1, y1, word = word_info
                page = doc_new.load_page(int(page_num))
                highlight = page.add_highlight_annot(fitz.Rect(x0, y0, x1, y1))
                highlight.set_colors(stroke=[0.68, 0.85, 0.9])  # Blue for replacements (new part)
                highlight.update()

    output_new_path = os.path.join(output_folder, f"annotated_NEW_{os.path.basename(new_pdf_path)}")
    doc_new.save(output_new_path, garbage=4, deflate=True, clean=True)
    print(f"Saved annotated new PDF to: {output_new_path}")
    doc_new.close()


if __name__ == "__main__":
    old_pdf = "sample_pdf/old_document.pdf"  # CHANGE THIS
    new_pdf = "sample_pdf/new_document.pdf"  # CHANGE THIS
    output_dir = "pdf_comparison_output"

    if not os.path.exists(old_pdf):
        print(f"Error: Old PDF not found at {old_pdf}")
    elif not os.path.exists(new_pdf):
        print(f"Error: New PDF not found at {new_pdf}")
    else:
        try:
            start_time = datetime.now()
            create_annotated_pdfs(old_pdf, new_pdf, output_folder=output_dir)
            end_time = datetime.now()
            print(f"\nComparison finished in: {end_time - start_time}")
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()