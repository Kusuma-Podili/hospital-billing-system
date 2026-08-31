"""
MedBill Enterprise - Main Entry Point
Hospital Billing & Revenue Cycle Management System
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from medbill.web.server import run_server


def main():
    port = int(os.environ.get("PORT", 8080))
    print("=" * 80)
    print(f"[*] Starting MedBill Enterprise Hospital Billing System on port {port}...")
    print(f"[*] Access Web POS & RCM Dashboard: http://localhost:{port}")
    print("=" * 80)
    run_server(port=port)


if __name__ == "__main__":
    main()
