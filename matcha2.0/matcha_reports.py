from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
from datetime import datetime  # Add this line
import difflib
from matcha import extract_text_with_positions # Make sure this import works correctly

def generate_comparison_report(old_pdf_path, new_pdf_path, output_folder="comparison_reports"):
    """
    Generates a PDF report summarizing the differences between two PDF files.

    Args:
        old_pdf_path (str): Path to the old PDF file.
        new_pdf_path (str): Path to the new PDF file.
        output_folder (str, optional): Folder to save the report. Defaults to "comparison_reports".
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

    title = Paragraph(f"PDF Comparison Report: {base_name_old} vs {base_name_new}", styles['h1'])
    story.append(title)
    story.append(Spacer(1, 0.2*inch))

    # --- Extract Text Content ---
    print("Extracting text for report...")
    words_old = extract_text_with_positions(old_pdf_path)
    words_new = extract_text_with_positions(new_pdf_path)

    flat_words_old = [word[5] for page in words_old for word in page]
    flat_words_new = [word[5] for page in words_new for word in page]

    # --- Perform Detailed Comparison ---
    matcher = difflib.SequenceMatcher(None, flat_words_old, flat_words_new, autojunk=False)
    opcodes = matcher.get_opcodes()

    added_count = 0
    removed_count = 0
    replaced_count = 0

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'insert':
            added_count += (j2 - j1)
        elif tag == 'delete':
            removed_count += (i2 - i1)
        elif tag == 'replace':
            replaced_count += min(i2 - i1, j2 - j1) # Consider the shorter segment for word count

    total_old_words = len(flat_words_old)
    total_new_words = len(flat_words_new)

    added_percentage = (added_count / total_new_words * 100) if total_new_words > 0 else 0
    removed_percentage = (removed_count / total_old_words * 100) if total_old_words > 0 else 0
    replaced_percentage = (replaced_count / max(total_old_words, total_new_words) * 100) if max(total_old_words, total_new_words) > 0 else 0


    # --- Build Report Content ---
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(f"<b>Summary of Changes:</b>", styles['h2']))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph(f"Total words in Old PDF: {total_old_words}", styles['Normal']))
    story.append(Paragraph(f"Total words in New PDF: {total_new_words}", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph(f"Newly Added Words: {added_count} ({added_percentage:.2f}%)", styles['Normal']))
    story.append(Paragraph(f"Removed Words: {removed_count} ({removed_percentage:.2f}%)", styles['Normal']))
    story.append(Paragraph(f"Replaced Words (estimated): {replaced_count} ({replaced_percentage:.2f}%)", styles['Normal']))

    doc.build(story)
    print(f"Generated comparison report: {report_filename}")

if __name__ == "__main__":
    from your_main_script import extract_text_with_positions # Import the function

    old_pdf = "sample_pdf/old_document.pdf" # CHANGE THIS
    new_pdf = "sample_pdf/new_document.pdf" # CHANGE THIS
    output_dir = "comparison_reports"

    if not os.path.exists(old_pdf):
        print(f"Error: Old PDF not found at {old_pdf}")
    elif not os.path.exists(new_pdf):
        print(f"Error: New PDF not found at {new_pdf}")
    else:
        try:
            start_time = datetime.now()
            generate_comparison_report(old_pdf, new_pdf, output_folder=output_dir)
            end_time = datetime.now()
            print(f"\nReport generation finished in: {end_time - start_time}")
        except Exception as e:
            print(f"An error occurred during report generation: {e}")
            import traceback
            traceback.print_exc()