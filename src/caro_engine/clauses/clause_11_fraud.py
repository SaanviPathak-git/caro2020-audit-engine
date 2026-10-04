"""
Substantive Audit Testing Module: Clause (xi) - Fraud Reporting & Whistleblower Complaints
Statutory Reference: CARO 2020 Clause 3(xi)(a)-(c) / Section 143(12) / Form ADT-4 / SA 240
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_11_fraud(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_xi_fraud_reporting", {})
    
    substantive_tests = [
        "Inquired of management, Audit Committee, Internal Audit and vigil mechanism officers regarding suspected or actual fraud per SA 240.",
        "Inspected Audit Committee minutes and whistleblower complaints register for the financial year.",
        "Verified whether any fraud involving amount of ₹1 Crore or more was reported to Central Government in Form ADT-4 under Section 143(12).",
        "Considered all whistleblower complaints received by the company and assessed their financial reporting impact."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    fraud_by = gov.get("fraud_by_company_noticed_or_reported", False)
    fraud_on = gov.get("fraud_on_company_noticed_or_reported", False)
    adt4_filed = gov.get("form_adt4_filed_with_central_govt", False)
    wb_count = gov.get("whistleblower_complaints_received", 0)
    wb_considered = gov.get("whistleblower_complaints_considered_by_auditor", True)
    audit_text = gov.get("substantive_audit_check", "")
    
    if fraud_by or fraud_on:
        status = ClauseStatus.QUALIFIED
        exceptions.append(AuditException(
            clause_id="Clause (xi)(a)",
            headline="Fraud noticed or reported during the year",
            description=audit_text or "Fraud noticed or reported on/by the company during the year.",
            severity="CRITICAL"
        ))
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        
    if adt4_filed:
        if status != ClauseStatus.QUALIFIED:
            status = ClauseStatus.QUALIFIED
        exceptions.append(AuditException(
            clause_id="Clause (xi)(b)",
            headline="Report filed in Form ADT-4 under Section 143(12)",
            description="The statutory auditor filed Form ADT-4 with the Central Government regarding fraud.",
            severity="CRITICAL"
        ))
        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

    observations.append(f"Considered {wb_count} whistle-blower complaints received by the Company during the year per Clause 3(xi)(c).")

    if status == ClauseStatus.CLEAN:
        icai_text = (
            "(xi) (a) According to the information and explanations given to us, no fraud by the Company or any fraud on the Company has been noticed or reported during the year.\n"
            "(b) No report under sub-section (12) of Section 143 of the Companies Act, 2013 has been filed by the auditors in Form ADT-4 as prescribed under Rule 13 of Companies (Audit and Auditors) Rules, 2014 with the Central Government during the year.\n"
            f"(c) As represented to us by the management, {wb_count} whistle-blower complaints were received by the Company during the year and were investigated and considered by us while determining the nature, timing and extent of our audit procedures."
        )
    else:
        icai_text = (
            f"(xi) (a) According to the information and explanations given to us, fraud on/by the Company has been noticed or reported: {audit_text}\n"
            f"(b) A report under sub-section (12) of Section 143 of the Companies Act in Form ADT-4 has been filed with the Central Government during the year.\n"
            f"(c) We have taken into consideration {wb_count} whistle-blower complaints received by the Company during the year."
        )

    return ClauseResult(
        clause_id="Clause (xi)",
        clause_num="xi",
        clause_sub="(a)-(c)",
        title="Fraud Reporting & Whistleblower Complaints (Section 143(12))",
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
