"""
Integration Tests for CaroAuditEngine Orchestrator
"""

import pytest
from pathlib import Path
from caro_engine.core.engine import CaroAuditEngine
from caro_engine.core.models import ClauseStatus

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_clients"

def test_tata_motors_full_audit_run():
    tata_path = SAMPLE_DIR / "tata_motors_fy24"
    assert tata_path.exists(), f"Tata Motors sample path missing: {tata_path}"
    
    engine = CaroAuditEngine(tata_path)
    summary = engine.run_audit()
    
    assert summary.total_clauses == 21
    assert summary.metadata.company_name == "Tata Motors Limited"
    # Materiality calculation
    assert summary.metadata.materiality.overall_materiality > 300.0  # ~366.44 Cr
    assert summary.clean_count >= 15
    # Should flag the municipal tax arrears in Clause vii
    cl7 = engine.get_result_by_clause_id("Clause (vii)")
    assert cl7 is not None
    assert cl7.status == ClauseStatus.QUALIFIED

def test_zenith_infra_qualified_audit_run():
    zenith_path = SAMPLE_DIR / "zenith_infra_fy24"
    assert zenith_path.exists(), f"Zenith sample path missing: {zenith_path}"
    
    engine = CaroAuditEngine(zenith_path)
    summary = engine.run_audit()
    
    assert summary.total_clauses == 21
    assert summary.metadata.company_name == "Zenith Infrastructure & Power Limited"
    assert summary.qualified_count >= 12
    assert summary.total_exceptions >= 20
    assert summary.total_quantified_exposure_cr > 1000.0
