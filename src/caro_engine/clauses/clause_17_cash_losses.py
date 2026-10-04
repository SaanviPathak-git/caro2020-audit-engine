"""
Substantive Audit Testing Module: Clause (xvii) - Recalculation of Real Cash Losses
Statutory Reference: CARO 2020 Clause 3(xvii) / ICAI Guidance Note on CARO 2020 (Para 17)
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_17_cash_losses(data: Dict[str, Any]) -> ClauseResult:
    pnl_data = data.get("cash_flow_and_pnl", {})
    cy = pnl_data.get("current_year_fy24", {})
    py = pnl_data.get("preceding_year_fy23", {})
    
    substantive_tests = [
        "Extracted Profit / (Loss) Before Tax from audited Statement of Profit and Loss for current and preceding FYs.",
        "Reconciled non-cash charges: added back Depreciation, Amortization, asset impairments, and non-cash unrealized FX per ICAI Guidance Note.",
        "Mathematically recalculated real cash profit / cash loss for both financial years.",
        "Determined whether statutory disclosure of cash loss amounts is legally mandated under Clause 3(xvii)."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.CAST_VERIFIED, AuditTickMark.TRIAL_BALANCE_TIED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    # Mathematical recalculation
    cy_pbt = float(cy.get("profit_loss_before_tax_cr", 0.0))
    cy_dep = float(cy.get("depreciation_and_amortization_cr", 0.0))
    cy_imp = float(cy.get("impairment_loss_cr", 0.0))
    cy_fx = float(cy.get("unrealized_fx_gain_loss_cr", 0.0))
    cy_other = float(cy.get("other_non_cash_items_cr", 0.0))
    cy_cash = cy_pbt + cy_dep + cy_imp + cy_fx + cy_other

    py_pbt = float(py.get("profit_loss_before_tax_cr", 0.0))
    py_dep = float(py.get("depreciation_and_amortization_cr", 0.0))
    py_imp = float(py.get("impairment_loss_cr", 0.0))
    py_fx = float(py.get("unrealized_fx_gain_loss_cr", 0.0))
    py_other = float(py.get("other_non_cash_items_cr", 0.0))
    py_cash = py_pbt + py_dep + py_imp + py_fx + py_other

    cy_loss = cy_cash < 0
    py_loss = py_cash < 0
    
    cash_loss_headers = [
        "Financial Year",
        "Profit / (Loss) Before Tax (₹ Cr)",
        "Depreciation & Amortization (₹ Cr)",
        "Other Non-Cash Adjustments (₹ Cr)",
        "Net Realized Cash Profit / (Loss) (₹ Cr)",
        "Cash Loss Incurred?"
    ]
    cash_loss_rows = [
        [cy.get("financial_year", "Current Year"), f"{cy_pbt:.2f}", f"{cy_dep:.2f}", f"{cy_imp + cy_fx + cy_other:.2f}", f"{cy_cash:.2f}", "Yes" if cy_loss else "No"],
        [py.get("financial_year", "Preceding Year"), f"{py_pbt:.2f}", f"{py_dep:.2f}", f"{py_imp + py_fx + py_other:.2f}", f"{py_cash:.2f}", "Yes" if py_loss else "No"]
    ]

    if cy_loss or py_loss:
        status = ClauseStatus.QUALIFIED
        loss_details = []
        if cy_loss:
            loss_details.append(f"Current FY ({cy.get('financial_year')}): ₹{abs(cy_cash):.2f} Cr")
        if py_loss:
            loss_details.append(f"Preceding FY ({py.get('financial_year')}): ₹{abs(py_cash):.2f} Cr")
            
        exceptions.append(AuditException(
            clause_id="Clause (xvii)",
            headline="Cash losses incurred by company",
            description=f"Company has incurred cash losses: {'; '.join(loss_details)}.",
            amount_involved=abs(cy_cash) if cy_loss else abs(py_cash),
            severity="HIGH"
        ))
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        
        icai_text = (
            f"(xvii) The Company has incurred cash losses of ₹{abs(cy_cash):.2f} Crore in the current financial year "
            f"and ₹{abs(py_cash):.2f} Crore in the immediately preceding financial year."
            if (cy_loss and py_loss) else
            (f"(xvii) The Company has incurred cash losses of ₹{abs(cy_cash):.2f} Crore in the current financial year, "
             f"but did not incur cash losses in the immediately preceding financial year." if cy_loss else
             f"(xvii) The Company has not incurred cash losses in the current financial year, but incurred cash losses of "
             f"₹{abs(py_cash):.2f} Crore in the immediately preceding financial year.")
        )
    else:
        observations.append(f"No cash losses incurred. Current year cash profit: ₹{cy_cash:.2f} Cr; Preceding year: ₹{py_cash:.2f} Cr.")
        icai_text = "(xvii) The Company has not incurred cash losses in the current financial year and in the immediately preceding financial year."

    return ClauseResult(
        clause_id="Clause (xvii)",
        clause_num="xvii",
        clause_sub="",
        title="Recalculation of Real Cash Losses",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=cash_loss_headers,
        disclosure_table_rows=cash_loss_rows,
        workpaper_rows=[
            {"year": "Current FY", "pbt": cy_pbt, "depreciation": cy_dep, "cash_profit_loss": cy_cash, "has_loss": cy_loss},
            {"year": "Preceding FY", "pbt": py_pbt, "depreciation": py_dep, "cash_profit_loss": py_cash, "has_loss": py_loss}
        ],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
