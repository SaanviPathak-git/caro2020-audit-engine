"""
Standard Audit Tickmarks & Evidentiary Annotations
Compliant with ICAI SA 230 (Audit Documentation) & Big 4 Electronic Workpaper Standards
"""

from typing import Dict

class AuditTickMark:
    VOUCHED = "[V]"             # Vouched to primary documentary evidence (tax invoices, deeds, agreements) per SA 500
    CAST_VERIFIED = "[C]"       # Mathematically cast, cross-cast & footings recalculated
    BANK_RECONCILED = "[CONF]"  # Reconciled against third-party external confirmation / bank returns per SA 505
    STATUTORY_LIMIT = "[STAT]"  # Substantively tested against Companies Act / statutory legal thresholds
    TRIAL_BALANCE_TIED = "[TB]" # Tied to audited Trial Balance / General Ledger closing balances as of March 31
    DOCUMENT_INSPECTED = "[DOC]"# Board minutes, approvals, internal audit, or legal notices inspected per SA 250
    EXCEPTION_FLAGGED = "[EX]"  # Audit exception / non-compliance flagged requiring CARO qualification

TICKMARK_LEGEND: Dict[str, str] = {
    AuditTickMark.VOUCHED: "Vouched to underlying primary source document (invoices/deeds/contracts) per SA 500.",
    AuditTickMark.CAST_VERIFIED: "Mathematically cast and cross-cast recalculated by audit software without exception.",
    AuditTickMark.BANK_RECONCILED: "Reconciled with independent third-party confirmation / quarterly bank returns per SA 505.",
    AuditTickMark.STATUTORY_LIMIT: "Substantively tested against legal thresholds prescribed under Companies Act, 2013 / CARO 2020.",
    AuditTickMark.TRIAL_BALANCE_TIED: "Tied directly to the audited Trial Balance / General Ledger closing balances as of March 31.",
    AuditTickMark.DOCUMENT_INSPECTED: "Inspected minutes, approvals, or external legal documentation per SA 250.",
    AuditTickMark.EXCEPTION_FLAGGED: "Audit exception identified exceeding tolerable statutory threshold, requiring CARO disclosure."
}
