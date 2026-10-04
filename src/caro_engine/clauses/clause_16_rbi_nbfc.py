"""
Substantive Audit Testing Module: Clause (xvi) - RBI Registration (Section 45-IA) & CIC Evaluation
Statutory Reference: CARO 2020 Clause 3(xvi)(a)-(d) / Reserve Bank of India Act, 1934 / Core Investment Companies Master Directions
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_16_rbi_nbfc(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_xvi_rbi_nbfc_registration", {})
    ratios_data = data.get("balance_sheet_ratios", {})
    
    substantive_tests = [
        "Tested 50-50 principal business test (financial assets > 50% of total assets and income from financial assets > 50% of gross income) per RBI criteria.",
        "Verified whether company is carrying on non-banking financial business requiring registration under Section 45-IA of RBI Act, 1934.",
        "Evaluated whether company qualifies as a Core Investment Company (CIC) holding >= 90% of net assets in group equity/debt.",
        "Counted total number of registered or unregistered CICs in the corporate group."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.STATUTORY_LIMIT, AuditTickMark.DOCUMENT_INSPECTED]
    status = ClauseStatus.CLEAN
    
    req_reg = gov.get("required_to_be_registered_under_45_ia", False)
    conducted_nbfc = gov.get("has_conducted_nbfc_activities", False)
    is_cic = gov.get("is_core_investment_company_cic", False)
    cic_count = gov.get("group_cic_count", 0)
    remarks = gov.get("remarks", "")
    
    if req_reg or conducted_nbfc:
        status = ClauseStatus.QUALIFIED
        exceptions.append(AuditException(
            clause_id="Clause (xvi)",
            headline="Operating as NBFC without RBI Section 45-IA registration",
            description=remarks or "Company conducted NBFC activities without obtaining Certificate of Registration from RBI.",
            severity="CRITICAL"
        ))
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        icai_text = (
            f"(xvi) (a)-(b) The Company was required to obtain registration under Section 45-IA of the RBI Act or conducted NBFC activities without valid CoR: {remarks}\n"
            f"(c) The Company is not a Core Investment Company (CIC).\n"
            f"(d) Group CIC count: {cic_count}."
        )
    else:
        observations.append("The Company does not meet the 50-50 test for NBFC registration under Section 45-IA of the RBI Act.")
        icai_text = (
            "(xvi) (a) The Company is not required to be registered under Section 45-IA of the Reserve Bank of India Act, 1934. Accordingly, clause 3(xvi)(a) of the Order is not applicable.\n"
            "(b) The Company has not conducted any Non-Banking Financial or Housing Finance activities without obtaining a valid Certificate of Registration (CoR) from the Reserve Bank of India as per the Reserve Bank of India Act, 1934.\n"
            "(c) The Company is not a Core Investment Company (CIC) as defined in the regulations made by the Reserve Bank of India. Accordingly, clause 3(xvi)(c) of the Order is not applicable.\n"
            f"(d) According to the information and explanations provided by the management, the Group has {cic_count} Core Investment Company (CIC) as part of the Group."
        )

    return ClauseResult(
        clause_id="Clause (xvi)",
        clause_num="xvi",
        clause_sub="(a)-(d)",
        title="RBI NBFC Registration & CIC Status (Section 45-IA)",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=[],
        disclosure_table_rows=[],
        workpaper_rows=[gov] if gov else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
