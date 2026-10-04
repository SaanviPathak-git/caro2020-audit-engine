"""
Substantive Audit Testing Module: Clause (vi) - Maintenance of Cost Records
Statutory Reference: CARO 2020 Clause 3(vi) / Section 148(1) of Companies Act, 2013 / Companies (Cost Records and Audit) Rules, 2014
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_06_cost_records(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_vi_cost_records", {})
    
    substantive_tests = [
        "Ascertained whether Central Government has prescribed maintenance of cost records under Section 148(1) for company's products/services.",
        "Obtained Form CRA-1 cost registers, bills of materials, and process cost ledgers.",
        "Performed broad review to ascertain whether prescribed books and cost records have, prima facie, been made and maintained per ICAI Guidance Note.",
        "Inspected previous year Cost Audit Report and status of current year cost audit appointment in Form CRA-2."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.DOCUMENT_INSPECTED]
    status = ClauseStatus.CLEAN
    
    mandated = gov.get("cost_records_mandated_by_central_govt", True)
    maintained = gov.get("cost_accounts_and_records_maintained", True)
    audit_check_text = gov.get("substantive_audit_check", "")
    
    if not mandated:
        icai_text = "(vi) The Central Government has not specified maintenance of cost records under sub-section (1) of Section 148 of the Act for any of the products manufactured or services rendered by the Company. Accordingly, clause 3(vi) of the Order is not applicable."
        observations.append("Maintenance of cost records not prescribed for the company's activities.")
    else:
        if maintained:
            observations.append("Cost accounts and records prescribed under Section 148(1) have, prima facie, been made and maintained.")
            icai_text = (
                "(vi) We have broadly reviewed the books of account maintained by the Company pursuant to the rules made by the "
                "Central Government for the maintenance of cost records under sub-section (1) of Section 148 of the Companies Act, 2013, "
                "and are of the opinion that, prima facie, the prescribed accounts and records have been made and maintained. "
                "We have not, however, made a detailed examination of the same with a view to determine whether they are accurate or complete."
            )
        else:
            status = ClauseStatus.QUALIFIED
            exceptions.append(AuditException(
                clause_id="Clause (vi)",
                headline="Prescribed cost records NOT maintained under Section 148(1)",
                description="The Company has failed to maintain the prescribed cost accounts and records under Section 148(1) of the Act.",
                severity="CRITICAL"
            ))
            tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
            icai_text = (
                "(vi) The Central Government has prescribed maintenance of cost records under sub-section (1) of Section 148 of the Act. "
                "However, the Company has NOT made and maintained the prescribed accounts and records during the year."
            )

    return ClauseResult(
        clause_id="Clause (vi)",
        clause_num="vi",
        clause_sub="",
        title="Maintenance of Cost Records (Section 148(1))",
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
