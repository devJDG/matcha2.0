import fitz  # PyMuPDF
import difflib
import os
from datetime import datetime

def extract_text_with_positions(pdf_path):
    doc = fitz.open(pdf_path)
    pages_content = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        words = page.get_text("words")
        page_words = [(page_num, w[0], w[1], w[2], w[3], w[4].strip()) for w in words if w[4].strip()]
        if page_words:
            pages_content.append(page_words)
    doc.close()
    return pages_content

def compare_text_content(text_list_old, text_list_new):
   
    flat_text_old = [" ".join(word[5] for word in page) for page in text_list_old]
    flat_text_new = [" ".join(word[5] for word in page) for page in text_list_new]

    diff = difflib.unified_diff(
        flat_text_old,
        flat_text_new,
        fromfile='Old PDF',
        tofile='New PDF',
        lineterm='', 
        n=3 
    )
    diff_report = list(diff)

    return diff_report

def create_annotated_pdfs(old_pdf_path, new_pdf_path, output_folder="annotated_pdfs"):
    
    print("Extracting text from Old PDF...")
    words_old = extract_text_with_positions(old_pdf_path)
    print("Extracting text from New PDF...")
    words_new = extract_text_with_positions(new_pdf_path)

    flat_words_old = [word for page in words_old for word in page]
    flat_words_new = [word for page in words_new for word in page]

    matcher = difflib.SequenceMatcher(None,
                                      [w[5] for w in flat_words_old],
                                      [w[5] for w in flat_words_new],
                                      autojunk=False) 

    opcodes = matcher.get_opcodes()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc_old = fitz.open(old_pdf_path)
    print("Annotating Old PDF...")
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'delete' or tag == 'replace':
            for k in range(i1, i2):
                word_info = flat_words_old[k]
                page_num, x0, y0, x1, y1, _ = word_info
                page = doc_old.load_page(int(page_num))
                # Highlight deleted/replaced text in Red
                highlight = page.add_highlight_annot(fitz.Rect(x0, y0, x1, y1))
                highlight.set_colors(stroke=[1, 0, 0]) # Red
                highlight.update()

    output_old_path = os.path.join(output_folder, f"annotated_OLD_{os.path.basename(old_pdf_path)}")
    doc_old.save(output_old_path, garbage=4, deflate=True, clean=True)
    print(f"Saved annotated old PDF to: {output_old_path}")
    doc_old.close()

    doc_new = fitz.open(new_pdf_path)
    print("Annotating New PDF...")
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'insert' or tag == 'replace':
            for k in range(j1, j2):
                word_info = flat_words_new[k]
                page_num, x0, y0, x1, y1, _ = word_info
                page = doc_new.load_page(int(page_num))
                 # Highlight inserted/replaced text in Green
                highlight = page.add_highlight_annot(fitz.Rect(x0, y0, x1, y1))
                highlight.set_colors(stroke=[0, 1, 0]) # Green
                highlight.update()

    output_new_path = os.path.join(output_folder, f"annotated_NEW_{os.path.basename(new_pdf_path)}")
    doc_new.save(output_new_path, garbage=4, deflate=True, clean=True)
    print(f"Saved annotated new PDF to: {output_new_path}")
    doc_new.close()

if __name__ == "__main__":
    old_pdf = "sample_pdf/old_document.pdf" # CHANGE THIS
    new_pdf = "sample_pdf/new_document.pdf" # CHANGE THIS
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