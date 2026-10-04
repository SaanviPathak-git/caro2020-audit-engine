"""
Substantive Audit Testing Module: Clause (xviii) - Resignation of Statutory Auditors
Statutory Reference: CARO 2020 Clause 3(xviii) / Section 140(2) / Form ADT-3 / SA 300
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_18_auditor_resignation(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_xviii_auditor_resignation", {})
    
    substantive_tests = [
        "Inquired of management and inspected MCA ROC filings for any resignation of previous auditors under Section 140(2).",
        "Inspected Form ADT-3 filed by the resigning auditor with the Registrar of Companies.",
        "Reviewed written communication and responses from previous auditor pursuant to ICAI Code of Ethics and SA 300.",
        "Assessed whether objections or concerns raised by outgoing auditor impact current year audit risk and scope."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    has_resigned = gov.get("resignation_of_statutory_auditor_during_year", False)
    issues_raised = gov.get("issues_or_objections_raised", "None")
    
    if not has_resigned:
        observations.append("There has been no resignation of the statutory auditors during the year.")
        icai_text = "(xviii) There has been no resignation of the statutory auditors during the year. Accordingly, clause 3(xviii) of the Order is not applicable."
    else:
        status = ClauseStatus.OBSERVATION
        observations.append(f"Statutory auditor resigned during the year. Concerns considered: {issues_raised}.")
        icai_text = (
            f"(xviii) There has been resignation of the statutory auditors during the year and we have taken into consideration "
            f"the issues, objections or concerns raised by the outgoing auditor: {issues_raised}"
        )

    return ClauseResult(
        clause_id="Clause (xviii)",
        clause_num="xviii",
        clause_sub="",
        title="Resignation of Statutory Auditors (Section 140(2) & SA 300)",
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
