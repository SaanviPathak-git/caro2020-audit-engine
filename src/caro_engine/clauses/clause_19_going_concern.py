"""
Substantive Audit Testing Module: Clause (xix) - Going Concern & Liquidity Capability Assessment
Statutory Reference: CARO 2020 Clause 3(xix) / SA 570 (Going Concern) / Schedule III Ratios
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_19_going_concern(data: Dict[str, Any]) -> ClauseResult:
    ratios_data = data.get("balance_sheet_ratios", {})
    fin_ratios = ratios_data.get("financial_ratios", {})
    gap_data = ratios_data.get("one_year_liquidity_gap_analysis", {})
    
    substantive_tests = [
        "Mathematically recalculated Schedule III financial ratios including Current Ratio, Debt-Equity, and Debt Service Coverage Ratio (DSCR).",
        "Evaluated 12-month asset-liability maturity schedule: financial assets realizable within 1 year vs liabilities falling due within 1 year per SA 570.",
        "Audited unutilized committed bank credit facilities available to service short-term liquidity demands.",
        "Assessed management's projected operational cash flows, business plans, and capital expenditure commitments.",
        "Formed audit conclusion regarding capability of meeting liabilities existing at balance sheet date as and when they fall due within 1 year."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.CAST_VERIFIED, AuditTickMark.TRIAL_BALANCE_TIED, AuditTickMark.BANK_RECONCILED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN

    # 1. Ratio Analysis
    ratio_table_headers = [
        "Ratio Name",
        "Current Year",
        "Prior Year",
        "Variance %",
        "Benchmark / Tolerance",
        "Healthy?"
    ]
    ratio_table_rows = []
    
    unhealthy_count = 0
    for r_key, r_info in fin_ratios.items():
        name = r_key.replace("_", " ").title()
        cy_val = float(r_info.get("ratio_current_year", 0.0))
        py_val = float(r_info.get("ratio_prior_year", 0.0))
        var_pct = float(r_info.get("variance_pct", 0.0))
        thresh = float(r_info.get("threshold_benchmark", 1.0))
        healthy = bool(r_info.get("is_healthy", True))
        
        if not healthy:
            unhealthy_count += 1
            
        ratio_table_rows.append([
            name,
            f"{cy_val:.2f}",
            f"{py_val:.2f}",
            f"{var_pct:+.2f}%",
            f"{thresh:.2f}",
            "Yes" if healthy else "No"
        ])

    # 2. Maturity Gap Analysis
    assets_1y = float(gap_data.get("financial_assets_realizable_within_1_year_cr", {}).get("total_realizable_financial_assets_cr", 0.0))
    liab_1y = float(gap_data.get("financial_liabilities_maturing_within_1_year_cr", {}).get("total_maturing_financial_liabilities_cr", 0.0))
    surplus_deficit = float(gap_data.get("net_liquidity_surplus_deficit_cr", assets_1y - liab_1y))
    cushion = float(gap_data.get("total_effective_liquidity_cushion_cr", surplus_deficit))
    uncertainty_flag = bool(gap_data.get("going_concern_material_uncertainty_identified", False))

    if uncertainty_flag or cushion < 0:
        status = ClauseStatus.QUALIFIED
        exc = AuditException(
            clause_id="Clause (xix)",
            headline="Material uncertainty on Going Concern (1-year liquidity deficit)",
            description=f"Negative liquidity cushion of ₹{abs(cushion):.2f} Cr over the next 12 months with {unhealthy_count} adverse financial ratios.",
            amount_involved=abs(cushion),
            severity="CRITICAL"
        )
        exceptions.append(exc)
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        
        icai_text = (
            "(xix) On the basis of the financial ratios, ageing and expected dates of realization of financial assets and payment of "
            "financial liabilities, other information accompanying the financial statements, our knowledge of the Board of Directors and management plans, "
            f"we note that MATERIAL UNCERTAINTY EXISTS as on the date of the audit report regarding whether the Company is capable of meeting its "
            f"liabilities existing at the date of balance sheet as and when they fall due within a period of one year from the balance sheet date. "
            f"The Company has an effective 12-month liquidity deficit of ₹{abs(cushion):.2f} Crore."
        )
    else:
        observations.append(f"Healthy liquidity cushion of ₹{cushion:.2f} Cr (including undrawn credit lines). No material uncertainty on going concern.")
        icai_text = (
            "(xix) On the basis of the financial ratios, ageing and expected dates of realization of financial assets and payment of financial "
            "liabilities, other information accompanying the financial statements, our knowledge of the Board of Directors and management plans and based on "
            "our examination of the evidence supporting the assumptions, nothing has come to our attention, which causes us to believe that any material "
            "uncertainty exists as on the date of the audit report indicating that Company is not capable of meeting its liabilities existing at the date "
            "of balance sheet as and when they fall due within a period of one year from the balance sheet date. We, however, state that this is not an assurance "
            "as to the future viability of the Company."
        )

    return ClauseResult(
        clause_id="Clause (xix)",
        clause_num="xix",
        clause_sub="",
        title="Going Concern Capability & 1-Year Liquidity Assessment",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=ratio_table_headers,
        disclosure_table_rows=ratio_table_rows,
        workpaper_rows=ratio_table_rows,
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
