"""
Rule Validator for CARO 2020 Clause 3(xxi): Qualifications or Adverse Remarks in Group CARO Reports.
Statutory Mandate:
Whether there have been any qualifications or adverse remarks by the respective auditors in the Companies (Auditor's Report)
Order (CARO) reports of the companies included in the consolidated financial statements, if yes,
indicate the details of the companies and the paragraph numbers of the CARO report containing qualifications or adverse remarks.
"""

import pandas as pd
from typing import Dict, Any, List
from engine.models import ClauseResult, ClauseStatus, RiskSeverity, AuditException, AuditTickMark


def evaluate_clause_21_group_caro(group_caro_df: pd.DataFrame, metadata: Dict[str, Any]) -> ClauseResult:
    exceptions: List[AuditException] = []
    tick_marks: List[str] = [
        AuditTickMark.AGREED_TO_CONFIRMATION.value, 
        AuditTickMark.TRACED_TO_STATUTE.value
    ]

    qualified_subs = group_caro_df[group_caro_df['has_qualifications_or_adverse_remarks'].astype(str).str.lower() == 'yes']
    
    group_disclosure_table = []
    if not qualified_subs.empty:
        for _, row in qualified_subs.iterrows():
            group_disclosure_table.append({
                "Name of the Entity": row['subsidiary_associate_name'],
                "CIN": row['cin'],
                "Relationship": row['relationship'],
                "Auditor Firm": row['auditor_firm_name'],
                "CARO Clause / Paragraph": row['qualifying_clause_paragraph'],
                "Nature of Qualification / Adverse Remark": row['nature_of_qualification_or_adverse_remark']
            })
            exceptions.append(AuditException(
                clause_id="3(xxi)",
                clause_title=f"CARO Qualification in {row['subsidiary_associate_name']}",
                severity=RiskSeverity.MEDIUM,
                exception_description=f"Respective auditor ({row['auditor_firm_name']}) reported a qualification under {row['qualifying_clause_paragraph']}: {row['nature_of_qualification_or_adverse_remark']}.",
                statutory_reference="Clause 3(xxi) of CARO 2020",
                quantification_inr_cr=0.0,
                recommended_caro_disclosure="Mandatory disclosure of entity details and clause paragraph numbers in Consolidated CARO report.",
                tick_mark=AuditTickMark.EXCEPTION_NOTED
            ))

    total_group_entities = len(group_caro_df)
    qualified_count = len(qualified_subs)

    if qualified_count > 0:
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.MEDIUM
        summary_finding = f"Consolidated CARO: {qualified_count} out of {total_group_entities} group entities contain qualifications / adverse remarks by respective auditors."
        entities_summary = "; ".join([f"{r['Name of the Entity']} ({r['CARO Clause / Paragraph']})" for r in group_disclosure_table])
        icai_text = (
            "(xxi) According to the information and explanations given to us and based on the CARO reports issued by the respective auditors of the companies included in the consolidated financial statements, "
            f"qualifications or adverse remarks have been included in the CARO reports of the following companies:\n"
            f"[REFER STATUTORY DISCLOSURE TABLE: {entities_summary}]"
        )
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        summary_finding = f"All {total_group_entities} group entities' CARO reports examined have clean unqualified opinions."
        icai_text = (
            "(xxi) According to the information and explanations given to us and based on the CARO reports issued by the auditors of the companies included in the consolidated financial statements, "
            "there are no qualifications or adverse remarks included in the CARO reports of the respective companies."
        )

    return ClauseResult(
        clause_id="3(xxi)",
        clause_number="Clause (xxi)",
        clause_title="Qualifications or Adverse Remarks in Group CARO Reports",
        status=status,
        severity=severity,
        summary_finding=summary_finding,
        icai_standard_text=icai_text,
        exceptions=exceptions,
        disclosure_table=group_disclosure_table if group_disclosure_table else None,
        audit_workpaper_data={
            "total_entities_reviewed": total_group_entities,
            "qualified_entities_count": qualified_count
        },
        tick_marks_applied=tick_marks
    )
