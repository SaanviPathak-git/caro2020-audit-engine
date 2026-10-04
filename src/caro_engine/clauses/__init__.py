"""
Substantive Audit Testing Modules for all 21 Clauses of CARO 2020
"""

from .clause_01_ppe import test_clause_01_ppe
from .clause_02_inventory import test_clause_02_inventory
from .clause_03_loans_granted import test_clause_03_loans_granted
from .clause_04_sec185_186 import test_clause_04_sec185_186
from .clause_05_deposits import test_clause_05_deposits
from .clause_06_cost_records import test_clause_06_cost_records
from .clause_07_statutory_dues import test_clause_07_statutory_dues
from .clause_08_undisclosed_income import test_clause_08_undisclosed_income
from .clause_09_borrowings_default import test_clause_09_borrowings_default
from .clause_10_ipo_private_placement import test_clause_10_ipo_private_placement
from .clause_11_fraud import test_clause_11_fraud
from .clause_12_nidhi import test_clause_12_nidhi
from .clause_13_related_party import test_clause_13_related_party
from .clause_14_internal_audit import test_clause_14_internal_audit
from .clause_15_non_cash_directors import test_clause_15_non_cash_directors
from .clause_16_rbi_nbfc import test_clause_16_rbi_nbfc
from .clause_17_cash_losses import test_clause_17_cash_losses
from .clause_18_auditor_resignation import test_clause_18_auditor_resignation
from .clause_19_going_concern import test_clause_19_going_concern
from .clause_20_csr import test_clause_20_csr
from .clause_21_cfs_qualifications import test_clause_21_cfs_qualifications

ALL_CLAUSE_TESTERS = [
    test_clause_01_ppe,
    test_clause_02_inventory,
    test_clause_03_loans_granted,
    test_clause_04_sec185_186,
    test_clause_05_deposits,
    test_clause_06_cost_records,
    test_clause_07_statutory_dues,
    test_clause_08_undisclosed_income,
    test_clause_09_borrowings_default,
    test_clause_10_ipo_private_placement,
    test_clause_11_fraud,
    test_clause_12_nidhi,
    test_clause_13_related_party,
    test_clause_14_internal_audit,
    test_clause_15_non_cash_directors,
    test_clause_16_rbi_nbfc,
    test_clause_17_cash_losses,
    test_clause_18_auditor_resignation,
    test_clause_19_going_concern,
    test_clause_20_csr,
    test_clause_21_cfs_qualifications,
]
