import os
from datetime import datetime
from collections import Counter
import difflib

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Assuming extract_text_with_positions and exempt_words_by_page_count are in a module named 'matcha'
# If they are in the same file, you don't need the 'from matcha import' line.
# For this refactoring, I'll include them directly to make the example self-contained.

import fitz  # PyMuPDF

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


def generate_comparison_report(old_pdf_path, new_pdf_path, output_folder="comparison_reports"):
    """
    Generates a PDF report summarizing the differences between two PDF documents,
    excluding words that appear on every page (exempted words).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_name_old = os.path.splitext(os.path.basename(old_pdf_path))[0]
    base_name_new = os.path.splitext(os.path.basename(new_pdf_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join(output_folder, f"ComparisonReport_{base_name_old}_vs_{base_name_new}_{timestamp}.pdf")

    doc = SimpleDocTemplate(report_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # --- Report Title ---
    title = Paragraph(f"PDF Comparison Report: {base_name_old} vs {base_name_new}", styles['h1'])
    story.append(title)
    story.append(Spacer(1, 0.2*inch))

    # --- Extract and Filter Text Content ---
    print("Extracting text for report...")
    words_old_raw = extract_text_with_positions(old_pdf_path)
    words_new_raw = extract_text_with_positions(new_pdf_path)

    flat_words_old_raw = [word for page in words_old_raw for word in page]
    flat_words_new_raw = [word for page in words_new_raw for word in page]

    num_pages_old = len(words_old_raw)
    num_pages_new = len(words_new_raw)

    # Determine exempted words based on their count across all pages
    exempt_old = exempt_words_by_page_count(flat_words_old_raw, num_pages_old)
    exempt_new = exempt_words_by_page_count(flat_words_new_raw, num_pages_new)

    # Filter out exempted words before comparison
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

    # --- Perform Detailed Comparison ---
    matcher = difflib.SequenceMatcher(None, seq_old, seq_new, autojunk=False)
    opcodes = matcher.get_opcodes()

    added_count = 0
    removed_count = 0
    replaced_count_old = 0
    replaced_count_new = 0

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'insert':
            added_count += (j2 - j1)
        elif tag == 'delete':
            removed_count += (i2 - i1)
        elif tag == 'replace':
            replaced_count_old += (i2 - i1)
            replaced_count_new += (j2 - j1)

    total_old_words_filtered = len(words_old_filtered)
    total_new_words_filtered = len(words_new_filtered)

    added_percentage = (added_count / total_new_words_filtered * 100) if total_new_words_filtered > 0 else 0
    removed_percentage = (removed_count / total_old_words_filtered * 100) if total_old_words_filtered > 0 else 0
    
    # For replaced, consider the larger count of words involved in replacement
    replaced_percentage = (max(replaced_count_old, replaced_count_new) / max(total_old_words_filtered, total_new_words_filtered) * 100) if max(total_old_words_filtered, total_new_words_filtered) > 0 else 0

    # --- Build Report Content ---
    story.append(Paragraph(f"Date of Report: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(f"<b>Summary of Changes (Excluding Exempted Words):</b>", styles['h2']))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph(f"Total non-exempt words in Old PDF: {total_old_words_filtered}", styles['Normal']))
    story.append(Paragraph(f"Total non-exempt words in New PDF: {total_new_words_filtered}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph(f"Newly Added Words: {added_count} ({added_percentage:.2f}%)", styles['Normal']))
    story.append(Paragraph(f"Removed Words: {removed_count} ({removed_percentage:.2f}%)", styles['Normal']))
    story.append(Paragraph(f"Replaced Words (estimated): {max(replaced_count_old, replaced_count_new)} ({replaced_percentage:.2f}%)", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(f"<i>Note: Words appearing on every page of a document have been exempted from this comparison to focus on substantive changes.</i>", styles['Small']))

    # --- Build and Save Report ---
    doc.build(story)
    print(f"Generated comparison report: {report_filename}")