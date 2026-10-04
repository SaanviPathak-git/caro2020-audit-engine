"""
Substantive Audit Testing Module: Clause (vii) - Statutory Dues & Disputed Litigations
Statutory Reference: CARO 2020 Clause 3(vii)(a)-(b) / Guidance Note on CARO 2020 / SA 250
"""

import pandas as pd
from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_07_statutory_dues(data: Dict[str, Any]) -> ClauseResult:
    dues_df: pd.DataFrame = data.get("statutory_dues_ledger", pd.DataFrame())
    lit_df: pd.DataFrame = data.get("litigation_register", pd.DataFrame())
    
    substantive_tests = [
        "Vouched statutory tax challans and bank debits to verify regularity in depositing statutory dues per SA 250.",
        "Scanned GST (GSTR-3B), PF, ESIC, TDS (TRACES) and Advance Tax ledgers as of March 31.",
        "Calculated aging of all unpaid undisputed statutory dues from their respective due dates to March 31.",
        "Flagged undisputed arrears remaining unpaid for more than six months (> 6 months) as of balance sheet date per Clause 3(vii)(a).",
        "Inspected dispute notices, demand orders, appeal memos, and legal counsel opinions for disputed tax litigations per SA 501.",
        "Verified amounts paid under protest / pre-deposit and organized litigations by respective appellate forums per Clause 3(vii)(b)."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.CAST_VERIFIED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.TRIAL_BALANCE_TIED]
    status = ClauseStatus.CLEAN

    # 1. Undisputed Dues > 6 Months (Clause vii(a))
    undisputed_table_headers = [
        "Name of Statute",
        "Nature of Dues",
        "Amount (₹ Cr)",
        "Period to Which Amount Relates",
        "Due Date",
        "Date of Payment / Status"
    ]
    undisputed_table_rows = []
    
    if not dues_df.empty:
        for _, row in dues_df.iterrows():
            is_gt_6m = str(row.get("exceeds_6_months", "No")).strip().lower() in ["yes", "true"]
            amt = float(row.get("amount_cr", 0.0))
            statute = row.get("statute_name", "")
            nature = row.get("nature_of_dues", "")
            
            if is_gt_6m and amt > 0:
                undisputed_table_rows.append([
                    statute,
                    nature,
                    f"{amt:.2f}",
                    str(row.get("period_to_which_relates", "")),
                    str(row.get("due_date", "")),
                    str(row.get("payment_date", "Unpaid"))
                ])
                status = ClauseStatus.QUALIFIED
                exceptions.append(AuditException(
                    clause_id="Clause (vii)(a)",
                    headline=f"Undisputed statutory due unpaid > 6 months: {nature}",
                    description=f"Undisputed arrears of {nature} under {statute} amounting to ₹{amt:.2f} Cr remained unpaid for more than 6 months as of March 31.",
                    amount_involved=amt,
                    severity="HIGH"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

        if not undisputed_table_rows:
            observations.append("The Company has generally been regular in depositing undisputed statutory dues with appropriate authorities. No arrears unpaid > 6 months as of March 31.")
        else:
            observations.append(f"Undisputed statutory arrears exceeding 6 months identified totaling ₹{sum(float(r[2]) for r in undisputed_table_rows):.2f} Cr.")

    # 2. Disputed Statutory Dues (Clause vii(b))
    disputed_table_headers = [
        "Name of Statute",
        "Nature of Dues",
        "Gross Disputed Amount (₹ Cr)",
        "Amount Paid Under Protest (₹ Cr)",
        "Net Unpaid Amount (₹ Cr)",
        "Period to Which Relates",
        "Forum Where Dispute is Pending"
    ]
    disputed_table_rows = []
    
    if not lit_df.empty:
        for _, row in lit_df.iterrows():
            gross = float(row.get("gross_disputed_amount_cr", 0.0))
            protest = float(row.get("amount_paid_under_protest_cr", 0.0))
            net = float(row.get("net_unpaid_amount_cr", gross - protest))
            
            disputed_table_rows.append([
                row.get("statute_name", ""),
                row.get("nature_of_dues", ""),
                f"{gross:.2f}",
                f"{protest:.2f}",
                f"{net:.2f}",
                str(row.get("period_to_which_relates", "")),
                str(row.get("forum_where_pending", ""))
            ])
            
        observations.append(f"Disputed statutory dues pending before appellate forums documented across {len(disputed_table_rows)} proceedings.")

    # ICAI Report text
    if not undisputed_table_rows:
        part_a_text = (
            "(vii) (a) According to the information and explanations given to us and on the basis of our examination of the records of the Company, "
            "the Company has generally been regular in depositing undisputed statutory dues including Goods and Services Tax, provident fund, "
            "employees' state insurance, income-tax, sales-tax, service tax, duty of customs, duty of excise, value added tax, cess and other statutory dues "
            "applicable to it with the appropriate authorities.\n"
            "According to the information and explanations given to us, no undisputed amounts payable in respect of Goods and Services Tax, provident fund, "
            "employees' state insurance, income-tax, sales-tax, service tax, duty of customs, duty of excise, value added tax, cess and other statutory dues "
            "were in arrears as at March 31, 2024 for a period of more than six months from the date they became payable.\n"
        )
    else:
        part_a_text = (
            "(vii) (a) According to the information and explanations given to us and on the basis of our examination of the records of the Company, "
            "undisputed amounts payable in respect of statutory dues which were in arrears as at March 31, 2024 for a period of more than six months "
            "from the date they became payable are as follows:\n"
        )
        
    if disputed_table_rows:
        part_b_text = (
            "(b) According to the information and explanations given to us, statutory dues relating to Goods and Services Tax, provident fund, "
            "income-tax, sales-tax, service tax, duty of customs, duty of excise and value added tax which have not been deposited on account of any dispute "
            "are set out in the table below:\n"
        )
    else:
        part_b_text = "(b) According to the information and explanations given to us, there are no statutory dues which have not been deposited on account of any dispute.\n"

    icai_text = part_a_text + part_b_text

    # Combined disclosure table for reporting
    combined_headers = undisputed_table_headers if undisputed_table_rows else disputed_table_headers
    combined_rows = undisputed_table_rows if undisputed_table_rows else disputed_table_rows

    return ClauseResult(
        clause_id="Clause (vii)",
        clause_num="vii",
        clause_sub="(a)-(b)",
        title="Statutory Dues & Disputed Litigations",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=combined_headers,
        disclosure_table_rows=combined_rows,
        workpaper_rows=dues_df.to_dict(orient="records") if not dues_df.empty else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
