"""
Substantive Audit Testing Module: Clause (xv) - Non-Cash Transactions with Directors
Statutory Reference: CARO 2020 Clause 3(xv) / Section 192 of Companies Act, 2013
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_15_non_cash_directors(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_xv_non_cash_transactions", {})
    
    substantive_tests = [
        "Inquired of management and inspected fixed asset registers, disposal ledgers, and property transfers.",
        "Verified whether any asset was acquired from or transferred to directors or connected persons without cash consideration per Section 192.",
        "Where non-cash transactions occurred, audited whether prior approval was obtained by a resolution in general meeting and valuation conducted by Registered Valuer."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    has_non_cash = gov.get("non_cash_transactions_with_directors", False)
    s192_complied = gov.get("provisions_of_section_192_complied", True)
    remarks = gov.get("remarks", "")
    
    if not has_non_cash:
        observations.append("The Company has not entered into any non-cash transactions with directors or connected persons.")
        icai_text = (
            "(xv) In our opinion and according to the information and explanations given to us, the Company has not entered into any non-cash "
            "transactions with its directors or persons connected with them and hence, provisions of Section 192 of the Companies Act, 2013 are not applicable."
        )
    else:
        if not s192_complied:
            status = ClauseStatus.QUALIFIED
            exceptions.append(AuditException(
                clause_id="Clause (xv)",
                headline="Non-cash transactions with directors in breach of Section 192",
                description=remarks or "Non-cash transaction entered into with director without requisite approval under Section 192.",
                severity="HIGH"
            ))
            tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
            icai_text = f"(xv) According to the information and explanations given to us, the Company has entered into non-cash transactions with directors in contravention of Section 192: {remarks}"
        else:
            observations.append("Non-cash transactions with directors complied with Section 192.")
            icai_text = "(xv) The Company entered into non-cash transactions with directors in compliance with Section 192."

    return ClauseResult(
        clause_id="Clause (xv)",
        clause_num="xv",
        clause_sub="",
        title="Non-Cash Transactions with Directors (Section 192)",
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
