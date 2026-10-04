"""
Draft CARO 2020 Statutory Report Generator (Legal Annexure per ICAI Standards)
"""

from pathlib import Path
from typing import List, Dict, Any
from tabulate import tabulate
from ..core.models import ClauseResult, ClauseStatus, ClientMetadata

def format_table_markdown(headers: List[str], rows: List[List[Any]]) -> str:
    if not headers or not rows:
        return ""
    return tabulate(rows, headers=headers, tablefmt="github")

def generate_draft_caro_report_markdown(
    metadata: ClientMetadata,
    clause_results: List[ClauseResult]
) -> str:
    """Generates the official ICAI Legal Annexure for the Independent Auditor's Report in Markdown."""
    
    clean_cnt = sum(1 for r in clause_results if r.status == ClauseStatus.CLEAN)
    qual_cnt = sum(1 for r in clause_results if r.status == ClauseStatus.QUALIFIED)
    obs_cnt = sum(1 for r in clause_results if r.status == ClauseStatus.OBSERVATION)
    
    lines = []
    lines.append(f"# ANNEXURE 'A' TO THE INDEPENDENT AUDITOR'S REPORT")
    lines.append(f"*(Referred to in Paragraph 1 under 'Report on Other Legal and Regulatory Requirements' section of our report of even date)*")
    lines.append("")
    lines.append(f"**To the Members of {metadata.company_name}**")
    lines.append(f"**CIN:** {metadata.cin}")
    lines.append(f"**Financial Year Ended:** {metadata.audit_period_end}")
    lines.append("")
    lines.append(
        "To the best of our information and according to the explanations provided to us by the Company and the books of account and records "
        "examined by us in the normal course of audit, we report that:"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    for res in clause_results:
        clause_tag = f"### Clause 3({res.clause_num}){res.clause_sub}: {res.title}"
        lines.append(clause_tag)
        
        # Status Badge
        badge = "✅ CLEAN" if res.status == ClauseStatus.CLEAN else (
            "⚠️ QUALIFIED / ADVERSE" if res.status == ClauseStatus.QUALIFIED else (
                "ℹ️ OBSERVATION" if res.status == ClauseStatus.OBSERVATION else "➖ NOT APPLICABLE"
            )
        )
        lines.append(f"**Audit Finding Status:** `{badge}`")
        lines.append("")
        
        # ICAI Legal Text
        lines.append(res.icai_report_text)
        lines.append("")
        
        # Mandatory Table if present
        if res.disclosure_table_headers and res.disclosure_table_rows:
            lines.append("**Statutory Disclosure Table:**")
            lines.append("")
            lines.append(format_table_markdown(res.disclosure_table_headers, res.disclosure_table_rows))
            lines.append("")
            
        lines.append("---")
        lines.append("")

    # Auditor Signature Block
    lines.append("### For and on behalf of:")
    lines.append(f"**{metadata.firm_name}**")
    lines.append("Chartered Accountants")
    lines.append("")
    lines.append(f"**{metadata.lead_partner}**")
    lines.append("Partner")
    lines.append("Membership No.: 048921")
    lines.append(f"Place: Mumbai / New Delhi")
    lines.append(f"Date: {metadata.audit_period_end}")
    lines.append(f"UDIN: 24048921BSRCARO202099")
    lines.append("")

    return "\n".join(lines)

def save_draft_caro_report(
    output_path: Path,
    metadata: ClientMetadata,
    clause_results: List[ClauseResult]
) -> Path:
    md_content = generate_draft_caro_report_markdown(metadata, clause_results)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return output_path
