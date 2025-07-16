import os
import shutil
import subprocess
import sys
import textwrap

# --- Configuration ---
TEMP_DIR_NAME = "latex_temp"
TEMP_FILENAME = "_temp"
IMAGE_DPI = 200


def show_pdf_viewer():
    """Renders PDF data from stdin in a borderless Tkinter window.

    This function runs in a separate process, invoked with the '--view'
    argument. It's designed to be self-contained to avoid loading GUI
    libraries in the main CLI process.
    """
    # Imports are local to this function because it runs in a dedicated
    # process, preventing the main CLI from loading heavy GUI packages.
    import tkinter as tk

    import fitz  # PyMuPDF
    from PIL import Image, ImageTk

    pdf_bytes = sys.stdin.buffer.read()
    if not pdf_bytes:
        return

    try:
        doc = fitz.open("pdf", pdf_bytes)
        page = doc.load_page(0)

        text_content = page.get_text("text")
        pix = page.get_pixmap(dpi=IMAGE_DPI)
        doc.close()

        pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        root = tk.Tk()
        root.overrideredirect(True)

        # Use a frame to create a visual margin around the image.
        margin = 10
        frame = tk.Frame(root, background="white", padx=margin, pady=margin)
        frame.pack()

        tk_image = ImageTk.PhotoImage(pil_image)
        label = tk.Label(frame, image=tk_image, background="white", cursor="arrow")
        # Keep a reference to the image to prevent it from being garbage collected.
        label.image = tk_image
        label.pack()

        def copy_to_clipboard():
            """Copies the extracted text content to the system clipboard."""
            root.clipboard_clear()
            root.clipboard_append(text_content)

        def close_viewer(event=None):
            """Closes the viewer window."""
            root.destroy()

        context_menu = tk.Menu(root, tearoff=0)
        context_menu.add_command(label="Copy Text", command=copy_to_clipboard)
        context_menu.add_separator()
        context_menu.add_command(label="Close", command=close_viewer)

        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)

        # Bind events
        frame.bind("<Button-3>", show_context_menu)
        label.bind("<Button-3>", show_context_menu)
        root.bind("<Escape>", close_viewer)

        # Center the window on the screen
        root.update_idletasks()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        win_w = root.winfo_width()
        win_h = root.winfo_height()
        x = (screen_w // 2) - (win_w // 2)
        y = (screen_h // 2) - (win_h // 2)
        root.geometry(f"{win_w}x{win_h}+{x}+{y}")

        root.mainloop()

    except Exception:
        # Silently fail in the viewer process to avoid crashing the main CLI.
        pass


def run_latex_compiler(code_snippet):
    """Compiles a LaTeX snippet and pipes the resulting PDF to the viewer process."""
    latex_template = f"""
    \\documentclass[preview, border=5pt]{{standalone}}
    \\usepackage{{amsmath}}
    \\usepackage{{amssymb}}
    \\usepackage{{graphicx}}
    \\usepackage{{xcolor}}
    \\begin{{document}}
    {code_snippet}
    \\end{{document}}
    """
    full_latex_code = textwrap.dedent(latex_template)

    temp_dir = os.path.join(os.getcwd(), TEMP_DIR_NAME)
    os.makedirs(temp_dir, exist_ok=True)

    base_path = os.path.join(temp_dir, TEMP_FILENAME)
    tex_path = f"{base_path}.tex"
    pdf_path = f"{base_path}.pdf"

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(full_latex_code)

    print("Compiling...")

    # Suppress the console window on Windows when calling pdflatex.
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW

    process = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", f"-output-directory={temp_dir}", tex_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        creationflags=creation_flags,
    )

    if process.returncode != 0:
        print("\n--- LaTeX Compilation Error ---")
        log_lines = process.stdout.splitlines()
        error_snippet = "An unknown error occurred. Check the .log file."
        for i, line in enumerate(log_lines):
            if line.startswith("!"):
                error_snippet = "\n".join(log_lines[i : i + 5])
                break
        print(error_snippet)
    else:
        print("Compilation successful! Displaying preview...")
        try:
            if not os.path.exists(pdf_path):
                print("Error: PDF file was not created by the compiler.")
                return

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            # Launch the viewer part of this script in a new process,
            # piping the PDF data directly to its standard input.
            viewer_process = subprocess.Popen(
                [sys.executable, __file__, "--view"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags,
            )
            viewer_process.stdin.write(pdf_bytes)
            viewer_process.stdin.close()
        except Exception as e:
            print(f"\n--- Preview Generation Error ---\n{e}")

    # The PDF data is now in the viewer's memory, so we can clean up build files.
    for ext in [".tex", ".aux", ".log", ".pdf"]:
        try:
            filepath = f"{base_path}{ext}"
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError:
            pass


def main_cli_loop():
    """Runs the main interactive command-line loop for user input."""
    print("--- LaTeX Live Preview CLI ---")
    print("Type your LaTeX code. Enter ':c' on a new line to compile.")
    print("Press Ctrl+C to exit.")

    lines = []
    while True:
        try:
            prompt = ">>> " if not lines else "... "
            print(prompt, end="", flush=True)
            line = sys.stdin.readline()

            if not line:  # Catches EOF (Ctrl+D on Unix)
                raise EOFError

            if line.strip().lower() == ":c":
                if not lines:
                    print("No code to compile.")
                    continue
                run_latex_compiler("\n".join(lines))
                lines = []
            else:
                # readline() includes a newline, strip it.
                lines.append(line.rstrip("\n"))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            temp_dir = os.path.join(os.getcwd(), TEMP_DIR_NAME)
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            break


if __name__ == "__main__":
    # This script is dual-purpose: it runs the CLI by default, but acts
    # as a PDF viewer if called with the '--view' argument. This avoids
    # mixing the CLI logic with the GUI display logic in the same process.
    if len(sys.argv) > 1 and sys.argv[1] == "--view":
        show_pdf_viewer()
    else:
        main_cli_loop()
