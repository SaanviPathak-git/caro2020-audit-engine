"""
Core Audit Engine Orchestrator
Executes substantive tests across all 21 CARO 2020 clauses and manages deliverables.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from .models import ClientMetadata, ClauseResult, ClauseStatus, AuditException
from .materiality import compute_audit_materiality
from ..utils.loaders import ClientDataLoader
from ..clauses import ALL_CLAUSE_TESTERS

class AuditExecutionSummary:
    def __init__(self, metadata: ClientMetadata, clause_results: List[ClauseResult]):
        self.metadata = metadata
        self.clause_results = clause_results
        self.total_clauses = len(clause_results)
        self.clean_count = sum(1 for r in clause_results if r.status == ClauseStatus.CLEAN)
        self.observation_count = sum(1 for r in clause_results if r.status == ClauseStatus.OBSERVATION)
        self.qualified_count = sum(1 for r in clause_results if r.status == ClauseStatus.QUALIFIED)
        self.na_count = sum(1 for r in clause_results if r.status == ClauseStatus.NOT_APPLICABLE)
        
        self.all_exceptions: List[AuditException] = []
        for r in clause_results:
            self.all_exceptions.extend(r.exceptions)
            
        self.total_exceptions = len(self.all_exceptions)
        self.total_quantified_exposure_cr = sum(
            e.amount_involved for e in self.all_exceptions if e.amount_involved
        )

class CaroAuditEngine:
    """Main execution engine for automated CARO 2020 substantive audit testing."""

    def __init__(self, client_dir: Path):
        self.client_dir = Path(client_dir)
        self.loader = ClientDataLoader(self.client_dir)
        self.raw_data: Dict[str, Any] = {}
        self.results: List[ClauseResult] = []
        self.summary: Optional[AuditExecutionSummary] = None

    def load_data(self):
        """Load all raw client schedules."""
        self.raw_data = self.loader.load_all_client_schedules()
        return self.raw_data

    def run_audit(self) -> AuditExecutionSummary:
        """Execute substantive tests across all 21 clauses."""
        if not self.raw_data:
            self.load_data()

        self.results = []
        for tester in ALL_CLAUSE_TESTERS:
            res: ClauseResult = tester(self.raw_data)
            self.results.append(res)

        self.summary = AuditExecutionSummary(self.raw_data["metadata"], self.results)
        return self.summary

    def get_result_by_clause_id(self, clause_id: str) -> Optional[ClauseResult]:
        for r in self.results:
            if r.clause_id.lower() == clause_id.lower() or r.clause_num.lower() == clause_id.lower():
                return r
        return None
