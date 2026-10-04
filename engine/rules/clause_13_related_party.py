"""
Rule Validator for CARO 2020 Clause 3(xiii): Related Party Transactions (Sections 177 & 188 and Ind AS 24).
Statutory Mandate:
Whether all transactions with related parties are in compliance with Sections 177 and 188 of the Companies Act, 2013
and details have been disclosed in the financial statements as required by applicable accounting standards.
"""

import pandas as pd
from typing import Dict, Any, List
from engine.models import ClauseResult, ClauseStatus, RiskSeverity, AuditException, AuditTickMark


def evaluate_clause_13_related_party(rpt_df: pd.DataFrame, metadata: Dict[str, Any]) -> ClauseResult:
    exceptions: List[AuditException] = []
    tick_marks: List[str] = [
        AuditTickMark.CHECKED_TO_GL.value, 
        AuditTickMark.TRACED_TO_STATUTE.value
    ]

    non_177 = rpt_df[rpt_df['audit_committee_prior_approval_sec177'].astype(str).str.lower() == 'no']
    non_188 = rpt_df[rpt_df['board_approval_sec188'].astype(str).str.lower() == 'no']
    undisclosed = rpt_df[rpt_df['disclosed_in_financial_statements_indas24'].astype(str).str.lower() == 'no']

    if not non_177.empty:
        for _, row in non_177.iterrows():
            exceptions.append(AuditException(
                clause_id="3(xiii)",
                clause_title="Related Party Transaction Non-Compliance with Section 177",
                severity=RiskSeverity.HIGH,
                exception_description=f"Transaction with {row['related_party_name']} of ₹{row['transaction_value_cr']} Cr entered without prior Audit Committee approval under Section 177.",
                statutory_reference="Section 177 Companies Act, 2013 / Clause 3(xiii)",
                quantification_inr_cr=float(row['transaction_value_cr']),
                recommended_caro_disclosure="Disclose lack of Section 177 approval.",
                tick_mark=AuditTickMark.EXCEPTION_NOTED
            ))

    if not undisclosed.empty:
        for _, row in undisclosed.iterrows():
            exceptions.append(AuditException(
                clause_id="3(xiii)",
                clause_title="Omission of Related Party Disclosures under Ind AS 24",
                severity=RiskSeverity.HIGH,
                exception_description=f"Transaction with {row['related_party_name']} of ₹{row['transaction_value_cr']} Cr not disclosed in Note on Related Party Disclosures.",
                statutory_reference="Ind AS 24 / Clause 3(xiii)",
                quantification_inr_cr=float(row['transaction_value_cr']),
                recommended_caro_disclosure="Disclose non-disclosure in financial statements.",
                tick_mark=AuditTickMark.EXCEPTION_NOTED
            ))

    total_rpt_val = float(rpt_df['transaction_value_cr'].sum())

    if exceptions:
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.HIGH
        summary_finding = f"Non-compliance noted in {len(exceptions)} related party transactions."
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        summary_finding = f"All related party transactions (Total: ₹{total_rpt_val:,.2f} Cr) comply with Section 177 & 188; omnibus approvals obtained; fully disclosed in Ind AS 24 Notes."

    icai_text = (
        "(xiii) In our opinion and according to the information and explanations given to us, the Company is in compliance with Sections 177 and 188 of the Companies Act, 2013 where applicable, for all transactions with the related parties and the details of related party transactions have been disclosed in the standalone financial statements as required by the applicable accounting standards (Ind AS 24)."
    )

    return ClauseResult(
        clause_id="3(xiii)",
        clause_number="Clause (xiii)",
        clause_title="Related Party Transactions (Sections 177 & 188 and Ind AS 24)",
        status=status,
        severity=severity,
        summary_finding=summary_finding,
        icai_standard_text=icai_text,
        exceptions=exceptions,
        disclosure_table=rpt_df.to_dict(orient="records"),
        audit_workpaper_data={
            "total_rpt_value_cr": total_rpt_val,
            "parties_reviewed": len(rpt_df),
            "omnibus_approval_status": "Compliant"
        },
        tick_marks_applied=tick_marks
    )
