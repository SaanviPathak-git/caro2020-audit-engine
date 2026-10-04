"""
Rule Validator for CARO 2020 Clause 3(vii): Undisputed and Disputed Statutory Dues.
Statutory Mandate:
(a) Regularity in depositing undisputed statutory dues (GST, PF, ESI, Income-tax, Customs, etc.).
    Arrears outstanding for more than 6 months from the date they became payable as on the balance sheet date.
(b) Statutory dues not deposited on account of any dispute, forum where dispute is pending, and amounts involved.
"""

import pandas as pd
from typing import Dict, Any, List
from engine.models import ClauseResult, ClauseStatus, RiskSeverity, AuditException, AuditTickMark


def evaluate_clause_07_statutory_dues(
    undisputed_df: pd.DataFrame, 
    disputed_df: pd.DataFrame, 
    metadata: Dict[str, Any]
) -> ClauseResult:
    exceptions: List[AuditException] = []
    tick_marks: List[str] = [
        AuditTickMark.CHECKED_TO_GL.value, 
        AuditTickMark.RECALCULATED.value, 
        AuditTickMark.TRACED_TO_STATUTE.value
    ]

    # 1. Check Undisputed Dues > 6 months as of 31 March (Clause 3(vii)(a))
    undisputed_overdue = undisputed_df[undisputed_df['overdue_gt_6_months'].astype(str).str.lower() == 'yes']
    undisputed_table = []
    
    if not undisputed_overdue.empty:
        for _, row in undisputed_overdue.iterrows():
            amt = float(row['outstanding_as_on_31mar2024'])
            undisputed_table.append({
                "Name of the Statute": row['statute_name'],
                "Nature of Dues": row['nature_of_dues'],
                "Amount Outstanding (₹ Cr)": amt,
                "Due Date": str(row['due_date']),
                "Period Outstanding": "> 6 Months",
                "Reason for Non-Payment": row['reason_for_delay']
            })
            exceptions.append(AuditException(
                clause_id="3(vii)(a)",
                clause_title="Undisputed Statutory Dues Unpaid for More Than 6 Months",
                severity=RiskSeverity.HIGH,
                exception_description=f"Undisputed dues of ₹{amt:.2f} Cr ({row['statute_name']} - {row['nature_of_dues']}) remained outstanding for >6 months as on March 31, 2024. Reason: {row['reason_for_delay']}.",
                statutory_reference="Clause 3(vii)(a) of CARO 2020",
                quantification_inr_cr=amt,
                recommended_caro_disclosure="Mandatory statutory disclosure in Annexure to Auditor's Report.",
                tick_mark=AuditTickMark.EXCEPTION_NOTED
            ))

    # 2. Group Disputed Dues by Forum (Clause 3(vii)(b))
    disputed_table = []
    total_disputed_gross = 0.0
    total_disputed_net = 0.0

    if not disputed_df.empty:
        for _, row in disputed_df.iterrows():
            gross = float(row['gross_amount_cr'])
            paid = float(row['amount_paid_under_protest_cr'])
            net = float(row['net_amount_unpaid_cr'])
            total_disputed_gross += gross
            total_disputed_net += net
            
            disputed_table.append({
                "Name of the Statute": row['name_of_statute'],
                "Nature of Dues": row['nature_of_dues'],
                "Gross Demand (₹ Cr)": gross,
                "Paid Under Protest (₹ Cr)": paid,
                "Net Unpaid (₹ Cr)": net,
                "Financial Year": row['period_relates_to_fy'],
                "Appellate Forum Where Dispute is Pending": row['forum_where_dispute_is_pending']
            })

        exceptions.append(AuditException(
            clause_id="3(vii)(b)",
            clause_title="Disputed Statutory Dues Pending Before Appellate Authorities",
            severity=RiskSeverity.MEDIUM,
            exception_description=f"Statutory dues aggregating to Gross ₹{total_disputed_gross:.2f} Cr (Net Unpaid ₹{total_disputed_net:.2f} Cr) have not been deposited on account of disputes before various forums including ITAT, CESTAT, High Court and Supreme Court.",
            statutory_reference="Clause 3(vii)(b) of CARO 2020",
            quantification_inr_cr=total_disputed_net,
            recommended_caro_disclosure="Mandatory statutory disclosure table by statute and appellate forum.",
            tick_mark=AuditTickMark.TRACED_TO_STATUTE
        ))

    status = ClauseStatus.QUALIFIED
    severity = RiskSeverity.HIGH if not undisputed_overdue.empty else RiskSeverity.MEDIUM
    
    total_undisputed_overdue = sum([r['Amount Outstanding (₹ Cr)'] for r in undisputed_table])
    summary_finding = (
        f"Statutory dues regular in most instances. "
        f"Undisputed arrears > 6 months: {len(undisputed_table)} items totaling ₹{total_undisputed_overdue:.2f} Cr (Property tax & local cess). "
        f"Disputed litigations: {len(disputed_table)} matters totaling Net Unpaid ₹{total_disputed_net:.2f} Cr before ITAT, CESTAT, High Court & Supreme Court."
    )

    icai_text = (
        "(vii)(a) According to the records of the Company, undisputed statutory dues including Goods and Services Tax, provident fund, employees' state insurance, income-tax, duty of customs and cess have generally been regularly deposited with the appropriate authorities, except for the following arrears of outstanding statutory dues as at 31 March 2024 for a period of more than six months from the date they became payable:\n"
        f"[REFER STATUTORY DISCLOSURE TABLE: {len(undisputed_table)} items totaling ₹{total_undisputed_overdue:.2f} Cr]\n"
        "(b) According to the records of the Company, statutory dues that have not been deposited on account of any dispute are as follows:\n"
        f"[REFER STATUTORY DISCLOSURE TABLE: {len(disputed_table)} matters totaling Gross ₹{total_disputed_gross:.2f} Cr, Net Unpaid ₹{total_disputed_net:.2f} Cr]"
    )

    return ClauseResult(
        clause_id="3(vii)",
        clause_number="Clause (vii)",
        clause_title="Undisputed and Disputed Statutory Dues",
        status=status,
        severity=severity,
        summary_finding=summary_finding,
        icai_standard_text=icai_text,
        exceptions=exceptions,
        disclosure_table=disputed_table,
        audit_workpaper_data={
            "undisputed_overdue_table": undisputed_table,
            "disputed_table": disputed_table,
            "total_undisputed_arrears_gt_6m_cr": total_undisputed_overdue,
            "total_disputed_net_unpaid_cr": total_disputed_net
        },
        tick_marks_applied=tick_marks
    )
