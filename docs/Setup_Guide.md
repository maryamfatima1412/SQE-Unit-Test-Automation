# Setup Guide (Task 1)

## Project selected
Python project: **Student Portal - Attendance & Result Management System** (`student_portal.py`, Tkinter + JSON storage), the same
application that was tested manually in Assignment 2. It is our own project; the code is public in the group repository.

## Steps

### 1. Install the tools
* Python 3.10 or newer (3.12 used): https://www.python.org/downloads/ (tick "Add python to PATH" on Windows).
* Git: https://git-scm.com/downloads
* tkinter comes with Python on Windows/macOS. Ubuntu/Debian: `sudo apt install python3-tk python3-venv`.

Check: `python --version`, `git --version`, `python -c "import tkinter"` (no error).

### 2. Get the code
```bash
git clone <repo-url>
cd SQE-Unit-Test-Automation
```

### 3. Create the virtual environment
```bash
python -m venv venv                 # Ubuntu: python3 -m venv --system-site-packages venv
venv\Scripts\activate               # Windows
source venv/bin/activate            # Linux / macOS
```

### 4. Install the requirements
```bash
pip install -r requirements.txt
```
Installs pytest, pytest-xdist (parallel runs), pytest-cov (coverage) and openpyxl (reads the Excel file).

### 5. Verify the setup
```bash
python run_tests.py smoke
python run_tests.py all
python run_tests.py parallel
python run_tests.py coverage
```
Expected: `160 passed, 6 xfailed` for `all` and `parallel`. (The 6 xfailed tests are known defects and are expected.)

### 6. (Optional) Run the application
```bash
python src/student_portal.py
```
Logins are in the Assignment 2 report. The application creates `portal_data.json` in the folder it is started from (ignored by Git; the tests never touch it).

## Common problems
| Problem | Fix |
|---|---|
| `ModuleNotFoundError: tkinter` | install `python3-tk` (Ubuntu) / reinstall Python with tcl/tk (Windows) |
| `pytest` not found | activate the venv, then `pip install -r requirements.txt` |
| `Unit_Test_Cases.xlsx not found` | run `python tools/generate_excel.py` |
| `unrecognized arguments: -n` | `pip install pytest-xdist` |
