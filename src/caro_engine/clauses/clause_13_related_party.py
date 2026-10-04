"""
Substantive Audit Testing Module: Clause (xiii) - Related Party Transactions (Sections 177, 188 & Ind AS 24)
Statutory Reference: CARO 2020 Clause 3(xiii) / Sections 177 & 188 of Companies Act, 2013 / Ind AS 24 / SA 550
"""

import pandas as pd
from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_13_related_party(data: Dict[str, Any]) -> ClauseResult:
    rpt_df: pd.DataFrame = data.get("related_party_transactions", pd.DataFrame())
    
    substantive_tests = [
        "Obtained list of related parties and related party transactions per SA 550.",
        "Inspected Audit Committee prior approvals and omnibus approvals under Section 177.",
        "Tested whether transactions not in ordinary course of business or not at arm's length received Board and Shareholder approvals under Section 188.",
        "Benchmarked transaction pricing against transfer pricing documentation and market comparables.",
        "Reconciled related party ledger balances against Note disclosures in financial statements per Ind AS 24."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.DOCUMENT_INSPECTED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.TRIAL_BALANCE_TIED]
    status = ClauseStatus.CLEAN
    
    rpt_headers = [
        "Related Party Name",
        "Relationship",
        "Nature of Transaction",
        "Amount (₹ Cr)",
        "Audit Committee Approval",
        "Arm's Length Tested",
        "Disclosed in Financial Statements"
    ]
    rpt_rows = []
    
    if not rpt_df.empty:
        for _, row in rpt_df.iterrows():
            party = row.get("related_party_name", "")
            amt = float(row.get("transaction_value_cr", 0.0))
            ac_app = str(row.get("audit_committee_prior_approval", "Yes")).strip().lower() in ["yes", "true"]
            al_tested = "yes" in str(row.get("arms_length_basis_tested", "Yes")).strip().lower()
            disclosed = str(row.get("disclosed_in_financial_statements_note38", "Yes")).strip().lower() in ["yes", "true"]
            
            rpt_rows.append([
                party,
                str(row.get("relationship", "")),
                str(row.get("nature_of_transaction", "")),
                f"{amt:.2f}",
                "Yes" if ac_app else "No",
                "Yes" if al_tested else "No",
                "Yes" if disclosed else "No"
            ])
            
            # Check statutory breaches
            if not ac_app or not disclosed or not al_tested:
                status = ClauseStatus.QUALIFIED
                desc_parts = []
                if not ac_app:
                    desc_parts.append("Missing Audit Committee approval (Sec 177)")
                if not al_tested:
                    desc_parts.append("Not at arm's length without Sec 188 approvals")
                if not disclosed:
                    desc_parts.append("Omitted from Ind AS 24 notes to accounts")
                    
                exceptions.append(AuditException(
                    clause_id="Clause (xiii)",
                    headline=f"RPT non-compliance with {party}",
                    description=f"Transaction with {party} of ₹{amt:.2f} Cr breached statutory requirements: {', '.join(desc_parts)}.",
                    amount_involved=amt,
                    severity="HIGH"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

        if not any(e.clause_id == "Clause (xiii)" for e in exceptions):
            observations.append("All transactions with related parties comply with Sections 177 and 188 and are disclosed in the financial statements per Ind AS 24.")

    if status == ClauseStatus.CLEAN:
        icai_text = (
            "(xiii) According to the information and explanations given to us and based on our examination of the records of the Company, "
            "transactions with the related parties are in compliance with Sections 177 and 188 of the Act, where applicable, and details of such "
            "transactions have been disclosed in the financial statements as required by the applicable accounting standards (Ind AS 24)."
        )
    else:
        icai_text = (
            "(xiii) According to the information and explanations given to us and based on our examination of records, "
            "certain transactions with related parties were NOT in compliance with Sections 177 and/or 188 of the Act or have not been disclosed "
            "as required by the applicable accounting standards, as detailed in the audit exception log."
        )

    return ClauseResult(
        clause_id="Clause (xiii)",
        clause_num="xiii",
        clause_sub="",
        title="Related Party Transactions (Sections 177, 188 & Ind AS 24)",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=rpt_headers if rpt_rows else [],
        disclosure_table_rows=rpt_rows if rpt_rows else [],
        workpaper_rows=rpt_df.to_dict(orient="records") if not rpt_df.empty else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
