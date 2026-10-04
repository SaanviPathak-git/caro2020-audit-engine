"""
Substantive Audit Testing Module: Clause (xx) - Corporate Social Responsibility (CSR) Compliance
Statutory Reference: CARO 2020 Clause 3(xx)(a)-(b) / Section 135(5) & 135(6) of Companies Act, 2013 / Companies (CSR Policy) Rules, 2014
"""

import pandas as pd
from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_20_csr(data: Dict[str, Any]) -> ClauseResult:
    csr_df: pd.DataFrame = data.get("csr_schedule", pd.DataFrame())
    
    substantive_tests = [
        "Mathematically recalculated 2% CSR obligation based on average net profits of preceding 3 financial years per Section 198.",
        "Audited actual CSR disbursements against approved CSR Committee projects and verified implementation agency registrations.",
        "Tested unspent amounts for Ongoing Projects: verified transfer to Special Unspent CSR Account within 30 days of FY-end per Section 135(6).",
        "Tested unspent amounts for Other than Ongoing Projects: verified transfer to Schedule VII specified Fund (PM CARES / Clean Ganga) within 6 months per Section 135(5)."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.CAST_VERIFIED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.TRIAL_BALANCE_TIED]
    status = ClauseStatus.CLEAN

    csr_table_headers = [
        "Financial Year",
        "Statutory 2% Obligation (₹ Cr)",
        "Actual Amount Spent (₹ Cr)",
        "Unspent on Ongoing Projects (₹ Cr)",
        "Unspent on Other Projects (₹ Cr)",
        "Compliance Status"
    ]
    csr_table_rows = []

    if not csr_df.empty:
        for _, row in csr_df.iterrows():
            fy = str(row.get("financial_year", ""))
            oblg = float(row.get("statutory_2pct_obligation_cr", 0.0))
            spent = float(row.get("actual_csr_spent_cr", 0.0))
            unspent_on = float(row.get("unspent_ongoing_projects_cr", 0.0))
            unspent_oth = float(row.get("unspent_other_projects_cr", 0.0))
            trans_spec = str(row.get("transferred_to_special_unspent_bank_account", "")).strip().lower()
            trans_fund = str(row.get("transferred_to_schedule_vii_fund", "")).strip().lower()
            
            comp_status = "Complied"
            if unspent_oth > 0 and ("no" in trans_fund):
                comp_status = "Non-compliant (Sec 135(5))"
                status = ClauseStatus.QUALIFIED
                exceptions.append(AuditException(
                    clause_id="Clause (xx)(a)",
                    headline=f"Unspent CSR not transferred to Schedule VII fund ({fy})",
                    description=f"Unspent CSR amount of ₹{unspent_oth:.2f} Cr was not transferred to Fund specified in Schedule VII within 6 months.",
                    amount_involved=unspent_oth,
                    severity="HIGH"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

            if unspent_on > 0 and ("no" in trans_spec):
                comp_status = "Non-compliant (Sec 135(6))"
                status = ClauseStatus.QUALIFIED
                exceptions.append(AuditException(
                    clause_id="Clause (xx)(b)",
                    headline=f"Unspent CSR not transferred to Special Account ({fy})",
                    description=f"Unspent ongoing project CSR amount of ₹{unspent_on:.2f} Cr was not transferred to Special Account within 30 days.",
                    amount_involved=unspent_on,
                    severity="HIGH"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

            csr_table_rows.append([
                fy,
                f"{oblg:.2f}",
                f"{spent:.2f}",
                f"{unspent_on:.2f}",
                f"{unspent_oth:.2f}",
                comp_status
            ])

        if not exceptions:
            observations.append("CSR obligations fully spent or unspent amounts duly transferred in compliance with Section 135(5) and 135(6).")

    if status == ClauseStatus.CLEAN:
        icai_text = (
            "(xx) (a) In respect of other than ongoing projects, the Company has transferred unspent amount to a Fund specified in Schedule VII "
            "to the Companies Act within a period of six months of the expiry of the financial year in compliance with second proviso to sub-section (5) "
            "of Section 135 of the said Act (or no unspent amount remained to be transferred).\n"
            "(b) In respect of ongoing projects, the Company has transferred unspent amount to a Special Account in compliance with the provision "
            "of sub-section (6) of Section 135 of the said Act (or no unspent amount remained to be transferred)."
        )
    else:
        icai_text = (
            "(xx) According to the records of the Company examined by us, the Company has NOT complied with the statutory provisions of Section 135:\n"
            "(a) Unspent amounts in respect of other than ongoing projects were not transferred to Schedule VII fund within 6 months, as detailed in the exception log.\n"
            "(b) Unspent amounts in respect of ongoing projects were not transferred to the designated Special Bank Account within 30 days, as detailed in the exception log."
        )

    return ClauseResult(
        clause_id="Clause (xx)",
        clause_num="xx",
        clause_sub="(a)-(b)",
        title="Corporate Social Responsibility (CSR) Compliance (Section 135)",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=csr_table_headers,
        disclosure_table_rows=csr_table_rows,
        workpaper_rows=csr_df.to_dict(orient="records") if not csr_df.empty else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
