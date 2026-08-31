"""
MedBill Enterprise - Application Runner Entry Point
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from medbill.web.server import run_server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    run_server(port=port)
