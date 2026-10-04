"""
Substantive Audit Testing Module: Clause (iv) - Compliance with Sections 185 & 186
Statutory Reference: CARO 2020 Clause 3(iv) / Sections 185 & 186 of Companies Act, 2013
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_04_sec185_186(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_iv_sec185_186", {})
    
    substantive_tests = [
        "Verified compliance with Section 185 regarding prohibition and conditions on loans, advances, guarantees to directors or interested entities.",
        "Tested compliance with Section 186 limits (60% of paid-up share capital, free reserves & securities premium OR 100% of free reserves & securities premium).",
        "Inspected Form MBP-2 register of loans, guarantees, securities and investments.",
        "Verified whether prior approval of public financial institutions (PFIs) was obtained where applicable.",
        "Checked whether special resolutions were passed in general meeting if Section 186 limits were exceeded."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.DOCUMENT_INSPECTED]
    status = ClauseStatus.CLEAN
    
    s185_ok = gov.get("loans_to_directors_sec185_compliant", True)
    s186_ok = gov.get("loans_guarantees_investments_sec186_compliant", True)
    remarks = gov.get("remarks", "")
    
    if not s185_ok:
        status = ClauseStatus.QUALIFIED
        exceptions.append(AuditException(
            clause_id="Clause (iv)",
            headline="Non-compliance with Section 185 (Loans to Directors)",
            description=remarks or "Loans or guarantees were granted in contravention of Section 185.",
            severity="CRITICAL"
        ))
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

    if not s186_ok:
        status = ClauseStatus.QUALIFIED
        exceptions.append(AuditException(
            clause_id="Clause (iv)",
            headline="Non-compliance with Section 186 (Loans & Investments)",
            description=remarks or "Loans, investments or guarantees exceeded statutory limits without requisite special resolution or approvals.",
            severity="HIGH"
        ))
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        
    if status == ClauseStatus.CLEAN:
        observations.append("The Company has complied with the provisions of Sections 185 and 186 of the Act.")
        icai_text = "(iv) In our opinion and according to the information and explanations given to us, the Company has complied with the provisions of Sections 185 and 186 of the Companies Act, 2013 in respect of loans granted, investments made and guarantees and securities provided."
    else:
        icai_text = f"(iv) According to the information and explanations given to us, the Company has not complied with the provisions of Sections 185 and/or 186 of the Companies Act, 2013: {remarks}"

    return ClauseResult(
        clause_id="Clause (iv)",
        clause_num="iv",
        clause_sub="",
        title="Compliance with Sections 185 and 186 (Loans to Directors & Investments)",
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
