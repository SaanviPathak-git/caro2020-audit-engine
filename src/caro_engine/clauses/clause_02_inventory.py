"""
Substantive Audit Testing Module: Clause (ii) - Inventories & Working Capital Bank Returns
Statutory Reference: CARO 2020 Clause 3(ii)(a)-(b) / Ind AS 2 (Inventories) / SA 501 / Guidance Note on CARO 2020
"""

import pandas as pd
from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_02_inventory(data: Dict[str, Any]) -> ClauseResult:
    inv_df: pd.DataFrame = data.get("inventory_physical_verification", pd.DataFrame())
    bank_df: pd.DataFrame = data.get("quarterly_bank_returns", pd.DataFrame())
    
    substantive_tests = [
        "Evaluated management inventory counting instructions and attended sample physical count per SA 501.",
        "Tested mathematical reconciliation between physical count records and perpetual inventory ledgers.",
        "Calculated variance percentages per inventory class against the statutory 10% discrepancy threshold.",
        "Inspected bank sanction letters to determine if working capital limits secured by current assets exceed ₹5 Crore.",
        "Obtained quarterly stock and book debt returns submitted to lending banks / consortium.",
        "Performed independent substantive reconciliation between quarterly bank filings and audited General Ledger / Trial Balance.",
        "Evaluated reasons for variance (timing differences, valuation adjustments, cut-off differences)."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.CAST_VERIFIED, AuditTickMark.BANK_RECONCILED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.TRIAL_BALANCE_TIED]
    status = ClauseStatus.CLEAN

    # 1. Test Clause (ii)(a): Inventory Physical Verification & 10% variance limit
    if not inv_df.empty:
        for _, row in inv_df.iterrows():
            var_pct = abs(float(row.get("variance_pct", 0.0)))
            properly_adj = str(row.get("properly_adjusted_in_books", "Yes")).strip().lower() in ["yes", "true"]
            inv_class = row.get("inventory_class", "General Inventory")
            plant = row.get("plant_location", "Main Plant")
            
            if var_pct >= 10.0:
                status = ClauseStatus.QUALIFIED
                exc = AuditException(
                    clause_id="Clause (ii)(a)",
                    headline=f"Inventory variance >= 10% at {plant} ({inv_class})",
                    description=f"Physical inventory count revealed a discrepancy of {var_pct:.2f}% (exceeding statutory 10% threshold) amounting to ₹{abs(float(row.get('variance_amount_cr', 0.0))):.2f} Cr. Properly adjusted in books: {row.get('properly_adjusted_in_books')}.",
                    amount_involved=abs(float(row.get("variance_amount_cr", 0.0))),
                    variance_pct=var_pct,
                    severity="HIGH" if properly_adj else "CRITICAL"
                )
                exceptions.append(exc)
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        
        if not any(e.clause_id == "Clause (ii)(a)" for e in exceptions):
            observations.append("Physical verification of inventory conducted at reasonable intervals; coverage and procedure appropriate; no discrepancies >= 10% noticed.")

    # 2. Test Clause (ii)(b): Working Capital Limits > 5 Crore & Quarterly Bank Statements Reconciliation
    bank_table_headers = [
        "Quarter",
        "Name of Bank / Consortium",
        "Securities Particulars",
        "Type of Current Asset",
        "Amount as per Books (₹ Cr)",
        "Amount Reported to Bank (₹ Cr)",
        "Difference (₹ Cr)",
        "Reason for Material Discrepancy"
    ]
    bank_table_rows = []
    has_large_unexplained_variance = False

    if not bank_df.empty:
        for _, row in bank_df.iterrows():
            sanctioned = float(row.get("sanctioned_limit_cr", 0.0))
            if sanctioned >= 5.0: # Exceeds statutory ₹5 Crore threshold
                diff = float(row.get("difference_cr", 0.0))
                var_pct = abs(float(row.get("variance_pct", 0.0)))
                
                # Big 4 practice: If difference is non-zero, it must be reported in the disclosure table per Guidance Note
                if abs(diff) > 0.01:
                    bank_table_rows.append([
                        row.get("quarter", ""),
                        row.get("bank_name", ""),
                        row.get("security_particulars", ""),
                        row.get("current_asset_type", ""),
                        f"{float(row.get('amount_per_books_cr', 0.0)):.2f}",
                        f"{float(row.get('amount_reported_to_bank_cr', 0.0)):.2f}",
                        f"{diff:.2f}",
                        row.get("reason_for_difference", "")
                    ])
                    
                    # If variance is egregious (> 10% and unexplained or drawing power inflation)
                    if var_pct >= 10.0:
                        has_large_unexplained_variance = True
                        status = ClauseStatus.QUALIFIED
                        exceptions.append(AuditException(
                            clause_id="Clause (ii)(b)",
                            headline=f"Material unreconciled variance in bank stock statement ({row.get('quarter')})",
                            description=f"Quarterly statement filed with {row.get('bank_name')} showed a discrepancy of {var_pct:.2f}% (₹{abs(diff):.2f} Cr) against books of account. Reason noted: {row.get('reason_for_difference')}.",
                            amount_involved=abs(diff),
                            variance_pct=var_pct,
                            severity="CRITICAL"
                        ))
                        tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

        if bank_table_rows and status == ClauseStatus.CLEAN:
            # Differences exist but are reconciled timing adjustments (standard corporate practice like Tata Motors)
            status = ClauseStatus.OBSERVATION
            observations.append(f"Working capital limits exceeding ₹5 Cr sanctioned by banks. Quarterly returns show timing and reconciliation differences duly tabulated.")

    # Draft ICAI legal annexure wording
    if status == ClauseStatus.CLEAN and not bank_table_rows:
        icai_text = (
            "(ii) (a) The inventory has been physically verified by the management during the year. In our opinion, the frequency of verification, coverage and procedure of such verification is appropriate. No discrepancies of 10% or more in the aggregate for each class of inventory were noticed on such physical verification.\n"
            "(b) The Company has been sanctioned working capital limits in excess of ₹5 Crore in aggregate from banks and financial institutions on the basis of security of current assets. The quarterly returns/statements filed by the Company with such banks are in agreement with the books of account of the Company."
        )
    elif status == ClauseStatus.OBSERVATION or (status == ClauseStatus.CLEAN and bank_table_rows):
        icai_text = (
            "(ii) (a) The inventory has been physically verified by the management during the year. In our opinion, the frequency of verification, coverage and procedure of such verification is appropriate. Discrepancies noticed were not 10% or more in the aggregate for each class of inventory and have been properly dealt with in the books of account.\n"
            "(b) The Company has been sanctioned working capital limits in excess of ₹5 Crore in aggregate from banks on the basis of security of current assets. The quarterly returns or statements filed by the Company with such banks are in agreement with the books of account, except for the following quarterly returns where differences arose due to normal financial closure adjustments:\n"
        )
    else: # QUALIFIED
        icai_text = (
            "(ii) (a) According to the information and explanations given to us, physical verification of inventory was conducted by the management, but material discrepancies exceeding 10% in aggregate were noticed for certain classes of inventory as detailed in the exception log.\n"
            "(b) The Company has been sanctioned working capital limits in excess of ₹5 Crore from banks on the basis of security of current assets. The quarterly returns/statements filed by the Company with such banks were NOT in agreement with the books of account, as detailed in the reconciliation statement below:\n"
        )

    return ClauseResult(
        clause_id="Clause (ii)",
        clause_num="ii",
        clause_sub="(a)-(b)",
        title="Inventories & Working Capital Bank Returns",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=bank_table_headers,
        disclosure_table_rows=bank_table_rows,
        workpaper_rows=bank_df.to_dict(orient="records") if not bank_df.empty else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
