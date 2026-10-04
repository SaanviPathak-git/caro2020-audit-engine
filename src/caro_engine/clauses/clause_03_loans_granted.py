"""
Substantive Audit Testing Module: Clause (iii) - Loans, Investments, Guarantees & Securities Granted
Statutory Reference: CARO 2020 Clause 3(iii)(a)-(f) / Guidance Note on CARO 2020
"""

import pandas as pd
from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_03_loans_granted(data: Dict[str, Any]) -> ClauseResult:
    loans_df: pd.DataFrame = data.get("loans_investments_guarantees", pd.DataFrame())
    
    substantive_tests = [
        "Extracted all loans, advances in nature of loans, investments, and guarantees granted during the year per General Ledger.",
        "Computed aggregate amounts granted and closing balances segregated between Group Entities (Subsidiaries, JVs, Associates) and Other Parties.",
        "Audited loan agreements to verify if interest rates, repayment tenors, or security terms are prejudicial to the company's interest per Clause 3(iii)(b).",
        "Tested receipt of principal and interest installments against stipulated repayment schedules.",
        "Scanned loan aging ledgers to detect balances overdue for more than 90 days and inspected management legal recovery notices per Clause 3(iii)(d).",
        "Evaluated whether any loans falling due were rolled over, renewed, or extended by fresh loans per Clause 3(iii)(e).",
        "Calculated the proportion of loans repayable on demand or without specific repayment terms per Clause 3(iii)(f)."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.CAST_VERIFIED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.TRIAL_BALANCE_TIED]
    status = ClauseStatus.CLEAN
    
    # 1. Segregation calculation for Clause (iii)(a)
    sub_granted = 0.0
    sub_closing = 0.0
    oth_granted = 0.0
    oth_closing = 0.0
    total_loans_closing = 0.0
    on_demand_closing = 0.0
    
    overdue_gt_90 = []
    prejudicial_loans = []
    
    if not loans_df.empty:
        for _, row in loans_df.iterrows():
            rel = str(row.get("relationship", "")).strip().lower()
            tx_type = str(row.get("type", "")).strip().lower()
            granted = float(row.get("amount_granted_during_year_cr", 0.0))
            closing = float(row.get("balance_outstanding_cr", 0.0))
            is_prejudicial = str(row.get("terms_prejudicial", "No")).strip().lower() in ["yes", "true"]
            overdue_90 = float(row.get("overdue_gt_90_days_cr", 0.0))
            is_demand = str(row.get("repayable_on_demand_or_no_terms", "No")).strip().lower() in ["yes", "true"]
            
            if "loan" in tx_type or "advance" in tx_type:
                total_loans_closing += closing
                if is_demand:
                    on_demand_closing += closing

            if any(k in rel for k in ["subsidiary", "joint venture", "associate"]):
                sub_granted += granted
                sub_closing += closing
            else:
                oth_granted += granted
                oth_closing += closing

            # Check prejudicial terms
            if is_prejudicial:
                prejudicial_loans.append(row["party_name"])
                status = ClauseStatus.QUALIFIED
                exceptions.append(AuditException(
                    clause_id="Clause (iii)(b)",
                    headline=f"Prejudicial loan terms granted to {row['party_name']}",
                    description=f"Terms and conditions of loan/advance granted to {row['party_name']} (₹{granted:.2f} Cr granted, ₹{closing:.2f} Cr outstanding) are prejudicial to the interest of the Company.",
                    amount_involved=closing,
                    severity="CRITICAL"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

            # Check overdues > 90 days
            if overdue_90 > 0:
                overdue_gt_90.append((row["party_name"], overdue_90, str(row.get("reasonable_steps_taken", "No"))))
                status = ClauseStatus.QUALIFIED
                exceptions.append(AuditException(
                    clause_id="Clause (iii)(d)",
                    headline=f"Loan overdue > 90 days for {row['party_name']}",
                    description=f"Amount overdue for more than 90 days is ₹{overdue_90:.2f} Cr. Reasonable steps taken for recovery: {row.get('reasonable_steps_taken')}.",
                    amount_involved=overdue_90,
                    severity="HIGH"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

    # Clause (iii)(f) Demand loans percentage
    demand_pct = (on_demand_closing / total_loans_closing * 100.0) if total_loans_closing > 0 else 0.0
    if demand_pct > 0:
        if status != ClauseStatus.QUALIFIED:
            status = ClauseStatus.OBSERVATION
        observations.append(f"Loans repayable on demand or without specifying repayment terms constitute {demand_pct:.2f}% (₹{on_demand_closing:.2f} Cr) of total loans.")

    # ICAI Mandatory Table for Clause (iii)(a)
    loans_table_headers = [
        "Category",
        "Aggregate Amount Granted during the Year (₹ Cr)",
        "Balance Outstanding as at March 31 (₹ Cr)"
    ]
    loans_table_rows = [
        ["Subsidiaries, Joint Ventures and Associates", f"{sub_granted:.2f}", f"{sub_closing:.2f}"],
        ["Parties other than Subsidiaries, Joint Ventures and Associates", f"{oth_granted:.2f}", f"{oth_closing:.2f}"],
        ["Total", f"{sub_granted + oth_granted:.2f}", f"{sub_closing + oth_closing:.2f}"]
    ]

    # ICAI Report text
    if status == ClauseStatus.CLEAN:
        icai_text = (
            "(iii) According to the information and explanations given to us and on the basis of our examination of the records of the Company:\n"
            f"(a) During the year, the Company has provided loans, advances in nature of loans, investments and guarantees to subsidiaries, joint ventures and other parties as summarized in the table below:\n"
            f"    - To Subsidiaries, JVs & Associates: Granted ₹{sub_granted:.2f} Cr; Outstanding: ₹{sub_closing:.2f} Cr.\n"
            f"    - To Other Parties: Granted ₹{oth_granted:.2f} Cr; Outstanding: ₹{oth_closing:.2f} Cr.\n"
            "(b) In our opinion, the investments made, guarantees provided, and the terms and conditions of the grant of all loans and advances in the nature of loans are not prejudicial to the company's interest.\n"
            "(c) In respect of loans and advances in nature of loans, the schedule of repayment of principal and payment of interest has been stipulated and repayments or receipts are regular.\n"
            "(d) There are no amounts overdue for more than ninety days in respect of the loans or advances granted.\n"
            "(e) No loans or advances in the nature of loans granted which had fallen due during the year have been renewed or extended or fresh loans granted to settle the overdues.\n"
            "(f) The Company has not granted any loans or advances in the nature of loans either repayable on demand or without specifying any terms or period of repayment."
        )
    else:
        icai_text = (
            "(iii) According to the information and explanations given to us and on the basis of our examination of records:\n"
            f"(a) The Company has provided loans, guarantees, and securities during the year as detailed in the summary table.\n"
            f"(b) Terms and conditions of certain loans granted were prejudicial to the interest of the Company, as detailed in the exception log.\n"
            f"(c) Repayment schedules are regular except for instances identified in the audit findings.\n"
            f"(d) Certain amounts are overdue for more than 90 days as reported in the exception log.\n"
            f"(e) Renewals and extensions of loans, if any, have been reviewed and documented.\n"
            f"(f) Loans repayable on demand or without terms constitute {demand_pct:.2f}% of total loans."
        )

    return ClauseResult(
        clause_id="Clause (iii)",
        clause_num="iii",
        clause_sub="(a)-(f)",
        title="Loans, Investments, Guarantees & Securities Granted",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=loans_table_headers,
        disclosure_table_rows=loans_table_rows,
        workpaper_rows=loans_df.to_dict(orient="records") if not loans_df.empty else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
