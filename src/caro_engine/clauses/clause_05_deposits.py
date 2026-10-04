"""
Substantive Audit Testing Module: Clause (v) - Public Deposits & Deemed Deposits
Statutory Reference: CARO 2020 Clause 3(v) / Sections 73 to 76 of Companies Act, 2013 / RBI Directives
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_05_deposits(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_v_public_deposits", {})
    
    substantive_tests = [
        "Inquired into the existence of any public deposit schemes or unsecured loans falling under deemed deposits per Rule 2(1)(c) of Companies (Acceptance of Deposits) Rules, 2014.",
        "Verified compliance with Sections 73 to 76 regarding deposit repayment reserve, credit rating, and circulars.",
        "Scanned for any orders passed by CLB, NCLT, RBI, or any Court concerning public deposits."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.DOCUMENT_INSPECTED]
    status = ClauseStatus.CLEAN
    
    has_deposits = gov.get("has_accepted_public_deposits", False)
    rbi_complied = gov.get("directives_issued_by_rbi_complied", True)
    s73_complied = gov.get("provisions_of_sections_73_to_76_complied", True)
    orders_pending = gov.get("clb_or_nclt_orders_outstanding", False)
    remarks = gov.get("remarks", "")
    
    if not has_deposits:
        icai_text = "(v) In our opinion and according to the information and explanations given to us, the Company has not accepted any deposits or amounts which are deemed to be deposits within the meaning of Sections 73 to 76 of the Act and the rules framed thereunder. Accordingly, clause 3(v) of the Order is not applicable."
        observations.append("No public deposits or deemed deposits accepted by the company.")
    else:
        if not rbi_complied or not s73_complied or orders_pending:
            status = ClauseStatus.QUALIFIED
            exceptions.append(AuditException(
                clause_id="Clause (v)",
                headline="Non-compliance with Deposit Rules / Sections 73 to 76",
                description=remarks or "Non-compliance observed in relation to acceptance of public deposits.",
                severity="HIGH"
            ))
            tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
            icai_text = f"(v) The Company has accepted deposits, but non-compliances were observed: {remarks}"
        else:
            observations.append("Public deposits accepted in compliance with Sections 73 to 76 and RBI directives.")
            icai_text = "(v) In our opinion and according to the information and explanations given to us, the Company has complied with the directives issued by the Reserve Bank of India and the provisions of Sections 73 to 76 of the Act."

    return ClauseResult(
        clause_id="Clause (v)",
        clause_num="v",
        clause_sub="",
        title="Public Deposits & Deemed Deposits (Sections 73 to 76)",
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
