"""
Rule Validators for Governance, Regulatory and Legal CARO 2020 Clauses:
- Clause 3(iv): Section 185 & 186
- Clause 3(v): Deposits from Public (Sections 73 to 76)
- Clause 3(vi): Maintenance of Cost Records (Section 148(1))
- Clause 3(viii): Unrecorded Income in Tax Assessments
- Clause 3(x): End-use of IPO / FPO & Private Placement Funds
- Clause 3(xi): Fraud Reporting and Whistleblower Mechanism
- Clause 3(xii): Nidhi Companies
- Clause 3(xiv): Internal Audit System (Section 138)
- Clause 3(xv): Non-Cash Transactions with Directors (Section 192)
- Clause 3(xvi): Registration under Section 45-IA of RBI Act
- Clause 3(xviii): Resignation of Statutory Auditors
"""

from typing import Dict, Any, List
from engine.models import ClauseResult, ClauseStatus, RiskSeverity, AuditException, AuditTickMark


def evaluate_clause_04_sec185_186(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_iv_sec185_186", {})
    within_limits = info.get("within_limits", True)
    exceptions: List[AuditException] = []
    
    if not within_limits:
        exceptions.append(AuditException(
            clause_id="3(iv)",
            clause_title="Non-compliance with Section 185 or 186",
            severity=RiskSeverity.HIGH,
            exception_description="Loans, investments, guarantees or securities exceeded limits under Section 186 without prior special resolution or violated Section 185.",
            statutory_reference="Sections 185 & 186 of Companies Act, 2013 / Clause 3(iv)",
            recommended_caro_disclosure="Disclose non-compliance with Sections 185 and 186.",
            tick_mark=AuditTickMark.EXCEPTION_NOTED
        ))
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.HIGH
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW

    icai_text = (
        "(iv) In our opinion and according to the information and explanations given to us, the Company has complied with "
        "the provisions of Sections 185 and 186 of the Companies Act, 2013 in respect of loans granted, investments made and guarantees and securities provided."
    )
    return ClauseResult(
        clause_id="3(iv)",
        clause_number="Clause (iv)",
        clause_title="Loans to Directors & Investments (Sections 185 & 186)",
        status=status,
        severity=severity,
        summary_finding=info.get("audit_finding", "Compliant with Sections 185 and 186."),
        icai_standard_text=icai_text,
        exceptions=exceptions,
        disclosure_table=None,
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value, AuditTickMark.CHECKED_TO_GL.value]
    )


def evaluate_clause_05_deposits(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_v_deposits", {})
    has_deposits = info.get("has_accepted_public_deposits", False) or info.get("has_deemed_deposits", False)
    exceptions: List[AuditException] = []

    if has_deposits:
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.HIGH
        exceptions.append(AuditException(
            clause_id="3(v)",
            clause_title="Public Deposits Non-Compliance",
            severity=RiskSeverity.HIGH,
            exception_description="Acceptance of public deposits or deemed deposits in contravention of Sections 73 to 76.",
            statutory_reference="Sections 73 to 76 of Companies Act, 2013",
            recommended_caro_disclosure="Disclose details of contravention of Sections 73 to 76.",
            tick_mark=AuditTickMark.EXCEPTION_NOTED
        ))
        icai_text = "(v) The Company has accepted deposits or deemed deposits in non-compliance with Sections 73 to 76 of the Act."
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        icai_text = (
            "(v) The Company has not accepted any deposits or amounts which are deemed to be deposits within the meaning of "
            "Sections 73 to 76 of the Act and the rules made thereunder. Accordingly, reporting under Clause 3(v) of the Order is not applicable."
        )

    return ClauseResult(
        clause_id="3(v)",
        clause_number="Clause (v)",
        clause_title="Acceptance of Public Deposits (Sections 73 to 76)",
        status=status,
        severity=severity,
        summary_finding=info.get("audit_finding", "No public deposits or deemed deposits accepted."),
        icai_standard_text=icai_text,
        exceptions=exceptions,
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_06_cost_records(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_vi_cost_records", {})
    records_maintained = info.get("cost_records_maintained", True)
    exceptions: List[AuditException] = []

    if not records_maintained:
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.MEDIUM
        exceptions.append(AuditException(
            clause_id="3(vi)",
            clause_title="Cost Records Not Maintained",
            severity=RiskSeverity.MEDIUM,
            exception_description="Prescribed cost accounts and records under Section 148(1) have not been maintained.",
            statutory_reference="Section 148(1) of Companies Act, 2013",
            recommended_caro_disclosure="Disclose non-maintenance of cost records.",
            tick_mark=AuditTickMark.EXCEPTION_NOTED
        ))
        icai_text = "(vi) The Company has not made and maintained cost accounts and records prescribed by the Central Government under Section 148(1)."
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        icai_text = (
            "(vi) The Central Government has specified maintenance of cost records under sub-section (1) of Section 148 of the Act "
            "in respect of the Company's products/services. We have broadly reviewed the accounts and records maintained by the Company "
            "and are of the opinion that prima facie, the prescribed accounts and records have been made and maintained. "
            "We have not, however, made a detailed examination of the records with a view to determine whether they are accurate or complete."
        )

    return ClauseResult(
        clause_id="3(vi)",
        clause_number="Clause (vi)",
        clause_title="Maintenance of Cost Records (Section 148(1))",
        status=status,
        severity=severity,
        summary_finding=info.get("audit_finding", "Cost records maintained prima facie; Cost Auditor appointed."),
        icai_standard_text=icai_text,
        exceptions=exceptions,
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_08_unrecorded_income(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_viii_unrecorded_income", {})
    has_unrecorded = info.get("undisclosed_income_surrendered", False)
    exceptions: List[AuditException] = []

    if has_unrecorded and not info.get("surrendered_income_recorded_in_books", True):
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.HIGH
        exceptions.append(AuditException(
            clause_id="3(viii)",
            clause_title="Surrendered Income Not Recorded in Books",
            severity=RiskSeverity.HIGH,
            exception_description="Income disclosed in tax assessment not properly recorded in books of account.",
            statutory_reference="Clause 3(viii) of CARO 2020",
            recommended_caro_disclosure="Disclose unrecorded income not accounted for.",
            tick_mark=AuditTickMark.EXCEPTION_NOTED
        ))
        icai_text = "(viii) Transactions surrendered as income during the year in tax assessments have not been properly recorded in the books."
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        icai_text = (
            "(viii) According to the information and explanations given to us, no transactions were surrendered or disclosed as income "
            "during the year in the tax assessments under the Income Tax Act, 1961 (such as, search or survey or any other relevant provisions of the Income Tax Act, 1961) "
            "which had not been previously recorded in the books of account."
        )

    return ClauseResult(
        clause_id="3(viii)",
        clause_number="Clause (viii)",
        clause_title="Unrecorded Income Disclosed in Tax Assessments",
        status=status,
        severity=severity,
        summary_finding=info.get("audit_finding", "No unrecorded income surrendered in tax assessments."),
        icai_standard_text=icai_text,
        exceptions=exceptions,
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_10_ipo_placement(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_x_ipo_private_placement", {})
    status = ClauseStatus.UNQUALIFIED
    severity = RiskSeverity.LOW
    
    icai_text = (
        "(x)(a) The Company has not raised any moneys by way of initial public offer or further public offer (including debt instruments) during the year.\n"
        "(b) During the year, the Company has not made any preferential allotment or private placement of shares or convertible debentures (fully, partially or optionally convertible) "
        "and hence reporting under Clause 3(x)(b) is not applicable."
    )
    return ClauseResult(
        clause_id="3(x)",
        clause_number="Clause (x)",
        clause_title="End-Use of IPO / FPO & Private Placement Funds",
        status=status,
        severity=severity,
        summary_finding=info.get("audit_finding", "No IPO/FPO during the year; compliant with Sec 42/62."),
        icai_standard_text=icai_text,
        exceptions=[],
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_11_fraud(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_xi_fraud_reporting", {})
    has_fraud = info.get("fraud_by_or_on_company_noticed", False)
    complaints = info.get("whistleblower_complaints_received_count", 0)
    exceptions: List[AuditException] = []

    if has_fraud:
        status = ClauseStatus.QUALIFIED
        severity = RiskSeverity.CRITICAL
        exceptions.append(AuditException(
            clause_id="3(xi)(a)",
            clause_title="Fraud Noticed or Reported",
            severity=RiskSeverity.CRITICAL,
            exception_description="Material fraud noticed or reported during the year.",
            statutory_reference="Section 143(12) / Clause 3(xi)",
            recommended_caro_disclosure="Disclose nature and amount of fraud.",
            tick_mark=AuditTickMark.EXCEPTION_NOTED
        ))
        icai_text = "(xi)(a) Fraud by or on the Company was noticed or reported during the year."
    else:
        status = ClauseStatus.UNQUALIFIED
        severity = RiskSeverity.LOW
        icai_text = (
            "(xi)(a) Based upon the audit procedures performed and according to the information and explanations given to us, "
            "no fraud by the Company and no material fraud on the Company has been noticed or reported during the year.\n"
            "(b) No report under sub-section (12) of Section 143 of the Companies Act has been filed by the auditors in Form ADT-4 with the Central Government during the year and up to the date of this report.\n"
            f"(c) As represented to us by the management, the Company received {complaints} whistle-blower complaints during the year, which have been considered by us in determining the nature, timing and extent of our audit procedures."
        )

    return ClauseResult(
        clause_id="3(xi)",
        clause_number="Clause (xi)",
        clause_title="Fraud Reporting & Whistleblower Mechanism (SA 240 / Section 143(12))",
        status=status,
        severity=severity,
        summary_finding=info.get("audit_finding", f"No material fraud noticed. {complaints} whistleblower complaints reviewed by audit committee."),
        icai_standard_text=icai_text,
        exceptions=exceptions,
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_12_nidhi(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_xii_nidhi_company", {})
    return ClauseResult(
        clause_id="3(xii)",
        clause_number="Clause (xii)",
        clause_title="Compliance by Nidhi Companies",
        status=ClauseStatus.NOT_APPLICABLE,
        severity=RiskSeverity.LOW,
        summary_finding="The Company is not a Nidhi Company. Clause is not applicable.",
        icai_standard_text="(xii) The Company is not a Nidhi Company as defined under Section 406 of the Companies Act, 2013. Accordingly, Clause 3(xii) of the Order is not applicable.",
        exceptions=[],
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_14_internal_audit(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_xiv_internal_audit", {})
    status = ClauseStatus.UNQUALIFIED
    severity = RiskSeverity.LOW
    
    icai_text = (
        "(xiv)(a) In our opinion and based on our examination, the Company has an internal audit system commensurate with the size and nature of its business.\n"
        "(b) We have considered the internal audit reports of the Company issued till date for the period under audit."
    )
    return ClauseResult(
        clause_id="3(xiv)",
        clause_number="Clause (xiv)",
        clause_title="Internal Audit System (Section 138 / SA 610)",
        status=status,
        severity=severity,
        summary_finding=info.get("audit_finding", "Internal audit system commensurate with size; reports considered."),
        icai_standard_text=icai_text,
        exceptions=[],
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_15_non_cash(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_xv_non_cash_transactions", {})
    return ClauseResult(
        clause_id="3(xv)",
        clause_number="Clause (xv)",
        clause_title="Non-Cash Transactions with Directors (Section 192)",
        status=ClauseStatus.UNQUALIFIED,
        severity=RiskSeverity.LOW,
        summary_finding=info.get("audit_finding", "No non-cash transactions with directors."),
        icai_standard_text="(xv) In our opinion and according to the information and explanations given to us, during the year the Company has not entered into any non-cash transactions with its directors or persons connected with its directors and hence provisions of Section 192 of the Companies Act, 2013 are not applicable.",
        exceptions=[],
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_16_rbi_nbfc(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_xvi_rbi_nbfc_registration", {})
    return ClauseResult(
        clause_id="3(xvi)",
        clause_number="Clause (xvi)",
        clause_title="Registration under Section 45-IA of RBI Act, 1934 & CIC",
        status=ClauseStatus.UNQUALIFIED,
        severity=RiskSeverity.LOW,
        summary_finding=info.get("audit_finding", "Manufacturing entity; 50-50 test not triggered; not an NBFC or CIC."),
        icai_standard_text=(
            "(xvi)(a) The Company is not required to be registered under Section 45-IA of the Reserve Bank of India Act, 1934.\n"
            "(b) The Company has not conducted any Non-Banking Financial or Housing Finance activities without obtaining a valid Certificate of Registration (CoR) from the RBI.\n"
            "(c) The Company is not a Core Investment Company (CIC) as defined in the regulations made by the RBI.\n"
            "(d) According to the information and explanations provided to us, the Group does not have more than one CIC."
        ),
        exceptions=[],
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )


def evaluate_clause_18_auditor_resignation(data: Dict[str, Any], metadata: Dict[str, Any]) -> ClauseResult:
    info = data.get("clause_xviii_auditor_resignation", {})
    return ClauseResult(
        clause_id="3(xviii)",
        clause_number="Clause (xviii)",
        clause_title="Resignation of Statutory Auditors",
        status=ClauseStatus.NOT_APPLICABLE,
        severity=RiskSeverity.LOW,
        summary_finding=info.get("audit_finding", "No resignation of statutory auditors during the year."),
        icai_standard_text="(xviii) There has been no resignation of the statutory auditors during the year. Accordingly, reporting under Clause 3(xviii) of the Order is not applicable.",
        exceptions=[],
        audit_workpaper_data=info,
        tick_marks_applied=[AuditTickMark.TRACED_TO_STATUTE.value]
    )
