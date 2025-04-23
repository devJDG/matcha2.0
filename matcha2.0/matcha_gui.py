import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import traceback
from datetime import datetime

try:
    import matcha
    import matcha_reports  # Import the new reporting module
except ImportError as e:
    messagebox.showerror("Import Error", f"Could not find required module: {e}. Make sure matcha.py and matcha_reports.py are in the same directory.")
    exit()
except Exception as e:
    messagebox.showerror("Import Error", f"An error occurred during import:\n{e}")
    exit()

# --- GUI Class ---
class PdfComparatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Comparator - Matcha")
        self.root.geometry("600x300")  # Increased height to accommodate report path

        self.old_pdf_path = tk.StringVar()
        self.new_pdf_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        self.report_dir_path = tk.StringVar()  # For the report output
        default_output = os.path.join(os.path.dirname(__file__), "pdf_comparison_output")
        default_report_output = os.path.join(os.path.dirname(__file__), "comparison_reports")
        self.output_dir_path.set(default_output)
        self.report_dir_path.set(default_report_output)

        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- Input File Paths ---
        ttk.Label(main_frame, text="Old PDF:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.old_path_label = ttk.Label(main_frame, textvariable=self.old_pdf_path, relief="sunken", padding=2)
        self.old_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.browse_old_button = ttk.Button(main_frame, text="Browse...", command=self.select_old_pdf)
        self.browse_old_button.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)

        ttk.Label(main_frame, text="New PDF:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.new_path_label = ttk.Label(main_frame, textvariable=self.new_pdf_path, relief="sunken", padding=2)
        self.new_path_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.browse_new_button = ttk.Button(main_frame, text="Browse...", command=self.select_new_pdf)
        self.browse_new_button.grid(row=1, column=2, sticky=tk.E, padx=5, pady=5)

        # --- Output Directories ---
        ttk.Label(main_frame, text="Annotated Output Dir:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_dir_label = ttk.Label(main_frame, textvariable=self.output_dir_path, relief="sunken", padding=2)
        self.output_dir_label.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.browse_output_button = ttk.Button(main_frame, text="Select...", command=self.select_output_dir)
        self.browse_output_button.grid(row=2, column=2, sticky=tk.E, padx=5, pady=5)

        ttk.Label(main_frame, text="Report Output Dir:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_dir_label = ttk.Label(main_frame, textvariable=self.report_dir_path, relief="sunken", padding=2)
        self.report_dir_label.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.browse_report_button = ttk.Button(main_frame, text="Select...", command=self.select_report_dir)
        self.browse_report_button.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)

        # --- Comparison Button and Status ---
        self.compare_button = ttk.Button(main_frame, text="Compare PDFs & Generate Report", command=self.start_comparison_thread)
        self.compare_button.grid(row=4, column=0, columnspan=3, pady=15)

        self.status_label = ttk.Label(main_frame, text="Status: Ready", anchor=tk.W, wraplength=550)
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)

    def select_old_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select Old PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            self.old_pdf_path.set(file_path)
            self.update_status("Selected Old PDF.")

    def select_new_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select New PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            self.new_pdf_path.set(file_path)
            self.update_status("Selected New PDF.")

    def select_output_dir(self):
        dir_path = filedialog.askdirectory(
            title="Select Output Directory for Annotated PDFs",
            initialdir=self.output_dir_path.get()
        )
        if dir_path:
            self.output_dir_path.set(dir_path)
            self.update_status("Selected Output Directory for Annotated PDFs.")

    def select_report_dir(self):
        dir_path = filedialog.askdirectory(
            title="Select Output Directory for Comparison Report",
            initialdir=self.report_dir_path.get()
        )
        if dir_path:
            self.report_dir_path.set(dir_path)
            self.update_status("Selected Output Directory for Comparison Report.")

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

    def set_ui_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.browse_old_button.config(state=state)
        self.browse_new_button.config(state=state)
        self.browse_output_button.config(state=state)
        self.browse_report_button.config(state=state)
        self.compare_button.config(state=state)

    def start_comparison_thread(self):
        old_pdf = self.old_pdf_path.get()
        new_pdf = self.new_pdf_path.get()
        output_dir = self.output_dir_path.get()
        report_dir = self.report_dir_path.get()

        if not old_pdf or not os.path.exists(old_pdf):
            messagebox.showerror("Error", "Old PDF file not selected or does not exist.")
            return
        if not new_pdf or not os.path.exists(new_pdf):
            messagebox.showerror("Error", "New PDF file not selected or does not exist.")
            return
        if not output_dir:
            messagebox.showerror("Error", "Output directory for annotated PDFs not selected.")
            return
        if not report_dir:
            messagebox.showerror("Error", "Output directory for comparison report not selected.")
            return

        self.set_ui_state(False)
        self.update_status("Starting comparison and report generation... This may take a moment.")

        comparison_thread = threading.Thread(
            target=self.run_comparison_worker,
            args=(old_pdf, new_pdf, output_dir, report_dir),
            daemon=True
        )
        comparison_thread.start()

    def run_comparison_worker(self, old_pdf, new_pdf, output_dir, report_dir):
        start_time = datetime.now()
        try:
            matcha.create_annotated_pdfs(old_pdf, new_pdf, output_folder=output_dir)
            matcha_reports.generate_comparison_report(old_pdf, new_pdf, output_folder=report_dir)
            end_time = datetime.now()
            duration = end_time - start_time
            self.root.after(0, self.comparison_finished, f"Comparison and report generation finished successfully in {duration}. Annotated PDFs saved to '{output_dir}', report saved to '{report_dir}'")

        except Exception as e:
            tb_str = traceback.format_exc()
            error_message = f"An error occurred during comparison or report generation: {e}\n\n{tb_str}"
            print(error_message)
            self.root.after(0, self.comparison_failed, f"Error during comparison or report generation: {e}")

    def comparison_finished(self, message):
        self.update_status(message)
        self.set_ui_state(True)
        messagebox.showinfo("Success", "PDF comparison and report generation completed successfully!")

    def comparison_failed(self, error_message):
        self.update_status(error_message)
        self.set_ui_state(True)
        messagebox.showerror("Comparison Failed", error_message)


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PdfComparatorApp(root)
    root.mainloop()
