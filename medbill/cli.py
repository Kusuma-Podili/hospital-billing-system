"""
MedBill Enterprise - Command Line Interface (CLI)
Provides command-line commands for quick billing calculations, catalog lookups, and trial balance reports.
"""

import sys
import os
import argparse
from datetime import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from medbill.catalogs.icd10_cm import search_icd10
from medbill.catalogs.cpt_codes import search_cpt
from medbill.catalogs.pharmacy_ndc import search_medications
from medbill.catalogs.loinc_lab_panels import search_lab_panels
from medbill.modules.ledger.general_ledger import GeneralLedgerService


def main():
    parser = argparse.ArgumentParser(description="MedBill Enterprise - Hospital Billing System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Catalog search
    search_parser = subparsers.add_parser("search", help="Search clinical fee and diagnostic catalogs")
    search_parser.add_argument("catalog", choices=["icd10", "cpt", "pharmacy", "labs"], help="Catalog to search")
    search_parser.add_argument("query", help="Search keyword")

    # Ledger Trial Balance
    subparsers.add_parser("ledger", help="Display real-time Double-Entry General Ledger Trial Balance")

    # Run Server
    subparsers.add_parser("serve", help="Start the Web Dashboard and REST API Server")

    args = parser.parse_args()

    if args.command == "search":
        if args.catalog == "icd10":
            results = search_icd10(args.query)
            print(f"\n🔍 ICD-10 Search Results for '{args.query}':")
            for r in results:
                print(f"  [{r.code}] {r.description} (Chapter: {r.chapter}, Severity: {r.severity_level})")
        elif args.catalog == "cpt":
            results = search_cpt(args.query)
            print(f"\n🔍 CPT Search Results for '{args.query}':")
            for r in results:
                print(f"  [{r.code}] {r.description} (Category: {r.category}, Standard Fee: ${r.standard_fee:.2f})")
        elif args.catalog == "pharmacy":
            results = search_medications(args.query)
            print(f"\n🔍 Pharmacy NDC Search Results for '{args.query}':")
            for r in results:
                print(f"  [{r.ndc}] {r.brand_name} ({r.generic_name}) - ${r.unit_selling_price:.2f}")
        elif args.catalog == "labs":
            results = search_lab_panels(args.query)
            print(f"\n🔍 Diagnostic LOINC Search Results for '{args.query}':")
            for r in results:
                print(f"  [{r.loinc_code}] {r.panel_name} (${r.standard_price:.2f})")

    elif args.command == "ledger":
        ledger = GeneralLedgerService()
        tb = ledger.get_trial_balance()
        print("\n📊 MedBill Enterprise - General Ledger Trial Balance")
        print(f"Timestamp: {tb['timestamp']}")
        print("-" * 75)
        print(f"{'Code':<8} {'Account Name':<35} {'Type':<10} {'Debit ($)':>10} {'Credit ($)':>10}")
        print("-" * 75)
        for acc in tb["accounts"]:
            print(f"{acc['code']:<8} {acc['name']:<35} {acc['type']:<10} {acc['debit']:>10.2f} {acc['credit']:>10.2f}")
        print("-" * 75)
        print(f"{'TOTALS':<55} {tb['total_debits']:>10.2f} {tb['total_credits']:>10.2f}")
        print(f"Ledger Balance Status: {'✅ BALANCED' if tb['is_balanced'] else '❌ IMBALANCED'}\n")

    elif args.command == "serve":
        from medbill.web.server import run_server
        run_server()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
