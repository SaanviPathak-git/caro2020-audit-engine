"""
Audit Materiality Computation per SA 320 (ICAI & IAASB Standards)
"""

from typing import Dict, Any
from .models import MaterialityConfig

def compute_audit_materiality(
    benchmark_name: str,
    benchmark_amount: float,
    overall_pct: float = 0.5,
    perf_pct: float = 75.0,
    trivial_pct: float = 5.0
) -> MaterialityConfig:
    """
    Computes Overall Materiality (OM), Performance Materiality (PM),
    and Clearly Trivial Threshold (CTT) in accordance with ICAI SA 320.
    """
    mat = MaterialityConfig(
        benchmark_name=benchmark_name,
        benchmark_amount=benchmark_amount,
        overall_materiality_pct=overall_pct,
        performance_materiality_pct=perf_pct,
        clearly_trivial_pct=trivial_pct
    )
    mat.calculate()
    return mat
