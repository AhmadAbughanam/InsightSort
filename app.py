import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from tkinter import font as tkFont
import os
import threading
from datetime import datetime
import sys


from file_handler import (
    extract_text_from_file,
    move_file_to_topic_folder,
    scan_directory_for_files,
    log_to_report,
    remove_from_report_csv,
)
from llm_classifier import classify_with_llm
from rule_based_classifier import classify_rule_based
from extractor import (
    extract_keywords_llm,
    extract_keywords_tfidf,
    summarize_llm,
    summarize_rule_based,
)
from memory_store import store_file_metadata
from utils import is_supported_file
import yaml

# ------------------ Load Config ------------------
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    USE_LLM = config["classifier"]["use_llm_first"]
    FALLBACK_ENABLED = config["classifier"]["fallback_to_rule"]
    EXTRACT_LLM_MODE = config["extractor"]["llm_mode"]
except FileNotFoundError:
    messagebox.showerror("Config Error", "config.yaml not found!")
    sys.exit(1)

# ------------------ Enhanced GUI App ------------------


class ModernButton(tk.Button):
    """Custom modern button with hover effects"""

    def __init__(self, parent, **kwargs):
        # Extract custom colors
        self.bg_color = kwargs.pop("bg_color", "#4A90E2")
        self.hover_color = kwargs.pop("hover_color", "#357ABD")
        self.text_color = kwargs.pop("text_color", "white")

        super().__init__(
            parent,
            bg=self.bg_color,
            fg=self.text_color,
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            **kwargs,
        )

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _on_hover(self, event):
        self.config(bg=self.hover_color)

    def _on_leave(self, event):
        self.config(bg=self.bg_color)


class ProgressFrame(tk.Frame):
    """Custom progress frame with modern styling"""

    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa")

        self.progress_var = tk.StringVar(value="Ready to process files...")
        self.progress_label = tk.Label(
            self,
            textvariable=self.progress_var,
            bg="#f8f9fa",
            fg="#6c757d",
            font=("Segoe UI", 9),
        )
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(
            self, mode="determinate", style="Modern.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", padx=20, pady=2)

    def update_progress(self, current, total, message="Processing..."):
        progress = (current / total) * 100 if total > 0 else 0
        self.progress_bar["value"] = progress
        self.progress_var.set(f"{message} ({current}/{total})")
        self.update_idletasks()

    def reset(self):
        self.progress_bar["value"] = 0
        self.progress_var.set("Ready to process files...")


class StatsFrame(tk.Frame):
    """Statistics display frame"""

    def __init__(self, parent):
        super().__init__(parent, bg="white", relief="solid", bd=1)

        # Title
        title = tk.Label(
            self,
            text="📊 Session Statistics",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 12, "bold"),
        )
        title.pack(pady=(10, 5))

        # Stats container
        stats_container = tk.Frame(self, bg="white")
        stats_container.pack(fill="x", padx=10, pady=5)

        # Individual stat items
        self.files_processed = self._create_stat_item(
            stats_container, "Files Processed", "0", 0
        )
        self.success_rate = self._create_stat_item(
            stats_container, "Success Rate", "0%", 1
        )
        self.avg_time = self._create_stat_item(
            stats_container, "Avg Time/File", "0s", 2
        )

        self.reset_stats()

    def _create_stat_item(self, parent, label, initial_value, column):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=0, column=column, padx=10, pady=5, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)

        value_label = tk.Label(
            frame,
            text=initial_value,
            bg="white",
            fg="#4A90E2",
            font=("Segoe UI", 14, "bold"),
        )
        value_label.pack()

        desc_label = tk.Label(
            frame, text=label, bg="white", fg="#6c757d", font=("Segoe UI", 8)
        )
        desc_label.pack()

        return value_label

    def update_stats(self, processed, successful, avg_time):
        self.files_processed.config(text=str(processed))
        success_rate = (successful / processed * 100) if processed > 0 else 0
        self.success_rate.config(text=f"{success_rate:.1f}%")
        self.avg_time.config(text=f"{avg_time:.1f}s")

    def reset_stats(self):
        self.files_processed.config(text="0")
        self.success_rate.config(text="0%")
        self.avg_time.config(text="0s")


class InsightSortApp:
    def __init__(self, master):
        self.master = master
        self.setup_window()
        self.setup_styles()
        self.create_widgets()

        # Data
        self.files = []
        self.processing = False
        self.stats = {"processed": 0, "successful": 0, "total_time": 0}

    def setup_window(self):
        """Configure main window"""
        self.master.title("InsightSort - Intelligent Document Classifier")
        self.master.geometry("1000x800")
        self.master.minsize(800, 600)
        self.master.configure(bg="#f8f9fa")

        # Center window
        self.master.update_idletasks()
        x = (self.master.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.master.winfo_screenheight() // 2) - (800 // 2)
        self.master.geometry(f"1000x800+{x}+{y}")

        # Set icon (if available)
        try:
            self.master.iconbitmap("icon.ico")
        except:
            pass

    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure progressbar style
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background="#4A90E2",
            troughcolor="#e9ecef",
            borderwidth=0,
            lightcolor="#4A90E2",
            darkcolor="#4A90E2",
        )

    def create_widgets(self):
        """Create and layout all widgets"""
        main_container = tk.Frame(self.master, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        self.create_header(main_container)

        # Main content area
        content_frame = tk.Frame(main_container, bg="#f8f9fa")
        content_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Left panel (controls)
        left_panel = tk.Frame(content_frame, bg="white", relief="solid", bd=1)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        # Right panel (results)
        right_panel = tk.Frame(content_frame, bg="white", relief="solid", bd=1)
        right_panel.pack(side="right", fill="both", expand=True)

        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)

    def create_header(self, parent):
        """Create application header"""
        header_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        header_frame.pack(fill="x", pady=(0, 10))

        # Title section
        title_frame = tk.Frame(header_frame, bg="white")
        title_frame.pack(fill="x", padx=20, pady=15)

        # App icon and title
        title_container = tk.Frame(title_frame, bg="white")
        title_container.pack(side="left")

        app_title = tk.Label(
            title_container,
            text="🧠 InsightSort",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 20, "bold"),
        )
        app_title.pack(side="left")

        subtitle = tk.Label(
            title_container,
            text="Intelligent Document Classification & Organization",
            bg="white",
            fg="#6c757d",
            font=("Segoe UI", 11),
        )
        subtitle.pack(side="left", padx=(10, 0))

        # Config info
        config_frame = tk.Frame(title_frame, bg="white")
        config_frame.pack(side="right")

        mode_text = "🤖 AI Mode" if USE_LLM else "📋 Rule-based Mode"
        mode_label = tk.Label(
            config_frame,
            text=mode_text,
            bg="white",
            fg="#28a745" if USE_LLM else "#ffc107",
            font=("Segoe UI", 10, "bold"),
        )
        mode_label.pack()

        # Statistics
        self.stats_frame = StatsFrame(header_frame)
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 15))

    def create_left_panel(self, parent):
        """Create left control panel"""
        # Panel title
        panel_title = tk.Label(
            parent,
            text="📁 File Management",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 14, "bold"),
        )
        panel_title.pack(pady=(20, 15), anchor="w", padx=20)

        # File list section
        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        tk.Label(
            list_frame,
            text="📄 Selected Files:",
            bg="white",
            fg="#495057",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        # Files listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg="white")
        listbox_frame.pack(fill="both", expand=True)

        self.files_listbox = tk.Listbox(
            listbox_frame,
            height=8,
            bg="#f8f9fa",
            fg="#495057",
            font=("Consolas", 9),
            relief="solid",
            bd=1,
            selectmode="extended",
        )

        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.files_listbox.yview)

        self.files_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # File count
        self.file_count_var = tk.StringVar(value="0 files selected")
        file_count_label = tk.Label(
            list_frame,
            textvariable=self.file_count_var,
            bg="white",
            fg="#6c757d",
            font=("Segoe UI", 9),
        )
        file_count_label.pack(anchor="w", pady=(5, 0))

        # Buttons section
        buttons_frame = tk.Frame(parent, bg="white")
        buttons_frame.pack(fill="x", padx=20, pady=(10, 20))

        # Upload buttons
        self.upload_files_btn = ModernButton(
            buttons_frame,
            text="📂 Add Files",
            command=self.upload_files,
            bg_color="#4A90E2",
            hover_color="#357ABD",
        )
        self.upload_files_btn.pack(fill="x", pady=(0, 8))

        self.upload_folder_btn = ModernButton(
            buttons_frame,
            text="📁 Add Folder",
            command=self.upload_folder,
            bg_color="#17a2b8",
            hover_color="#138496",
        )
        self.upload_folder_btn.pack(fill="x", pady=(0, 8))

        # Clear button
        self.clear_btn = ModernButton(
            buttons_frame,
            text="🗑️ Clear List",
            command=self.clear_files,
            bg_color="#dc3545",
            hover_color="#c82333",
        )
        self.clear_btn.pack(fill="x", pady=(0, 15))

        # Process button
        self.process_btn = ModernButton(
            buttons_frame,
            text="⚡ Analyze & Organize",
            command=self.start_processing,
            bg_color="#28a745",
            hover_color="#218838",
        )
        self.process_btn.pack(fill="x", pady=(0, 8))

        # Delete from output button
        self.delete_btn = ModernButton(
            buttons_frame,
            text="🗑️ Delete from Output",
            command=self.delete_from_output,
            bg_color="#ffc107",
            hover_color="#e0a800",
            text_color="#212529",
        )
        self.delete_btn.pack(fill="x")

    def create_right_panel(self, parent):
        """Create right results panel"""
        # Panel title
        results_header = tk.Frame(parent, bg="white")
        results_header.pack(fill="x", padx=20, pady=(20, 10))

        panel_title = tk.Label(
            results_header,
            text="📊 Processing Results",
            bg="white",
            fg="#2c3e50",
            font=("Segoe UI", 14, "bold"),
        )
        panel_title.pack(side="left")

        # Clear results button
        clear_results_btn = tk.Button(
            results_header,
            text="🧹 Clear",
            command=self.clear_results,
            bg="#6c757d",
            fg="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Segoe UI", 8),
        )
        clear_results_btn.pack(side="right")

        # Progress section
        self.progress_frame = ProgressFrame(parent)
        self.progress_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Results text area
        results_frame = tk.Frame(parent, bg="white")
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.result_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            bg="#f8f9fa",
            fg="#495057",
            font=("Consolas", 10),
            relief="solid",
            bd=1,
            padx=10,
            pady=10,
        )
        self.result_text.pack(fill="both", expand=True)

        # Configure text tags for colored output
        self.result_text.tag_configure(
            "success", foreground="#28a745", font=("Consolas", 10, "bold")
        )
        self.result_text.tag_configure(
            "error", foreground="#dc3545", font=("Consolas", 10, "bold")
        )
        self.result_text.tag_configure(
            "info", foreground="#17a2b8", font=("Consolas", 10, "bold")
        )
        self.result_text.tag_configure(
            "warning", foreground="#ffc107", font=("Consolas", 10, "bold")
        )
        self.result_text.tag_configure(
            "header", foreground="#2c3e50", font=("Consolas", 12, "bold")
        )

        # Initial welcome message
        self.show_welcome_message()

    def show_welcome_message(self):
        """Display welcome message in results area"""
        welcome_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🧠 INSIGHTSORT READY                                        ║
╚════════════════════════════════════════════════════════════════════════════════╝

Welcome to InsightSort - Your Intelligent Document Classifier!

🔧 Current Configuration:
   • Classification: {"AI-Powered (LLM)" if USE_LLM else "Rule-based"}
   • Fallback: {"Enabled" if FALLBACK_ENABLED else "Disabled"}
   • Extraction: {"AI-Powered (LLM)" if EXTRACT_LLM_MODE else "Traditional (TF-IDF)"}

📋 How to get started:
   1. Click "📂 Add Files" or "📁 Add Folder" to select documents
   2. Review your file selection in the left panel
   3. Click "⚡ Analyze & Organize" to process your documents
   4. Watch the magic happen in real-time!

💡 Supported formats: PDF, DOC, DOCX, TXT, and more...

Ready to organize your documents intelligently? Let's begin! 🚀
        """

        self.result_text.insert("1.0", welcome_text)
        self.result_text.tag_add("header", "2.0", "2.end")
        self.result_text.tag_add("info", "4.0", "10.end")

    def upload_files(self):
        """Handle file upload"""
        filetypes = [
            ("All Supported", "*.pdf;*.doc;*.docx;*.txt;*.rtf"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.doc;*.docx"),
            ("Text files", "*.txt;*.rtf"),
            ("All files", "*.*"),
        ]

        selected = filedialog.askopenfilenames(
            title="Select Files to Process", filetypes=filetypes
        )

        added_count = 0
        for file_path in selected:
            if is_supported_file(file_path) and file_path not in self.files:
                self.files.append(file_path)
                self.files_listbox.insert("end", os.path.basename(file_path))
                added_count += 1

        self.update_file_count()

        if added_count > 0:
            self.log_message(
                f"✅ Added {added_count} file(s) to processing queue", "success"
            )
        else:
            self.log_message("⚠️ No new supported files were added", "warning")

    def upload_folder(self):
        """Handle folder upload"""
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if not folder:
            return

        self.log_message(f"🔍 Scanning folder: {folder}", "info")
        scanned = scan_directory_for_files(folder)

        added_count = 0
        for file_path in scanned:
            if file_path not in self.files:
                self.files.append(file_path)
                self.files_listbox.insert("end", os.path.basename(file_path))
                added_count += 1

        self.update_file_count()
        self.log_message(f"✅ Added {added_count} file(s) from folder scan", "success")

    def clear_files(self):
        """Clear file list"""
        if not self.files:
            return

        result = messagebox.askyesno(
            "Clear Files",
            f"Are you sure you want to clear all {len(self.files)} selected files?",
        )

        if result:
            self.files.clear()
            self.files_listbox.delete(0, "end")
            self.update_file_count()
            self.log_message("🧹 File list cleared", "info")

    def update_file_count(self):
        """Update file count display"""
        count = len(self.files)
        self.file_count_var.set(f"{count} file{'s' if count != 1 else ''} selected")

    def start_processing(self):
        """Start file processing in separate thread"""
        if not self.files:
            messagebox.showwarning("No Files", "Please add files to process first.")
            return

        if self.processing:
            messagebox.showinfo("Processing", "Files are already being processed.")
            return

        # Disable buttons during processing
        self.set_processing_state(True)

        # Start processing in separate thread
        processing_thread = threading.Thread(target=self.process_files)
        processing_thread.daemon = True
        processing_thread.start()

    def set_processing_state(self, processing):
        """Enable/disable buttons during processing"""
        self.processing = processing
        state = "disabled" if processing else "normal"

        self.upload_files_btn.config(state=state)
        self.upload_folder_btn.config(state=state)
        self.clear_btn.config(state=state)
        self.process_btn.config(state=state)
        self.delete_btn.config(state=state)

        if processing:
            self.process_btn.config(text="⏳ Processing...")
        else:
            self.process_btn.config(text="⚡ Analyze & Organize")

    def process_files(self):
        """Process all files with progress tracking"""
        start_time = datetime.now()
        total_files = len(self.files)
        successful = 0

        try:
            self.log_message(
                f"\n🚀 Starting batch processing of {total_files} files...", "header"
            )
            self.log_message(
                f"📅 Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}", "info"
            )

            for i, file_path in enumerate(self.files, 1):
                file_start_time = datetime.now()

                try:
                    # Update progress
                    self.master.after(
                        0,
                        lambda: self.progress_frame.update_progress(
                            i - 1,
                            total_files,
                            f"Processing {os.path.basename(file_path)}",
                        ),
                    )

                    self.master.after(
                        0,
                        lambda fp=file_path: self.log_message(
                            f"\n📄 [{i}/{total_files}] Processing: {os.path.basename(fp)}",
                            "info",
                        ),
                    )

                    # Step 1: Extract text
                    text = extract_text_from_file(file_path)

                    # Step 2: Classify
                    topic = None
                    if USE_LLM:
                        topic = classify_with_llm(text)
                        if topic == "Misc" and FALLBACK_ENABLED:
                            topic = classify_rule_based(text)
                    else:
                        topic = classify_rule_based(text)

                    # Step 3: Extract keywords and summary
                    if EXTRACT_LLM_MODE:
                        keywords = extract_keywords_llm(text)
                        summary = summarize_llm(text)
                    else:
                        keywords = extract_keywords_tfidf(text)
                        summary = summarize_rule_based(text)

                    # Step 4: Organize file
                    move_file_to_topic_folder(file_path, topic)

                    # Step 5: Store + log
                    store_file_metadata(
                        os.path.basename(file_path), topic, keywords, summary
                    )
                    log_to_report(file_path, topic, keywords, summary)

                    # Calculate processing time
                    processing_time = (datetime.now() - file_start_time).total_seconds()

                    # Step 6: Show results
                    self.master.after(
                        0,
                        lambda t=topic, k=keywords, s=summary, pt=processing_time: self.display_file_results(
                            t, k, s, pt
                        ),
                    )

                    successful += 1

                except Exception as e:
                    self.master.after(
                        0,
                        lambda fp=file_path, err=str(e): self.log_message(
                            f"❌ Error processing {os.path.basename(fp)}: {err}",
                            "error",
                        ),
                    )

                # Update progress
                self.master.after(
                    0,
                    lambda: self.progress_frame.update_progress(
                        i, total_files, "Processing complete"
                    ),
                )

            # Final summary
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            avg_time = total_time / total_files if total_files > 0 else 0

            self.master.after(
                0,
                lambda: self.display_final_summary(
                    total_files, successful, total_time, avg_time
                ),
            )

        finally:
            # Reset UI state
            self.master.after(0, lambda: self.set_processing_state(False))
            self.master.after(0, lambda: self.files.clear())
            self.master.after(0, lambda: self.files_listbox.delete(0, "end"))
            self.master.after(0, lambda: self.update_file_count())
            self.master.after(0, lambda: self.progress_frame.reset())

    def display_file_results(self, topic, keywords, summary, processing_time):
        """Display results for a single file"""
        self.log_message(f"   ✅ Topic: {topic}", "success")
        self.log_message(
            f"   🔑 Keywords: {', '.join(keywords[:5])}", "info"
        )  # Show first 5 keywords
        self.log_message(
            f"   📝 Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}",
            "info",
        )
        self.log_message(f"   ⏱️  Processing time: {processing_time:.2f}s", "info")
        self.log_message("   " + "─" * 50, "info")

    def display_final_summary(self, total, successful, total_time, avg_time):
        """Display final processing summary"""
        success_rate = (successful / total * 100) if total > 0 else 0

        summary_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 PROCESSING COMPLETE                  ║
╚══════════════════════════════════════════════════════════════╝


📊 Final Statistics:
   • Total Files: {total}
   • Successfully Processed: {successful}
   • Success Rate: {success_rate:.1f}%
   • Total Time: {total_time:.2f} seconds
   • Average Time per File: {avg_time:.2f} seconds

All files have been organized into topic folders! 🎯
        """

        self.log_message(summary_text, "header")

        # Update stats display
        self.stats_frame.update_stats(total, successful, avg_time)

    def delete_from_output(self):
        """Delete files from output directory"""
        output_dir = "output/organized"
        if not os.path.exists(output_dir):
            messagebox.showwarning("No Output", "No organized files found to delete.")
            return

        choice = filedialog.askopenfilename(
            initialdir=output_dir, title="Select File to Delete"
        )

        if not choice:
            return

        try:
            from memory_store import delete_file_metadata
            from file_handler import remove_from_report_csv  # 👈

            if os.path.isfile(choice):
                filename = os.path.basename(choice)
                os.remove(choice)
                delete_file_metadata(filename)
                remove_from_report_csv(filename)  # 👈

                # Clean up empty folder
                parent = os.path.dirname(choice)
                try:
                    if len(os.listdir(parent)) == 0:
                        os.rmdir(parent)
                except:
                    pass

                self.log_message(f"🗑️ Deleted file: {filename}", "warning")
                messagebox.showinfo("Deleted", f"Successfully deleted: {filename}")

        except Exception as e:
            self.log_message(f"❌ Error deleting file: {e}", "error")
            messagebox.showerror("Error", f"Failed to delete file: {e}")

    def clear_results(self):
        """Clear results text area"""
        self.result_text.delete("1.0", "end")
        self.show_welcome_message()
        self.stats_frame.reset_stats()

    def log_message(self, message, tag="info"):
        """Add message to results text with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.result_text.insert("end", formatted_message)

        # Apply tag to the new message
        start_line = self.result_text.index("end-2c linestart")
        end_line = self.result_text.index("end-1c")
        self.result_text.tag_add(tag, start_line, end_line)

        # Auto-scroll to bottom
        self.result_text.see("end")
        self.result_text.update_idletasks()


# ------------------ Application Entry Point ------------------


def main():
    """Main application entry point with error handling"""
    try:
        root = tk.Tk()

        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit InsightSort?"):
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Create and run app
        app = InsightSortApp(root)

        # Add keyboard shortcuts
        root.bind("<Control-o>", lambda e: app.upload_files())
        root.bind("<Control-f>", lambda e: app.upload_folder())
        root.bind("<Control-r>", lambda e: app.start_processing())
        root.bind("<Control-l>", lambda e: app.clear_results())
        root.bind("<F5>", lambda e: app.start_processing())

        # Show keyboard shortcuts in title
        root.title(
            "InsightSort - Intelligent Document Classifier (Ctrl+O: Files, Ctrl+F: Folder, F5: Process)"
        )

        root.mainloop()

    except Exception as e:
        messagebox.showerror(
            "Application Error", f"Failed to start InsightSort:\n{str(e)}"
        )
        sys.exit(1)


# ------------------ Launch Application ------------------

if __name__ == "__main__":
    main()
