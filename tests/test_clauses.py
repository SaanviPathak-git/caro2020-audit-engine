"""
Unit Tests for CARO 2020 Substantive Audit Testing Clauses
"""

import pytest
import pandas as pd
from pathlib import Path
from caro_engine.core.models import ClauseStatus
from caro_engine.clauses.clause_01_ppe import test_clause_01_ppe as run_clause_01_ppe
from caro_engine.clauses.clause_02_inventory import test_clause_02_inventory as run_clause_02_inventory
from caro_engine.clauses.clause_07_statutory_dues import test_clause_07_statutory_dues as run_clause_07_statutory_dues
from caro_engine.clauses.clause_17_cash_losses import test_clause_17_cash_losses as run_clause_17_cash_losses
from caro_engine.clauses.clause_19_going_concern import test_clause_19_going_concern as run_clause_19_going_concern

def test_revaluation_10_percent_threshold():
    """Test Clause (i)(d): Revaluation >= 10% without Registered Valuer triggers qualification."""
    far_df = pd.DataFrame([
        {
            "asset_class": "Plant & Machinery",
            "gross_block_beg": 100.0,
            "additions": 0.0,
            "disposals": 0.0,
            "revaluation_amount": 15.0,
            "gross_block_end": 115.0,
            "accum_depr": 20.0,
            "net_carrying_amount": 95.0,
            "physical_verified": "Yes",
            "revalued_by_registered_valuer": "No",
            "revaluation_pct_change": 15.0  # >= 10%
        }
    ])
    mock_data = {
        "fixed_asset_register": far_df,
        "title_deeds_register": pd.DataFrame(),
        "metadata": type("Meta", (), {"company_name": "Test Co"})()
    }
    res = run_clause_01_ppe(mock_data)
    assert res.status == ClauseStatus.QUALIFIED
    assert any("Registered Valuer" in e.headline for e in res.exceptions)

def test_quarterly_bank_returns_discrepancy():
    """Test Clause (ii)(b): Discrepancies in working capital bank returns for limits > ₹5 Cr."""
    bank_df = pd.DataFrame([
        {
            "quarter": "Q1 (June 2023)",
            "bank_name": "State Bank of India",
            "sanctioned_limit_cr": 25.0, # > 5 Cr
            "security_particulars": "Hypothecation of inventory",
            "current_asset_type": "Inventory",
            "amount_per_books_cr": 100.0,
            "amount_reported_to_bank_cr": 115.0,
            "difference_cr": -15.0,
            "variance_pct": -15.0, # Exceeds 10%
            "reason_for_difference": "Unreconciled drawing power adjustment"
        }
    ])
    mock_data = {
        "inventory_physical_verification": pd.DataFrame(),
        "quarterly_bank_returns": bank_df
    }
    res = run_clause_02_inventory(mock_data)
    assert res.status == ClauseStatus.QUALIFIED
    assert len(res.disclosure_table_rows) == 1
    assert any("bank stock statement" in e.headline.lower() for e in res.exceptions)

def test_statutory_dues_arrears_over_6_months():
    """Test Clause (vii)(a): Undisputed arrears unpaid > 6 months as of March 31 trigger qualification."""
    dues_df = pd.DataFrame([
        {
            "statute_name": "Central Goods and Services Tax Act 2017",
            "nature_of_dues": "CGST Output Tax",
            "amount_cr": 12.5,
            "period_to_which_relates": "FY 2023-24 (Q1)",
            "due_date": "2023-06-20",
            "payment_date": "Unpaid",
            "days_overdue_as_of_mar31": 280,
            "exceeds_6_months": "Yes"
        }
    ])
    mock_data = {
        "statutory_dues_ledger": dues_df,
        "litigation_register": pd.DataFrame()
    }
    res = run_clause_07_statutory_dues(mock_data)
    assert res.status == ClauseStatus.QUALIFIED
    assert len(res.disclosure_table_rows) == 1
    assert any("unpaid > 6 months" in e.headline for e in res.exceptions)

def test_cash_loss_recalculation():
    """Test Clause (xvii): Recalculation adjusts PBT for depreciation and flags cash loss."""
    pnl_data = {
        "current_year_fy24": {
            "financial_year": "2023-24",
            "profit_loss_before_tax_cr": -100.0,
            "depreciation_and_amortization_cr": 30.0,
            "impairment_loss_cr": 0.0,
            "unrealized_fx_gain_loss_cr": 0.0,
            "other_non_cash_items_cr": 0.0,
            "has_cash_loss": True
        },
        "preceding_year_fy23": {
            "financial_year": "2022-23",
            "profit_loss_before_tax_cr": 50.0,
            "depreciation_and_amortization_cr": 25.0,
            "impairment_loss_cr": 0.0,
            "unrealized_fx_gain_loss_cr": 0.0,
            "other_non_cash_items_cr": 0.0,
            "has_cash_loss": False
        }
    }
    mock_data = {"cash_flow_and_pnl": pnl_data}
    res = run_clause_17_cash_losses(mock_data)
    assert res.status == ClauseStatus.QUALIFIED
    assert any("Cash losses incurred" in e.headline for e in res.exceptions)
    assert "₹70.00 Crore" in res.icai_report_text # -100 + 30 = -70 cash loss
