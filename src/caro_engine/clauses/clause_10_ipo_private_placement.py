"""
Substantive Audit Testing Module: Clause (x) - Public Offer Moneys & Preferential Allotment
Statutory Reference: CARO 2020 Clause 3(x)(a)-(b) / Sections 42 & 62 of Companies Act, 2013 / SEBI Regulations
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_10_ipo_private_placement(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_x_ipo_preferential_allotment", {})
    
    substantive_tests = [
        "Inquired of management and inspected statutory registers regarding IPO, FPO or rights issues during the year.",
        "Verified whether moneys raised through public issues were utilized strictly for object clause stated in the prospectus / offer document.",
        "Audited compliance with Sections 42 and 62 for preferential allotment or private placement of shares or convertible debentures.",
        "Verified maintenance of application money in separate escrow bank account and filing of Form PAS-3 (Return of Allotment)."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    has_ipo = gov.get("moneys_raised_by_ipo_or_fpo", False)
    has_pref = gov.get("preferential_allotment_or_private_placement", False)
    sec_complied = gov.get("section_42_and_62_complied", True)
    purpose_ok = gov.get("funds_used_for_intended_purposes", True)
    remarks = gov.get("remarks", "")
    
    if not has_ipo and not has_pref:
        observations.append("The Company has not raised any moneys by way of initial public offer, further public offer or preferential allotment / private placement.")
        icai_text = (
            "(x) (a) The Company has not raised any moneys by way of initial public offer or further public offer (including debt instruments) during the year. Accordingly, clause 3(x)(a) of the Order is not applicable.\n"
            "(b) The Company has not made any preferential allotment or private placement of shares or convertible debentures during the year. Accordingly, clause 3(x)(b) of the Order is not applicable."
        )
    else:
        if not sec_complied or not purpose_ok:
            status = ClauseStatus.QUALIFIED
            exceptions.append(AuditException(
                clause_id="Clause (x)(b)",
                headline="Non-compliance in Preferential Allotment / Private Placement",
                description=remarks or "Preferential allotment made without full compliance with Section 42 / 62.",
                severity="HIGH"
            ))
            tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
            icai_text = (
                f"(x) (a) The Company has not raised moneys by way of IPO/FPO during the year.\n"
                f"(b) During the year, the Company made preferential allotment / private placement. However, non-compliances were identified: {remarks}"
            )
        else:
            observations.append("Moneys raised through preferential allotment were applied in compliance with Sections 42 and 62.")
            icai_text = (
                "(x) (a) Moneys raised by public offer, if any, were applied for intended purposes.\n"
                "(b) In our opinion and according to the information and explanations given to us, the Company has complied with the requirements of Sections 42 and 62 of the Companies Act, 2013 and the funds raised have been used for the purposes for which they were raised."
            )

    return ClauseResult(
        clause_id="Clause (x)",
        clause_num="x",
        clause_sub="(a)-(b)",
        title="Public Offers & Preferential Allotments (Sections 42 & 62)",
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
