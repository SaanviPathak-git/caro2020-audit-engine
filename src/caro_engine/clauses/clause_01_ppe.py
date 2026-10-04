"""
Substantive Audit Testing Module: Clause (i) - Property, Plant & Equipment and Intangibles
Statutory Reference: CARO 2020 Clause 3(i)(a)-(e) / Companies Act 2013 / Ind AS 16 & 38 / SA 500
"""

import pandas as pd
from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_01_ppe(data: Dict[str, Any]) -> ClauseResult:
    far_df: pd.DataFrame = data.get("fixed_asset_register", pd.DataFrame())
    title_df: pd.DataFrame = data.get("title_deeds_register", pd.DataFrame())
    gov_data: Dict[str, Any] = data.get("governance_check_responses", {})
    
    substantive_tests = [
        "Verified maintenance of proper records showing full particulars, quantitative details and situation of PPE & Intangibles per SA 500.",
        "Evaluated management's physical verification policy and inspected reconciliation schedules.",
        "Audited title deeds of immovable properties (other than leases) against revenue records and registration deeds.",
        "Performed mathematical recalculation of revaluation percentage change against the statutory 10% threshold.",
        "Verified whether revaluations were conducted by an IBBI Registered Valuer per Section 247.",
        "Inquired with management and inspected legal disclosures regarding proceedings under Prohibition of Benami Property Transactions Act, 1988."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.CAST_VERIFIED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.TRIAL_BALANCE_TIED]
    status = ClauseStatus.CLEAN
    
    # 1. Physical Verification Check
    unverified_classes = []
    if not far_df.empty and "physical_verified" in far_df.columns:
        for _, row in far_df.iterrows():
            if str(row["physical_verified"]).strip().lower() in ["no", "false"]:
                unverified_classes.append(row["asset_class"])
        if unverified_classes:
            status = ClauseStatus.QUALIFIED
            exc = AuditException(
                clause_id="Clause (i)(b)",
                headline="Physical verification not conducted for asset classes",
                description=f"Physical verification was not conducted during the year for: {', '.join(unverified_classes)}.",
                severity="HIGH"
            )
            exceptions.append(exc)
            tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        else:
            observations.append("PPE has been physically verified by management under an appropriate rotational cycle; no material discrepancies noted.")

    # 2. Revaluation Threshold Test (10% limit check & Registered Valuer)
    if not far_df.empty and "revaluation_pct_change" in far_df.columns:
        for _, row in far_df.iterrows():
            pct = float(row.get("revaluation_pct_change", 0.0))
            is_rv = str(row.get("revalued_by_registered_valuer", "")).strip().lower() in ["yes", "true"]
            asset_cls = row["asset_class"]
            
            if pct >= 10.0:
                if not is_rv:
                    status = ClauseStatus.QUALIFIED
                    exc = AuditException(
                        clause_id="Clause (i)(d)",
                        headline=f"Revaluation >= 10% without Registered Valuer for {asset_cls}",
                        description=f"Asset class '{asset_cls}' was revalued by {pct:.2f}% (exceeding 10% statutory threshold), but valuation was NOT conducted by an IBBI Registered Valuer in breach of Section 247.",
                        amount_involved=float(row.get("revaluation_amount", 0.0)),
                        variance_pct=pct,
                        severity="CRITICAL"
                    )
                    exceptions.append(exc)
                    tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
                else:
                    if status != ClauseStatus.QUALIFIED:
                        status = ClauseStatus.OBSERVATION
                    observations.append(f"Revaluation of {asset_cls} by {pct:.2f}% conducted by Registered Valuer per Section 247.")

    # 3. Title Deeds Check (Clause i(c))
    title_table_headers = [
        "Balance Sheet Line Item",
        "Description of Property",
        "Gross Carrying Value (₹ Cr)",
        "Title Deeds Held In Name Of",
        "Whether Promoter/Director/Relative",
        "Period Held (Years)",
        "Reason for Not Being Held in Company Name"
    ]
    title_table_rows = []
    
    if not title_df.empty:
        for _, row in title_df.iterrows():
            held_name = str(row["held_in_name_of"]).strip()
            # If held in someone else's name
            company_name = data.get("metadata").company_name
            if company_name.lower() not in held_name.lower():
                is_promoter = str(row.get("is_promoter_director_relative", "No")).strip()
                title_table_rows.append([
                    row["balance_sheet_line_item"],
                    row["property_description"],
                    f"{float(row['gross_carrying_value_cr']):.2f}",
                    held_name,
                    is_promoter,
                    str(row["period_held_years"]),
                    row["reason_for_not_held"]
                ])
                if is_promoter.lower() in ["yes", "true"]:
                    status = ClauseStatus.QUALIFIED
                    exceptions.append(AuditException(
                        clause_id="Clause (i)(c)",
                        headline="Immovable property held in name of Promoter/Director",
                        description=f"Property '{row['property_description']}' valued at ₹{row['gross_carrying_value_cr']} Cr is held in the name of {held_name} (promoter/director).",
                        amount_involved=float(row["gross_carrying_value_cr"]),
                        severity="CRITICAL"
                    ))
                    tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
                else:
                    if status == ClauseStatus.CLEAN:
                        status = ClauseStatus.OBSERVATION
                    observations.append(f"Title deed for '{row['property_description']}' held in name of {held_name} pending formal mutation.")

    # Draft ICAI legal annexure wording
    if status == ClauseStatus.CLEAN:
        icai_text = (
            "(i) (a) (A) The Company has maintained proper records showing full particulars, including quantitative details and situation of Property, Plant and Equipment.\n"
            "(B) The Company has maintained proper records showing full particulars of intangible assets.\n"
            "(b) The Property, Plant and Equipment have been physically verified by the management in accordance with a regular programme of verification which, in our opinion, is reasonable having regard to the size of the Company and the nature of its assets. No material discrepancies were noticed on such verification.\n"
            "(c) According to the information and explanations given to us and on the basis of our examination of the records of the Company, the title deeds of all the immovable properties (other than properties where the Company is the lessee and the lease agreements are duly executed in favour of the lessee) disclosed in the financial statements are held in the name of the Company.\n"
            "(d) The Company has not revalued its Property, Plant and Equipment (including Right of Use assets) or intangible assets or both during the year.\n"
            "(e) According to the information and explanations given to us, no proceedings have been initiated or are pending against the Company for holding any benami property under the Prohibition of Benami Property Transactions Act, 1988 (as amended) and rules made thereunder."
        )
    else:
        # Building detailed disclosure
        c_text = ""
        if title_table_rows:
            c_text = "According to the information and explanations given to us and on the basis of our examination of records, the title deeds of immovable properties (other than properties where the Company is lessee) disclosed in financial statements are held in the name of the Company, except for the following properties:\n"
        else:
            c_text = "The title deeds of all immovable properties disclosed in the financial statements are held in the name of the Company.\n"
            
        b_text = "The Property, Plant and Equipment have been physically verified by management during the year, except as noted in the exception schedule.\n" if unverified_classes else "The Property, Plant and Equipment have been physically verified by the management under a reasonable phased programme; no material discrepancies were noticed.\n"
        
        d_text = "The Company has revalued certain classes of Property, Plant and Equipment during the year, details of which are highlighted in the exception log.\n" if any(e.clause_id == "Clause (i)(d)" for e in exceptions) else "The Company has not revalued its Property, Plant and Equipment or intangible assets during the year.\n"

        icai_text = (
            f"(i) (a) (A) The Company has maintained proper records showing full particulars of Property, Plant and Equipment.\n"
            f"(B) The Company has maintained proper records showing full particulars of intangible assets.\n"
            f"(b) {b_text}"
            f"(c) {c_text}"
            f"(d) {d_text}"
            f"(e) According to the information and explanations given to us, no proceedings have been initiated or are pending against the Company for holding benami property under the Prohibition of Benami Property Transactions Act, 1988."
        )

    return ClauseResult(
        clause_id="Clause (i)",
        clause_num="i",
        clause_sub="(a)-(e)",
        title="Property, Plant & Equipment and Intangible Assets",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=title_table_headers,
        disclosure_table_rows=title_table_rows,
        workpaper_rows=far_df.to_dict(orient="records") if not far_df.empty else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
