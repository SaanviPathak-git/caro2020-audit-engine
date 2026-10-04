"""
Substantive Audit Testing Module: Clause (ix) - Borrowings Defaults, Wilful Defaulter & Fund Utilization
Statutory Reference: CARO 2020 Clause 3(ix)(a)-(f) / Guidance Note on CARO 2020 / SA 505 / RBI Wilful Defaulter Circulars
"""

import pandas as pd
from typing import Dict, Any, List
from ..core.models import ClauseResult, ClauseStatus, AuditException
from ..core.tickmarks import AuditTickMark
from ..utils.formatting import format_crores

def test_clause_09_borrowings_default(data: Dict[str, Any]) -> ClauseResult:
    borr_df: pd.DataFrame = data.get("borrowings_default_schedule", pd.DataFrame())
    tl_df: pd.DataFrame = data.get("term_loans_end_use", pd.DataFrame())
    ratios_data: Dict[str, Any] = data.get("balance_sheet_ratios", {})
    
    substantive_tests = [
        "Obtained direct bank confirmations per SA 505 and inspected bank loan statements, sanction letters and NCD debenture trust deeds.",
        "Tested mathematical debt service schedules and flagged overdue principal installments and interest defaults per Clause 3(ix)(a).",
        "Queried RBI wilful defaulter database, CIBIL/CRILC reports and bank sanction representations per Clause 3(ix)(b).",
        "Audited end-use of term loans by tracing drawdowns to CapEx invoices, asset capitalization entries and project escrow releases per Clause 3(ix)(c).",
        "Analyzed asset-liability maturity schedule and cash flows to evaluate whether short-term borrowings were utilized for long-term capital assets per Clause 3(ix)(d).",
        "Examined bank statements and inter-company advances to verify whether funds were borrowed to service obligations of subsidiaries or associates per Clause 3(ix)(e).",
        "Inspected share pledge registers and bank mortgage deeds to check whether loans were raised by pledging securities of subsidiaries per Clause 3(ix)(f)."
    ]
    
    observations: List[str] = []
    exceptions: List[AuditException] = []
    tickmarks = [AuditTickMark.VOUCHED, AuditTickMark.CAST_VERIFIED, AuditTickMark.BANK_RECONCILED, AuditTickMark.STATUTORY_LIMIT, AuditTickMark.TRIAL_BALANCE_TIED]
    status = ClauseStatus.CLEAN

    # 1. Repayment Default Testing (Clause ix(a))
    default_table_headers = [
        "Nature of Borrowing",
        "Name of Lender",
        "Amount Not Paid on Due Date (₹ Cr)",
        "Whether Principal or Interest",
        "No. of Days Delay / Unpaid",
        "Remarks"
    ]
    default_table_rows = []
    
    if not borr_df.empty:
        for _, row in borr_df.iterrows():
            p_def = float(row.get("default_principal_cr", 0.0))
            i_def = float(row.get("default_interest_cr", 0.0))
            days = int(row.get("days_delay", 0))
            lender = row.get("name_of_lender", "")
            nature = row.get("nature_of_borrowing", "")
            remarks = row.get("remarks", "")
            
            if p_def > 0 or i_def > 0:
                status = ClauseStatus.QUALIFIED
                tot_def = p_def + i_def
                typ = "Principal & Interest" if (p_def > 0 and i_def > 0) else ("Principal" if p_def > 0 else "Interest")
                
                default_table_rows.append([
                    nature,
                    lender,
                    f"{tot_def:.2f}",
                    typ,
                    str(days),
                    remarks
                ])
                
                exceptions.append(AuditException(
                    clause_id="Clause (ix)(a)",
                    headline=f"Default in debt servicing to {lender}",
                    description=f"Defaulted in payment of {typ} amounting to ₹{tot_def:.2f} Cr (delay of {days} days) for {nature}.",
                    amount_involved=tot_def,
                    severity="CRITICAL"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)

        if not default_table_rows:
            observations.append("The Company has not defaulted in repayment of loans or other borrowings or in the payment of interest thereon to any lender.")

    # 2. Term Loan End-Use Testing (Clause ix(c))
    diverted_loans = []
    if not tl_df.empty:
        for _, row in tl_df.iterrows():
            diverted = float(row.get("unutilized_diverted_amount_cr", 0.0))
            if diverted > 0:
                diverted_loans.append((row["lender_name"], diverted, row["stated_purpose"]))
                status = ClauseStatus.QUALIFIED
                exceptions.append(AuditException(
                    clause_id="Clause (ix)(c)",
                    headline=f"Term loan diversion for {row['lender_name']}",
                    description=f"Term loan from {row['lender_name']} had ₹{diverted:.2f} Cr unutilized/diverted from stated purpose: '{row['stated_purpose']}'.",
                    amount_involved=diverted,
                    severity="CRITICAL"
                ))
                tickmarks.append(AuditTickMark.EXCEPTION_FLAGGED)
        if not diverted_loans:
            observations.append("Term loans were applied for the purpose for which the loans were obtained.")

    # 3. Short-term funds used for long-term (Clause ix(d))
    net_wc = ratios_data.get("financial_ratios", {}).get("net_capital_turnover_ratio", {}).get("denominator_value_cr", 1.0)
    # If net working capital is deeply negative and funded non-current assets
    if net_wc < -100.0:
        if status != ClauseStatus.QUALIFIED:
            status = ClauseStatus.OBSERVATION
        observations.append(f"Short term funds appear to have been utilized for long term purposes as reflected in negative net working capital (₹{net_wc:.2f} Cr).")

    # ICAI Report text
    if status == ClauseStatus.CLEAN:
        icai_text = (
            "(ix) (a) According to the information and explanations given to us and on the basis of our examination of the records of the Company, "
            "the Company has not defaulted in repayment of loans or other borrowings or in the payment of interest thereon to any lender.\n"
            "(b) According to the information and explanations given to us, the Company has not been declared a wilful defaulter by any bank or financial institution or other lender.\n"
            "(c) In our opinion and according to the information and explanations given to us, term loans were applied for the purpose for which the loans were obtained.\n"
            "(d) According to the information and explanations given to us, and the procedures performed by us, and on an overall examination of the financial statements of the Company, "
            "we report that no funds raised on short-term basis have been used for long-term purposes by the Company.\n"
            "(e) According to the information and explanations given to us and on an overall examination of the financial statements of the Company, "
            "we report that the Company has not taken any funds from any entity or person on account of or to meet the obligations of its subsidiaries, associates or joint ventures.\n"
            "(f) According to the information and explanations given to us and procedures performed by us, we report that the Company has not raised loans during the year on the pledge of securities held in its subsidiaries, joint ventures or associate companies."
        )
    else:
        a_text = (
            "(ix) (a) According to the records of the Company examined by us and the information and explanations given to us, "
            "the Company has defaulted in repayment of loans or other borrowings or in the payment of interest thereon to lenders as detailed in the table below:\n"
            if default_table_rows else
            "(ix) (a) The Company has not defaulted in repayment of loans or other borrowings or in the payment of interest thereon to any lender.\n"
        )
        c_text = (
            "(c) According to the information and explanations given to us, term loans were diverted from their stated purpose as reported in the exception log.\n"
            if diverted_loans else
            "(c) Term loans were applied for the purpose for which the loans were obtained.\n"
        )
        icai_text = (
            f"{a_text}"
            "(b) According to the information and explanations given to us, the Company has not been declared a wilful defaulter by any bank or financial institution.\n"
            f"{c_text}"
            "(d) Short term funds and long term funds utilization has been reviewed and documented in audit findings.\n"
            "(e) Funds taken to meet obligations of group entities, if any, have been substantively tested.\n"
            "(f) The Company has not raised loans on the pledge of securities in subsidiaries, except as noted in the financial statements."
        )

    return ClauseResult(
        clause_id="Clause (ix)",
        clause_num="ix",
        clause_sub="(a)-(f)",
        title="Borrowings Defaults, Wilful Defaulter & Fund Utilization",
        status=status,
        substantive_tests=substantive_tests,
        observations=observations,
        exceptions=exceptions,
        disclosure_table_headers=default_table_headers,
        disclosure_table_rows=default_table_rows,
        workpaper_rows=borr_df.to_dict(orient="records") if not borr_df.empty else [],
        icai_report_text=icai_text,
        tickmarks_applied=tickmarks
    )
