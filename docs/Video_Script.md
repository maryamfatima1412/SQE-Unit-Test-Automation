# Setup Video - Script (about 3-4 minutes)

Record your screen with any recorder (Windows: Xbox Game Bar `Win+G`, or OBS). Save it as `docs/video/setup_video.mp4` (or put a
link in `docs/video/README.md` if the file is too big for Git, e.g. >100 MB - GitHub's limit). Say your names at the start.

| Time | Show on screen | Say (English or Urdu mix is fine) |
|---|---|---|
| 0:00 | Title / GitHub repo page | "Assalam o alaikum, we are Maryam Fatima (24F-3044) and Huda Asif (24F-3111). This is our SQE Assignment 3 - unit test automation of the Student Portal project." |
| 0:20 | Terminal: `python --version`, `git --version` | "Python and Git are installed." |
| 0:40 | `git clone <repo-url>` then `cd` | "First we clone the repository." |
| 1:10 | Create + activate venv | "We create a virtual environment so the packages stay separate." |
| 1:40 | `pip install -r requirements.txt` | "Pytest, xdist, cov and openpyxl are installed." |
| 2:10 | `python run_tests.py smoke` | "Smoke suite runs first." |
| 2:30 | `python run_tests.py all` -> `160 passed, 6 xfailed` | "All tests pass; the 6 xfailed tests are known defects." |
| 3:00 | `python run_tests.py parallel` | "Same tests in parallel with xdist." |
| 3:20 | Open `htmlcov/index.html` after `python run_tests.py coverage` (optional) | "Coverage report." |
| 3:40 | Folder tree in the editor | "Tests, data, docs and the Excel sheet are in the repo. Thank you." |

Tips: use a large terminal font; do the steps on a clean folder so the full setup is visible; if a step is slow, you may speed up that part in editing.
