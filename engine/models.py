"""
Pydantic Data Models and Schemas for CARO 2020 Substantive Audit Engine.
Complies with Companies Act, 2013 and ICAI Guidance Note on CARO 2020.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ClauseStatus(str, Enum):
    UNQUALIFIED = "UNQUALIFIED"                # Clean clause, no exceptions
    QUALIFIED = "QUALIFIED"                    # Audit exception / statutory disclosure required
    ADVERSE = "ADVERSE"                        # Adverse remark
    NOT_APPLICABLE = "NOT_APPLICABLE"          # E.g. Nidhi company, Auditor resignation
    DISCLAIMER = "DISCLAIMER"                  # Unable to obtain sufficient appropriate audit evidence


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditTickMark(str, Enum):
    CHECKED_TO_GL = "✓"                       # Checked to General Ledger / Trial Balance
    RECALCULATED = "^"                        # Mathematically recalculated by Auditor
    AGREED_TO_CONFIRMATION = "§"              # Agreed to third-party bank/custodian confirmation
    AGREED_TO_SUB_LEDGER = "«"                # Agreed to subsidiary ledger / asset register
    EXCEPTION_NOTED = "!"                     # Exception / non-compliance flagged
    TRACED_TO_STATUTE = "¶"                   # Traced to legal statute / gazette notification


class AuditException(BaseModel):
    clause_id: str
    clause_title: str
    severity: RiskSeverity
    exception_description: str
    statutory_reference: str
    quantification_inr_cr: Optional[float] = 0.0
    recommended_caro_disclosure: str
    tick_mark: AuditTickMark = AuditTickMark.EXCEPTION_NOTED


class ClauseResult(BaseModel):
    clause_id: str                            # e.g., "3(i)(a)", "3(ii)(b)"
    clause_number: str                        # e.g., "Clause (i)", "Clause (ii)"
    clause_title: str
    status: ClauseStatus
    severity: RiskSeverity
    summary_finding: str
    icai_standard_text: str                   # Legal text for the Auditor's Report
    exceptions: List[AuditException] = Field(default_factory=list)
    disclosure_table: Optional[List[Dict[str, Any]]] = None
    audit_workpaper_data: Optional[Dict[str, Any]] = None
    tick_marks_applied: List[str] = Field(default_factory=list)


class AuditEngagementMetadata(BaseModel):
    company_name: str
    cin: str
    financial_year: str
    balance_sheet_date: str
    audit_firm: str
    firm_registration_no: str
    engagement_partner: str
    membership_no: str
    company_type: str
    registered_office: str
    overall_materiality_inr_cr: float
    performance_materiality_inr_cr: float
    de_minimis_threshold_inr_cr: float
    working_capital_sanction_limit_inr_cr: float
    consortium_lead_bank: str


class AuditEngagementResult(BaseModel):
    metadata: AuditEngagementMetadata
    clause_results: Dict[str, ClauseResult]
    total_clauses_tested: int
    unqualified_count: int
    qualified_count: int
    not_applicable_count: int
    adverse_count: int
    total_exceptions_identified: int
    critical_risk_clauses: List[str]
    audit_opinion_summary: str
