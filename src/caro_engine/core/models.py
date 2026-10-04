"""
Data Models for CARO 2020 Statutory Audit Testing Engine
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ClauseStatus(str, Enum):
    CLEAN = "CLEAN"                     # Unmodified ICAI standard clause
    OBSERVATION = "OBSERVATION"         # Procedural point noted, no statutory breach
    QUALIFIED = "QUALIFIED"             # Statutory non-compliance / threshold breached
    NOT_APPLICABLE = "NOT_APPLICABLE"   # Clause not applicable to this entity (e.g. Nidhi)

class AuditException(BaseModel):
    clause_id: str
    headline: str
    description: str
    amount_involved: Optional[float] = 0.0
    statutory_threshold: Optional[float] = None
    variance_pct: Optional[float] = None
    forum_or_counterparty: Optional[str] = None
    severity: str = "HIGH"  # INFO, WARNING, HIGH, CRITICAL

class ClauseResult(BaseModel):
    clause_id: str                      # e.g., "Clause (ii)(b)"
    clause_num: str                     # e.g., "ii"
    clause_sub: str                     # e.g., "(b)"
    title: str                          # e.g., "Working Capital Bank Statements vs Books Reconciliation"
    status: ClauseStatus = ClauseStatus.CLEAN
    substantive_tests: List[str] = Field(default_factory=list)
    observations: List[str] = Field(default_factory=list)
    exceptions: List[AuditException] = Field(default_factory=list)
    disclosure_table_headers: List[str] = Field(default_factory=list)
    disclosure_table_rows: List[List[Any]] = Field(default_factory=list)
    workpaper_rows: List[Any] = Field(default_factory=list)
    icai_report_text: str = ""
    tickmarks_applied: List[str] = Field(default_factory=list)

class MaterialityConfig(BaseModel):
    benchmark_name: str = "Turnover / Revenue from Operations"
    benchmark_amount: float = 0.0
    overall_materiality_pct: float = 0.5   # 0.5% of Revenue
    overall_materiality: float = 0.0
    performance_materiality_pct: float = 75.0 # 75% of Overall Materiality
    performance_materiality: float = 0.0
    clearly_trivial_pct: float = 5.0      # 5% of Overall Materiality
    clearly_trivial_threshold: float = 0.0

    def calculate(self):
        self.overall_materiality = (self.benchmark_amount * self.overall_materiality_pct) / 100.0
        self.performance_materiality = (self.overall_materiality * self.performance_materiality_pct) / 100.0
        self.clearly_trivial_threshold = (self.overall_materiality * self.clearly_trivial_pct) / 100.0

class ClientMetadata(BaseModel):
    company_name: str
    cin: str
    financial_year: str = "2023-24"
    audit_period_start: str = "2023-04-01"
    audit_period_end: str = "2024-03-31"
    lead_partner: str = "CA Rajesh Mehta, FCA"
    firm_name: str = "Walker Chandiok & Co LLP / B S R & Co. LLP"
    nature_of_business: str = "Automotive Manufacturing & Mobility Solutions"
    is_listed: bool = True
    reporting_currency: str = "INR"
    unit_scale: str = "Crores" # Values in INR Crores
    materiality: Optional[MaterialityConfig] = None
