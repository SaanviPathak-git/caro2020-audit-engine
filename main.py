"""
Main Command-Line Interface (CLI) for CARO 2020 Automated Audit Testing Engine.
Run substantive audit procedures, generate Big 4 workpapers, and output draft CARO reports.
"""

import os
import sys
import argparse
from engine.auditor_core import Caro2020Auditor
from engine.workpaper_generator import create_audit_workpaper
from engine.report_generator import generate_draft_caro_report_markdown


def main():
    parser = argparse.ArgumentParser(description="CARO 2020 Automated Substantive Audit Testing Engine")
    parser.add_argument(
        "--schedules-dir", 
        type=str, 
        default="data/raw_schedules/tata_motors_fy24",
        help="Path to directory containing client schedules and metadata"
    )
    parser.add_argument(
        "--out-dir", 
        type=str, 
        default="outputs",
        help="Path to save generated audit workpapers and CARO reports"
    )
    args = parser.parse_args()

    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print("=" * 80)
    print(">> CARO 2020 AUTOMATED SUBSTANTIVE AUDIT TESTING ENGINE")
    print("   Standard: Companies (Auditor's Report) Order, 2020 / ICAI Guidance Note")
    print("=" * 80)

    print(f"\n[*] Loading client schedules from: {args.schedules_dir}")
    auditor = Caro2020Auditor(args.schedules_dir)
    print(f"[+] Loaded Client: {auditor.metadata.get('company_name')} (CIN: {auditor.metadata.get('cin')})")
    print(f"[+] Financial Year: {auditor.metadata.get('financial_year')} | Balance Sheet Date: {auditor.metadata.get('balance_sheet_date')}")
    print(f"[+] Overall Materiality: ₹{auditor.metadata.get('materiality', {}).get('overall_materiality_inr_cr')} Cr")

    print("\n[*] Executing independent substantive audit tests across all 21 clauses...")
    result = auditor.run_substantive_audit()

    print("\n" + "=" * 80)
    print(">> AUDIT TESTING RESULTS SUMMARY:")
    print("=" * 80)
    print(f"Total Clauses Tested           : {result.total_clauses_tested}")
    print(f"Unqualified (Clean) Clauses    : {result.unqualified_count}")
    print(f"Qualified Clauses (Disclosures): {result.qualified_count}")
    print(f"Not Applicable Clauses         : {result.not_applicable_count}")
    print(f"Adverse Remarks                : {result.adverse_count}")
    print(f"Total Audit Exceptions Flagged : {result.total_exceptions_identified}")
    print(f"Clauses with High/Critical Risk: {', '.join(result.critical_risk_clauses) if result.critical_risk_clauses else 'None'}")
    print("-" * 80)

    for cid, r in result.clause_results.items():
        tick_str = "".join(r.tick_marks_applied)
        status_disp = f"[{r.status.value}]"
        print(f"  {r.clause_id:<8} | {status_disp:<15} | {r.severity.value:<8} | {r.clause_title[:40]}")

    print("-" * 80)
    
    # Generate Deliverables
    os.makedirs(args.out_dir, exist_ok=True)
    
    workpaper_file = os.path.join(args.out_dir, "CARO_2020_Audit_Workpaper_TataMotors_FY24.xlsx")
    print(f"\n[*] Generating Big 4 Multi-Tab Audit Workpaper (.xlsx)...")
    create_audit_workpaper(result, workpaper_file)
    print(f"[+] Audit Workpaper generated at: {workpaper_file}")

    report_file = os.path.join(args.out_dir, "Draft_CARO_2020_Report_TataMotors_FY24.md")
    print(f"[*] Generating Statutory CARO 2020 Legal Annexure (.md)...")
    generate_draft_caro_report_markdown(result, report_file)
    print(f"[+] Draft CARO Report generated at: {report_file}")

    print("\n" + "=" * 80)
    print("[SUCCESS] AUDIT PROCEDURES COMPLETE - DELIVERABLES READY FOR REGULATORY INSPECTION")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
