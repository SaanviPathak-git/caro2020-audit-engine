"""
Statutory Legal CARO 2020 Report Annexure Generator.
Formats the final legal text for the Independent Auditor's Report using official
ICAI Guidance Note wording, inserting statutory disclosure tables where exceptions exist.
"""

import os
from typing import Dict, Any, List
from engine.models import AuditEngagementResult, ClauseStatus


def generate_draft_caro_report_markdown(result: AuditEngagementResult, output_path: str) -> str:
    lines = []
    meta = result.metadata

    lines.append(f"# ANNEXURE 'A' TO THE INDEPENDENT AUDITOR'S REPORT")
    lines.append(f"*(Referred to in paragraph 1 under 'Report on Other Legal and Regulatory Requirements' section of our report to the Members of {meta.company_name} of even date)*\n")
    lines.append(f"**Company Name:** {meta.company_name}  ")
    lines.append(f"**Corporate Identity Number (CIN):** {meta.cin}  ")
    lines.append(f"**Financial Year:** {meta.financial_year} (Ended {meta.balance_sheet_date})  ")
    lines.append(f"**Audit Firm:** {meta.audit_firm} (FRN: {meta.firm_registration_no})  \n")
    lines.append("---\n")
    lines.append("To the Members of **Tata Motors Limited**,\n")
    lines.append(
        "Based on the audit procedures performed for the purpose of reporting a true and fair view on the financial statements of the Company "
        "and taking into consideration the information and explanations given to us and the books of account and other records examined by us in the normal course of audit, "
        "and to the best of our knowledge and belief, we report that:\n"
    )

    for cid in [
        "3(i)", "3(ii)", "3(iii)", "3(iv)", "3(v)", "3(vi)", "3(vii)", "3(viii)",
        "3(ix)", "3(x)", "3(xi)", "3(xii)", "3(xiii)", "3(xiv)", "3(xv)", "3(xvi)",
        "3(xvii)", "3(xviii)", "3(xix)", "3(xx)", "3(xxi)"
    ]:
        cl_res = result.clause_results.get(cid)
        if not cl_res:
            continue

        lines.append(f"### {cl_res.clause_number}: {cl_res.clause_title}")
        
        # Add badge or status tag
        status_tag = f"**Status:** `{cl_res.status.value}` | **Severity:** `{cl_res.severity.value}`"
        lines.append(f"{status_tag}\n")

        # Legal text
        lines.append(cl_res.icai_standard_text + "\n")

        # Insert Statutory Disclosure Table if present and qualified
        if cl_res.status == ClauseStatus.QUALIFIED and cl_res.disclosure_table:
            lines.append("#### Statutory Disclosure Table:\n")
            tbl = cl_res.disclosure_table
            headers = list(tbl[0].keys())
            
            # Markdown table header
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            
            for row in tbl:
                row_vals = [str(row.get(h, '')).replace("\n", " ") for h in headers]
                lines.append("| " + " | ".join(row_vals) + " |")
            lines.append("\n")

        # Special handling for 3(vii) undisputed table if present in workpaper data
        if cid == "3(vii)" and "undisputed_overdue_table" in cl_res.audit_workpaper_data:
            undisp = cl_res.audit_workpaper_data["undisputed_overdue_table"]
            if undisp:
                lines.append("#### Undisputed Statutory Arrears Outstanding for More Than 6 Months:\n")
                headers = list(undisp[0].keys())
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in undisp:
                    row_vals = [str(row.get(h, '')).replace("\n", " ") for h in headers]
                    lines.append("| " + " | ".join(row_vals) + " |")
                lines.append("\n")

        lines.append("---\n")

    # Auditor Signature Block
    lines.append("\n### For and on behalf of:")
    lines.append(f"**{meta.audit_firm}**  ")
    lines.append("Chartered Accountants  ")
    lines.append(f"ICAI Firm Registration Number: {meta.firm_registration_no}  \n\n")
    lines.append(f"**{meta.engagement_partner}**  ")
    lines.append("Partner  ")
    lines.append(f"Membership Number: {meta.membership_no}  ")
    lines.append(f"Place: Mumbai  ")
    lines.append(f"Date: May 08, 2024  ")
    lines.append(f"UDIN: 24{meta.membership_no}AAAAAA0001  \n")

    content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return output_path
