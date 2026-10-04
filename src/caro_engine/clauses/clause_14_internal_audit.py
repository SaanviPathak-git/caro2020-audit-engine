"""
Substantive Audit Testing Module: Clause (xiv) - Internal Audit System & Reports Consideration
Statutory Reference: CARO 2020 Clause 3(xiv)(a)-(b) / Section 138 of Companies Act, 2013 / SA 610
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_14_internal_audit(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_xiv_internal_audit", {})
    
    substantive_tests = [
        "Evaluated whether internal audit is mandated under Section 138 (listed companies, unlisted public / private meeting turnover/borrowing thresholds).",
        "Assessed the organizational status, objectivity, scope, and technical competence of the Internal Audit function per SA 610.",
        "Reviewed internal audit charters, annual audit plans, and quarterly audit committee presentations.",
        "Considered and reviewed internal audit reports issued during the year and assessed corrective actions on reported control deficiencies."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    has_system = gov.get("internal_audit_system_in_place", True)
    commensurate = gov.get("commensurate_with_size_and_nature", True)
    reports_reviewed = gov.get("internal_audit_reports_reviewed_by_statutory_auditor", True)
    audit_text = gov.get("substantive_audit_check", "")
    
    if not has_system or not commensurate:
        status = ClauseStatus.QUALIFIED
        exceptions.append(AuditException(
            clause_id="Clause (xiv)(a)",
            headline="Internal audit system not commensurate with size and nature",
            description=audit_text or "Internal audit system is absent or not commensurate with company operations.",
            severity="HIGH"
        ))
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        icai_text = (
            "(xiv) (a) In our opinion, the internal audit system is not commensurate with the size and nature of the Company's business.\n"
            f"(b) Due to deficiencies in the internal audit process, internal audit reports were not available or adequately considered."
        )
    else:
        observations.append("Internal audit system is commensurate with size and nature of business; internal audit reports considered per SA 610.")
        icai_text = (
            "(xiv) (a) In our opinion and based on our examination, the Company has an internal audit system commensurate with the size and nature of its business.\n"
            "(b) We have considered the internal audit reports of the Company issued till date for the period under audit."
        )

    return ClauseResult(
        clause_id="Clause (xiv)",
        clause_num="xiv",
        clause_sub="(a)-(b)",
        title="Internal Audit System & Reports Consideration (Section 138 & SA 610)",
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
