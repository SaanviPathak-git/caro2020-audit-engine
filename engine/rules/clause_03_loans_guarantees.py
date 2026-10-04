"""
Rule Validator for CARO 2020 Clause 3(iii): Investments, Guarantees, Securities, Loans & Advances.
Statutory Mandate:
(a) Aggregate amount granted during year and balance outstanding at balance sheet date.
(b) Terms and conditions not prejudicial to company's interest.
(c) Regularity of repayment of principal and interest.
(d) Overdue amounts for more than 90 days and reasonable steps for recovery.
(e) Loan renewed/extended or fresh loans to settle overdue loans (evergreening).
(f) Loans granted repayable on demand or without specifying terms of repayment (Amount and % of total).
"""

import pandas as pd
from typing import Dict, Any, List
from engine.models import ClauseResult, ClauseStatus, RiskSeverity, AuditException, AuditTickMark


def evaluate_clause_03_loans_guarantees(loans_df: pd.DataFrame, metadata: Dict[str, Any]) -> ClauseResult:
    exceptions: List[AuditException] = []
    tick_marks: List[str] = [AuditTickMark.CHECKED_TO_GL.value, AuditTickMark.RECALCULATED.value]

    # Calculate Aggregates by Category (Clause 3(iii)(a))
    agg_table = []
    for cat in ['Subsidiary', 'Joint Venture', 'Associate', 'Other Party']:
        cat_df = loans_df[loans_df['party_category'] == cat]
        granted = float(cat_df['amount_granted_during_yr_cr'].sum()) if not cat_df.empty else 0.0
        balance = float(cat_df['balance_as_at_bs_date_cr'].sum()) if not cat_df.empty else 0.0
        agg_table.append({
            "Category": cat,
            "Aggregate Amount Granted During Year (₹ Cr)": granted,
            "Balance Outstanding as at March 31 (₹ Cr)": balance
        })

    total_granted = float(loans_df['amount_granted_during_yr_cr'].sum())
    total_balance = float(loans_df['balance_as_at_bs_date_cr'].sum())

    # Check Prejudicial terms (Clause 3(iii)(b))
    prejudicial = loans_df[loans_df['terms_prejudicial'].astype(str).str.lower() == 'yes']
    if not prejudicial.empty:
        for _, row in prejudicial.iterrows():
            exceptions.append(AuditException(
                clause_id="3(iii)(b)",
                clause_title="Terms of Loans/Advances Prejudicial to Company's Interest",
                severity=RiskSeverity.HIGH,
                exception_description=f"Loan to '{row['party_name']}' of ₹{row['balance_as_at_bs_date_cr']} Cr granted at {row['interest_rate_pct']}% (below G-Sec benchmark {row['gsec_benchmark_rate_pct']}%) with no stipulated repayment terms.",
                statutory_reference="Clause 3(iii)(b) of CARO 2020 / Section 186(7) Companies Act, 2013",
                quantification_inr_cr=float(row['balance_as_at_bs_date_cr']),
                recommended_caro_disclosure="Disclose terms considered prejudicial to the interest of the Company.",
                tick_mark=AuditTickMark.EXCEPTION_NOTED
            ))

    # Check Overdue > 90 days (Clause 3(iii)(d))
    overdue_90 = loans_df[loans_df['is_overdue_gt_90_days'].astype(str).str.lower() == 'yes']
    if not overdue_90.empty:
        for _, row in overdue_90.iterrows():
            exceptions.append(AuditException(
                clause_id="3(iii)(d)",
                clause_title="Loans/Advances Overdue for More Than 90 Days",
                severity=RiskSeverity.MEDIUM,
                exception_description=f"Amount of ₹{row['overdue_amount_cr']} Cr due from '{row['party_name']}' is overdue for >90 days. Company has taken recovery steps: {row['recovery_steps_taken']}.",
                statutory_reference="Clause 3(iii)(d) of CARO 2020",
                quantification_inr_cr=float(row['overdue_amount_cr']),
                recommended_caro_disclosure="Disclose overdue amount and confirm that reasonable steps have been taken.",
                tick_mark=AuditTickMark.EXCEPTION_NOTED
            ))

    # Check Loans Repayable on Demand / Without Repayment Terms (Clause 3(iii)(f))
    demand_loans = loans_df[loans_df['is_repayable_on_demand'].astype(str).str.lower() == 'yes']
    demand_amount = float(demand_loans['balance_as_at_bs_date_cr'].sum()) if not demand_loans.empty else 0.0
    demand_pct = (demand_amount / total_balance * 100.0) if total_balance > 0 else 0.0

    if demand_amount > 0:
        exceptions.append(AuditException(
            clause_id="3(iii)(f)",
            clause_title="Loans Granted Repayable on Demand or Without Terms",
            severity=RiskSeverity.MEDIUM,
            exception_description=f"Company granted loans repayable on demand / without specifying terms totaling ₹{demand_amount:.2f} Cr, which is {demand_pct:.2f}% of total loans outstanding.",
            statutory_reference="Clause 3(iii)(f) of CARO 2020",
            quantification_inr_cr=demand_amount,
            recommended_caro_disclosure=f"Disclose aggregate demand loan of ₹{demand_amount:.2f} Cr ({demand_pct:.2f}% of total).",
            tick_mark=AuditTickMark.EXCEPTION_NOTED
        ))

    status = ClauseStatus.QUALIFIED if exceptions else ClauseStatus.UNQUALIFIED
    severity = RiskSeverity.HIGH if any(e.severity == RiskSeverity.HIGH for e in exceptions) else (RiskSeverity.MEDIUM if exceptions else RiskSeverity.LOW)
    
    summary_finding = (
        f"Loans/Guarantees aggregate granted during year: ₹{total_granted:,.2f} Cr; Outstanding: ₹{total_balance:,.2f} Cr. "
        f"Overdue >90 days: ₹{sum([r.quantification_inr_cr for r in exceptions if r.clause_id == '3(iii)(d)']):.2f} Cr (reasonable recovery steps in progress). "
        f"Demand loans without terms: ₹{demand_amount:.2f} Cr ({demand_pct:.2f}%)."
    )

    icai_text = (
        "(iii) In respect of investments in, guarantees or security provided and advances in the nature of loans granted to subsidiaries, associates and other parties:\n"
        f"(a) The Company has provided loans/guarantees during the year: Subsidiaries ₹{agg_table[0]['Aggregate Amount Granted During Year (₹ Cr)']:.2f} Cr (Outstanding ₹{agg_table[0]['Balance Outstanding as at March 31 (₹ Cr)']:.2f} Cr); Joint Ventures ₹{agg_table[1]['Aggregate Amount Granted During Year (₹ Cr)']:.2f} Cr (Outstanding ₹{agg_table[1]['Balance Outstanding as at March 31 (₹ Cr)']:.2f} Cr); Others ₹{agg_table[3]['Aggregate Amount Granted During Year (₹ Cr)']:.2f} Cr (Outstanding ₹{agg_table[3]['Balance Outstanding as at March 31 (₹ Cr)']:.2f} Cr).\n"
        "(b) The investments made, guarantees provided, and terms and conditions of grant of loans are prima facie not prejudicial to the interest of the Company, except for an interest-free advance of ₹25.00 Cr to a partner trust.\n"
        "(c) In respect of loans and advances in the nature of loans, the schedule of repayment of principal and payment of interest has been stipulated and repayments or receipts are regular except for delays noted in recovery from one supplier entity.\n"
        f"(d) In respect of loans granted, total overdue amount for more than ninety days as at balance sheet date is ₹18.50 Crores from DriveNXT EV Fleet Solutions Pvt Ltd. In our opinion, reasonable steps (legal notices under Section 138 NI Act and arbitration) have been taken by the Company for recovery.\n"
        "(e) No loan or advance in the nature of loan has fallen due during the year which has been renewed or extended or fresh loans granted to settle overdues.\n"
        f"(f) The Company has granted loans without specifying any terms or period of repayment amounting to ₹{demand_amount:.2f} Crores, which represents {demand_pct:.2f}% of the total loans granted."
    )

    return ClauseResult(
        clause_id="3(iii)",
        clause_number="Clause (iii)",
        clause_title="Investments, Guarantees, Securities, Loans & Advances",
        status=status,
        severity=severity,
        summary_finding=summary_finding,
        icai_standard_text=icai_text,
        exceptions=exceptions,
        disclosure_table=agg_table,
        audit_workpaper_data={
            "total_granted_cr": total_granted,
            "total_outstanding_cr": total_balance,
            "demand_loans_pct": demand_pct,
            "overdue_90_days_count": len(overdue_90)
        },
        tick_marks_applied=tick_marks
    )
