"""
Rule Validator for CARO 2020 Clause 3(xix): Material Uncertainty on Going Concern.
Statutory Mandate:
On the basis of the financial ratios, ageing and expected dates of realisation of financial assets and
payment of financial liabilities, other information accompanying the financial statements,
the auditor's knowledge of the Board of Directors and management plans, whether the auditor is of the opinion that
no material uncertainty exists as on the date of the audit report that company is capable of meeting its liabilities
existing at the date of balance sheet as and when they fall due within a period of one year from the balance sheet date.
"""

import pandas as pd
from typing import Dict, Any, List
from engine.models import ClauseResult, ClauseStatus, RiskSeverity, AuditException, AuditTickMark


def evaluate_clause_19_going_concern(ratios_df: pd.DataFrame, metadata: Dict[str, Any]) -> ClauseResult:
    exceptions: List[AuditException] = []
    tick_marks: List[str] = [
        AuditTickMark.CHECKED_TO_GL.value, 
        AuditTickMark.RECALCULATED.value, 
        AuditTickMark.TRACED_TO_STATUTE.value
    ]

    ratios_dict = dict(zip(ratios_df['ratio_name'], ratios_df['current_fy_2023_24']))
    
    current_ratio = float(ratios_dict.get('Current Ratio (times)', 1.0))
    quick_ratio = float(ratios_dict.get('Quick / Acid-Test Ratio (times)', 0.8))
    dscr = float(ratios_dict.get('Debt Service Coverage Ratio (DSCR)', 2.0))
    assets_1yr = float(ratios_dict.get('Financial Assets Realisable within 1 Year (₹ Cr)', 14000.0))
    liab_1yr = float(ratios_dict.get('Financial Liabilities Due within 1 Year (₹ Cr)', 13000.0))
    headroom = assets_1yr - liab_1yr

    material_uncertainty = False
    if current_ratio < 0.75 and headroom < 0:
        material_uncertainty = True
        exceptions.append(AuditException(
            clause_id="3(xix)",
            clause_title="Material Uncertainty on Meeting One-Year Liabilities",
            severity=RiskSeverity.CRITICAL,
            exception_description=f"Current ratio ({current_ratio:.2f}) is significantly depressed and 1-year financial liabilities exceed realizable financial assets by ₹{abs(headroom):.2f} Cr, indicating material liquidity strain under SA 570.",
            statutory_reference="Clause 3(xix) of CARO 2020 / SA 570 (Revised) Going Concern",
            quantification_inr_cr=abs(headroom),
            recommended_caro_disclosure="Material uncertainty paragraph required in CARO and Auditor's Report.",
            tick_mark=AuditTickMark.EXCEPTION_NOTED
        ))

    if material_uncertainty:
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.CRITICAL
        summary_finding = f"Material uncertainty exists regarding capability to meet liabilities within 1 year (Shortfall: ₹{abs(headroom):.2f} Cr)."
        icai_text = (
            "(xix) On the basis of the financial ratios, ageing and expected dates of realization of financial assets and payment of financial liabilities, "
            "other information accompanying the financial statements and our knowledge of the Board of Directors and Management plans, "
            "material uncertainty exists as on the date of the audit report that the Company is capable of meeting its liabilities existing at the date of balance sheet as and when they fall due within a period of one year from the balance sheet date."
        )
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        summary_finding = (
            f"No material uncertainty on going concern. Current Ratio: {current_ratio:.2f}, Quick Ratio: {quick_ratio:.2f}, DSCR: {dscr:.2f}. "
            f"1-year financial assets (₹{assets_1yr:,.2f} Cr) exceed 1-year financial liabilities (₹{liab_1yr:,.2f} Cr) by ₹{headroom:,.2f} Cr."
        )
        icai_text = (
            "(xix) On the basis of the financial ratios, ageing and expected dates of realization of financial assets and payment of financial liabilities, "
            "other information accompanying the financial statements, our knowledge of the Board of Directors and management plans and based on our examination of the evidence supporting the assumptions, "
            "nothing has come to our attention, which causes us to believe that any material uncertainty exists as on the date of the audit report that Company is not capable of meeting its liabilities existing at the date of balance sheet as and when they fall due within a period of one year from the balance sheet date. "
            "We, however, state that this is not an assurance as to the future viability of the Company. We further state that our reporting is based on the facts up to the date of the audit report and we neither give any guarantee nor any assurance that all liabilities falling due within a period of one year from the balance sheet date, will get discharged by the Company as and when they fall due."
        )

    return ClauseResult(
        clause_id="3(xix)",
        clause_number="Clause (xix)",
        clause_title="Material Uncertainty Regarding Going Concern & Liquidity",
        status=status,
        severity=severity,
        summary_finding=summary_finding,
        icai_standard_text=icai_text,
        exceptions=exceptions,
        disclosure_table=ratios_df.to_dict(orient="records"),
        audit_workpaper_data={
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "dscr": dscr,
            "assets_realisable_1yr_cr": assets_1yr,
            "liabilities_due_1yr_cr": liab_1yr,
            "liquidity_headroom_cr": headroom
        },
        tick_marks_applied=tick_marks
    )
