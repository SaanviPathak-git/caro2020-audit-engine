"""
Rule Validator for CARO 2020 Clause 3(xvii): Incurrence of Real Cash Losses.
Statutory Mandate:
Whether the company has incurred cash losses in the financial year and in the immediately preceding financial year,
if so, state the amount of cash losses.
ICAI Formula:
Cash Loss = Profit / (Loss) After Tax (PAT)
          + Depreciation & Amortization expense
          + Impairment of assets (non-cash)
          +/- Other non-cash unrealized items.
"""

import pandas as pd
from typing import Dict, Any, List
from engine.models import ClauseResult, ClauseStatus, RiskSeverity, AuditException, AuditTickMark


def evaluate_clause_17_cash_losses(cash_loss_df: pd.DataFrame, metadata: Dict[str, Any]) -> ClauseResult:
    exceptions: List[AuditException] = []
    tick_marks: List[str] = [
        AuditTickMark.CHECKED_TO_GL.value, 
        AuditTickMark.RECALCULATED.value
    ]

    recalculated_table = []
    cash_loss_detected = False

    for _, row in cash_loss_df.iterrows():
        pat = float(row['pat_profit_loss_after_tax_cr'])
        depr = float(row['depreciation_amortization_cr'])
        imp = float(row.get('impairment_loss_non_cash_cr', 0.0))
        forex = float(row.get('unrealized_forex_loss_non_cash_cr', 0.0))
        tax_adj = float(row.get('deferred_tax_adjustment_cr', 0.0))
        
        # Substantive recalculation by auditor
        recalculated_cash_flow = pat + depr + imp + forex + tax_adj
        is_loss = recalculated_cash_flow < 0.0
        
        is_cy = str(row['is_current_year']).strip().lower() in ['yes', 'true', '1']
        
        recalculated_table.append({
            "Financial Year": str(row['financial_year']),
            "Is Current Year": "Yes" if is_cy else "No",
            "Profit / (Loss) After Tax (PAT) (₹ Cr)": pat,
            "Depreciation & Amortisation (₹ Cr)": depr,
            "Other Non-Cash Adjustments (₹ Cr)": imp + forex + tax_adj,
            "Recalculated Cash Profit / (Loss) (₹ Cr)": recalculated_cash_flow,
            "Incurred Cash Loss": "Yes" if is_loss else "No"
        })

        if is_loss:
            cash_loss_detected = True
            exceptions.append(AuditException(
                clause_id="3(xvii)",
                clause_title=f"Incurrence of Cash Loss in FY {row['financial_year']}",
                severity=RiskSeverity.HIGH,
                exception_description=f"Company incurred a cash loss of ₹{abs(recalculated_cash_flow):,.2f} Cr in FY {row['financial_year']}.",
                statutory_reference="Clause 3(xvii) of CARO 2020",
                quantification_inr_cr=abs(recalculated_cash_flow),
                recommended_caro_disclosure=f"Disclose cash loss of ₹{abs(recalculated_cash_flow):,.2f} Cr in FY {row['financial_year']}.",
                tick_mark=AuditTickMark.EXCEPTION_NOTED
            ))

    if cash_loss_detected:
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.HIGH
        loss_years = [r['Financial Year'] for r in recalculated_table if r['Incurred Cash Loss'] == "Yes"]
        summary_finding = f"Cash losses incurred in {', '.join(loss_years)}."
        loss_details = ", ".join([f"FY {r['Financial Year']}: ₹{abs(r['Recalculated Cash Profit / (Loss) (₹ Cr)']):.2f} Cr" for r in recalculated_table if r['Incurred Cash Loss'] == "Yes"])
        icai_text = f"(xvii) The Company has incurred cash losses in the following financial year(s): {loss_details}."
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        cy_list = [r['Recalculated Cash Profit / (Loss) (₹ Cr)'] for r in recalculated_table if r['Is Current Year'] == "Yes"]
        py_list = [r['Recalculated Cash Profit / (Loss) (₹ Cr)'] for r in recalculated_table if r['Is Current Year'] == "No"]
        cy_prof = cy_list[0] if cy_list else (recalculated_table[0]['Recalculated Cash Profit / (Loss) (₹ Cr)'] if recalculated_table else 0.0)
        py_prof = py_list[0] if py_list else (recalculated_table[1]['Recalculated Cash Profit / (Loss) (₹ Cr)'] if len(recalculated_table) > 1 else 0.0)
        summary_finding = f"No cash losses incurred in current FY (Cash profit: ₹{cy_prof:,.2f} Cr) or preceding FY (Cash profit: ₹{py_prof:,.2f} Cr)."
        icai_text = "(xvii) The Company has not incurred cash losses in the financial year and in the immediately preceding financial year."

    return ClauseResult(
        clause_id="3(xvii)",
        clause_number="Clause (xvii)",
        clause_title="Cash Losses Incurred in Financial Year & Preceding Financial Year",
        status=status,
        severity=severity,
        summary_finding=summary_finding,
        icai_standard_text=icai_text,
        exceptions=exceptions,
        disclosure_table=recalculated_table,
        audit_workpaper_data={
            "recalculated_table": recalculated_table,
            "cash_loss_detected": cash_loss_detected
        },
        tick_marks_applied=tick_marks
    )
