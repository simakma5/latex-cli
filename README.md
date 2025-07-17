# LaTeX Quick Preview CLI

A lightweight, command-line tool for instantly compiling and previewing LaTeX snippets. This tool provides a simple REPL (Read-Eval-Print Loop) in your terminal, which calls the `pdflatex` compiler and displays the output in a clean, borderless pop-up window.

It's designed for quickly testing equations, formatting, or small pieces of LaTeX without the overhead of a full IDE.

-----

## Features ✨

- **Interactive CLI:** A simple and familiar command-line prompt for entering LaTeX code.
- **Instant Pop-up Preview:** Renders your code in a borderless window that appears over your terminal for quick viewing.
- **Direct PDF Rendering:** Uses the high-quality PyMuPDF library to render the PDF directly to an image in memory, with no intermediate files.
- **Copy Functionality:** Right-click the preview window to copy the underlying, extracted text to your clipboard.
- **Minimal Dependencies:** Relies only on your existing TeX distribution and a few Python packages.
- **Automatic Cleanup:** Automatically creates and deletes temporary build files (`.log`, `.aux`, etc.) in a `latex_temp` subdirectory.

-----

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Conda:** An installation of **Anaconda** or **Miniconda**.
2. **TeX Distribution:** A working LaTeX installation such as **TeX Live**, **MiKTeX**, or **MacTeX**. The `pdflatex` command must be available in your system's PATH. You can check this by opening a terminal and typing `pdflatex --version`.

-----

## Installation & Setup 🚀

Follow these steps to set up the project using `conda`.

### 1\. Create Conda Environment & Install Dependencies

Navigate to your project directory (where you have `latex_cli.py` and `requirements.txt`). You can create a new `conda` environment and install all required packages in a single step using the `requirements.txt` file.

```shell
conda create --name latex_cli --file requirements.txt
```

This command creates a new, isolated environment named **latex\_cli** and installs all the packages listed in the requirements file.

### 2\. Activate the Environment

Once the environment is created, **activate it**:

```shell
conda activate latex_cli
```

Your terminal prompt should now show `(latex_cli)` at the beginning, indicating the environment is active.

-----

## Creating the Launcher (Windows)

To run the script easily from any terminal with a simple command like `latex-cli`, you should create a PowerShell script launcher. This also ensures the script is executed correctly using the Python interpreter from your `conda` environment.

### 1\. Create the PowerShell Script (`latex-cli.ps1`)

A PowerShell script is a plain text file that contains a sequence of commands.

1. **Create a dedicated folder for your scripts.** A good practice is to create a folder like `C:\Scripts`.
2. **Find your Python interpreter's full path.** With your `conda` environment active, run the command `where python`. It will show you the path. Copy the one that points inside your `latex_cli` Conda environment folder.
3. **Create a new text file** inside `C:\Scripts` and name it `latex-cli.ps1`.
4. **Edit `latex-cli.ps1`** and add the following lines, **replacing the paths** with the full paths to your Python interpreter and your `latex_cli.py` script.

**Example:**

```shell
& "C:/Users/marti/miniconda3/envs/latex_cli/python.exe" "C:/Users/marti/repositories/latex-cli/latex_cli.py" @Args
```

### 2\. Add Your Scripts Folder to the System PATH

This final step makes your `latex-cli` command globally accessible from any terminal.

1. Press the **Windows key** and type `env`.
2. Select **"Edit the system environment variables"**.
3. In the System Properties window, click the **"Environment Variables…"** button.
4. In the top section ("User variables"), find and select the **`Path`** variable, then click **"Edit…"**.
5. Click **"New"** and add the path to the folder where you saved `latex-cli.ps1` (e.g., `C:\Scripts`).
6. Click **"OK"** on all windows to save.

-----

## Usage

1. **Important:** Close and re-open any terminal windows for the PATH changes to take effect.
2. Run the tool by simply typing `latex-cli` in the terminal and pressing Enter.
3. You will see the `>>>` prompt. Type or paste your LaTeX code. Press Enter for new lines.
4. When you are finished, type `:c` on a new line and press Enter to compile.
5. A borderless preview window will pop up.
    - **Right-click** the preview to open a context menu to **copy the text**.
    - Press the **`Esc` key** to close the preview window.
6. To exit the CLI, press `Ctrl+C`.