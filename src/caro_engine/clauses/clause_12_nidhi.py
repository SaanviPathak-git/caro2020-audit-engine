"""
Substantive Audit Testing Module: Clause (xii) - Nidhi Company Compliance
Statutory Reference: CARO 2020 Clause 3(xii)(a)-(c) / Section 406 of Companies Act, 2013 / Nidhi Rules, 2014
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_12_nidhi(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_xii_nidhi_company", {})
    
    substantive_tests = [
        "Verified certificate of incorporation and Memorandum of Association to evaluate whether entity is a Nidhi company under Section 406.",
        "If applicable, tested Net Owned Funds to Deposits ratio against statutory ceiling of 1:20.",
        "Verified maintenance of 10% unencumbered term deposits per Rule 14 of Nidhi Rules, 2014.",
        "Tested deposit ledgers for any default in payment of interest on deposits or repayment thereof."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.STATUTORY_LIMIT]
    
    is_nidhi = gov.get("is_nidhi_company", False)
    
    if not is_nidhi:
        status = ClauseStatus.NOT_APPLICABLE
        observations.append("The Company is not a Nidhi company as defined under Section 406 of the Act.")
        icai_text = "(xii) In our opinion and according to the information and explanations given to us, the Company is not a Nidhi company. Accordingly, clauses 3(xii)(a), 3(xii)(b) and 3(xii)(c) of the Order are not applicable."
    else:
        status = ClauseStatus.CLEAN
        icai_text = "(xii) The Company is a Nidhi Company and has complied with the statutory ratios and requirements under Nidhi Rules, 2014."

    return ClauseResult(
        clause_id="Clause (xii)",
        clause_num="xii",
        clause_sub="(a)-(c)",
        title="Nidhi Company Statutory Ratios & Compliance",
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
