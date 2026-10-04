"""
Substantive Audit Testing Module: Clause (viii) - Undisclosed Income Surrendered in Tax Assessments
Statutory Reference: CARO 2020 Clause 3(viii) / Income Tax Act, 1961 (Sections 132, 133A, 153A, 158BD)
"""

from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark

def test_clause_08_undisclosed_income(data: Dict[str, Any]) -> ClauseResult:
    gov = data.get("governance_check_responses", {}).get("clause_viii_undisclosed_income", {})
    
    substantive_tests = [
        "Inquired of management, tax counsel, and inspected Income Tax assessment orders / search & survey files.",
        "Scanned for any surrender of income made under Section 132 or Section 133A of the Income-tax Act, 1961.",
        "Verified whether any previously unrecorded income surrendered during tax proceedings was recognized in the audited books of account during the year."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT]
    status = ClauseStatus.CLEAN
    
    has_surrendered = gov.get("unrecorded_transactions_surrendered_as_income", False)
    recorded_in_books = gov.get("previously_unrecorded_income_recorded_in_books", False)
    remarks = gov.get("remarks", "")
    
    if not has_surrendered:
        observations.append("No unrecorded transactions surrendered or disclosed as income in tax assessments during the year.")
        icai_text = (
            "(viii) According to the information and explanations given to us and on the basis of our examination of the records of the Company, "
            "the Company has not surrendered or disclosed any transactions, previously unrecorded as income in the books of account, "
            "in the tax assessments under the Income Tax Act, 1961 as income during the year."
        )
    else:
        if not recorded_in_books:
            status = ClauseStatus.QUALIFIED
            exceptions.append(AuditException(
                clause_id="Clause (viii)",
                headline="Undisclosed income surrendered in tax assessment NOT recorded in books",
                description=remarks or "Transactions surrendered as income during tax assessment were not recorded in the books of account.",
                severity="CRITICAL"
            ))
            tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
            icai_text = (
                f"(viii) According to the information and explanations given to us, the Company has surrendered or disclosed transactions as income during the year in tax assessments: {remarks} "
                "However, such previously unrecorded income has NOT been properly recorded in the books of account during the year."
            )
        else:
            status = ClauseStatus.OBSERVATION
            observations.append("Undisclosed income surrendered in tax assessments has been duly recorded in the books of account.")
            icai_text = (
                f"(viii) According to the information and explanations given to us, the Company surrendered or disclosed transactions as income during the year in tax assessments: {remarks} "
                "Such previously unrecorded income has been properly recorded in the books of account during the year."
            )

    return ClauseResult(
        clause_id="Clause (viii)",
        clause_num="viii",
        clause_sub="",
        title="Undisclosed Income Surrendered in Tax Assessments",
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
