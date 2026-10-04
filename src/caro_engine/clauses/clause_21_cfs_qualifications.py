"""
Substantive Audit Testing Module: Clause (xxi) - Group CARO Qualifications in Consolidated Financial Statements
Statutory Reference: CARO 2020 Clause 3(xxi) / Guidance Note on CARO 2020 / SA 600
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_21_cfs_qualifications(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_xxi_cfs_qualifications", {})
    meta = data.get("metadata")
    is_cfs = str(getattr(meta, "standalone_or_consolidated", "Standalone")).strip().lower() == "consolidated"
    
    substantive_tests = [
        "Identified all group components (subsidiaries, joint ventures, and associates) included in Consolidated Financial Statements per SA 600.",
        "Obtained and inspected independent auditor's reports and CARO 2020 annexures of each group component.",
        "Extracted all qualifications, adverse remarks, and disclaimers issued by component auditors.",
        "Compiled mandatory statutory disclosure table specifying company names, CIN, and CARO paragraph numbers."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    cfs_headers = [
        "Sr. No.",
        "Name of the Group Company",
        "CIN",
        "Relationship",
        "Clause / Paragraph No. of CARO Report Containing Qualification"
    ]
    cfs_rows = []
    
    if not is_cfs:
        status = ClauseStatus.NOT_APPLICABLE
        observations.append("Clause 3(xxi) is applicable only to Consolidated Financial Statements. This audit engagement is for Standalone Financial Statements.")
        icai_text = (
            "(xxi) The reporting under clause 3(xxi) of the Order is applicable only in respect of Consolidated Financial Statements. "
            "Accordingly, this clause is not applicable to the Standalone Financial Statements of the Company."
        )
    else:
        quals = gov.get("subsidiary_caro_qualifications", [])
        if not quals:
            observations.append("No qualifications or adverse remarks reported by respective auditors in CARO reports of group components.")
            icai_text = (
                "(xxi) According to the information and explanations given to us and based on the CARO reports issued by the respective "
                "auditors of subsidiaries, associates and joint ventures included in the consolidated financial statements, there are no qualifications "
                "or adverse remarks by the respective auditors in the CARO reports of the said companies."
            )
        else:
            status = ClauseStatus.QUALIFIED
            for idx, q in enumerate(quals, 1):
                cfs_rows.append([
                    str(idx),
                    q.get("company_name", ""),
                    q.get("cin", ""),
                    q.get("relationship", ""),
                    q.get("caro_paragraph", "")
                ])
                exceptions.append(AuditException(
                    clause_id="Clause (xxi)",
                    headline=f"CARO qualification in component {q.get('company_name')}",
                    description=f"Auditor of {q.get('company_name')} reported qualification in {q.get('caro_paragraph')}.",
                    severity="HIGH"
                ))
            tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
            icai_text = (
                "(xxi) According to the information and explanations given to us and based on the CARO reports issued by the respective "
                "auditors of the companies included in the consolidated financial statements, qualifications or adverse remarks have been reported "
                "by respective auditors as detailed below:\n"
            )

    return ClauseResult(
        clause_id="Clause (xxi)",
        clause_num="xxi",
        clause_sub="",
        title="CARO Qualifications in Consolidated Financial Statements",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=cfs_headers if cfs_rows else [],
        disclosure_table_rows=cfs_rows if cfs_rows else [],
        workpaper_rows=cfs_rows,
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
