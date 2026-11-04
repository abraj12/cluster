"""
Streamlit Cloud Entrypoint for Website Traffic Analytics & Prediction Dashboard.
Directly loads and executes the main dashboard application from dashboard/app.py.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Path to the primary dashboard script
DASHBOARD_SCRIPT = PROJECT_ROOT / "dashboard" / "app.py"

if __name__ == "__main__" or True:
    with open(DASHBOARD_SCRIPT, "r", encoding="utf-8") as f:
        code = compile(f.read(), str(DASHBOARD_SCRIPT), "exec")
        globs = {
            "__name__": "__main__",
            "__file__": str(DASHBOARD_SCRIPT),
            "__builtins__": __builtins__,
        }
        exec(code, globs)
