"""
Standard Audit Tickmarks & Evidentiary Annotations
Compliant with ICAI SA 230 (Audit Documentation) & Big 4 Workpaper Standards
"""

from typing import Dict

class AuditTickMark:
    VOUCHED = "✓"             # Verified against primary documentary evidence (tax invoice, title deed, agreement)
    CAST_VERIFIED = "Σ"       # Cast / cross-cast mathematically recalculated & verified
    BANK_RECONCILED = "Φ"     # Reconciled against third-party external confirmation / bank returns / portal
    STATUTORY_LIMIT = "λ"     # Verified against Companies Act / statutory limits & thresholds
    TRIAL_BALANCE_TIED = "GL" # Tied to General Ledger / Trial Balance as of balance sheet date
    EXCEPTION_FLAGGED = "X"   # Audit discrepancy detected, exceeds tolerance/threshold, flagged for CARO reporting
    DOCUMENT_INSPECTED = "Δ"  # Board minutes, internal audit reports, or legal notices inspected

TICKMARK_LEGEND: Dict[str, str] = {
    AuditTickMark.VOUCHED: "Vouched to underlying primary source document (invoices/deeds/contracts) per SA 500.",
    AuditTickMark.CAST_VERIFIED: "Mathematically cast and cross-cast recalculated by audit software without exception.",
    AuditTickMark.BANK_RECONCILED: "Reconciled with independent third-party confirmation / quarterly bank returns per SA 505.",
    AuditTickMark.STATUTORY_LIMIT: "Substantively tested against legal thresholds prescribed under Companies Act, 2013 / CARO 2020.",
    AuditTickMark.TRIAL_BALANCE_TIED: "Tied directly to the audited Trial Balance / General Ledger closing balances as of March 31.",
    AuditTickMark.EXCEPTION_FLAGGED: "Audit exception identified exceeding tolerable statutory threshold, requiring CARO disclosure.",
    AuditTickMark.DOCUMENT_INSPECTED: "Inspected minutes, approvals, or external legal documentation per SA 250."
}
