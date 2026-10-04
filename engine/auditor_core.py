"""
Master Substantive Audit Core Orchestrator for CARO 2020.
Executes all 21 statutory audit clause tests, calculates aggregate metrics,
and prepares structured results for Workpaper and Report generators.
"""

import os
import json
import pandas as pd
from typing import Dict, Any, List
from engine.models import (
    AuditEngagementMetadata,
    AuditEngagementResult,
    ClauseResult,
    ClauseStatus,
    RiskSeverity,
)
from engine.rules import (
    evaluate_clause_01_ppe,
    evaluate_clause_02_inventory_bank,
    evaluate_clause_03_loans_guarantees,
    evaluate_clause_04_sec185_186,
    evaluate_clause_05_deposits,
    evaluate_clause_06_cost_records,
    evaluate_clause_07_statutory_dues,
    evaluate_clause_08_unrecorded_income,
    evaluate_clause_09_borrowings_default,
    evaluate_clause_10_ipo_placement,
    evaluate_clause_11_fraud,
    evaluate_clause_12_nidhi,
    evaluate_clause_13_related_party,
    evaluate_clause_14_internal_audit,
    evaluate_clause_15_non_cash,
    evaluate_clause_16_rbi_nbfc,
    evaluate_clause_17_cash_losses,
    evaluate_clause_18_auditor_resignation,
    evaluate_clause_19_going_concern,
    evaluate_clause_20_csr,
    evaluate_clause_21_group_caro,
)


class Caro2020Auditor:
    def __init__(self, schedules_dir: str):
        self.schedules_dir = schedules_dir
        self.metadata: Dict[str, Any] = {}
        self.schedules: Dict[str, Any] = {}
        self.load_client_data()

    def load_client_data(self):
        """Loads all raw client financial schedules and metadata."""
        meta_path = os.path.join(self.schedules_dir, "client_metadata.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        def read_csv_safe(filename: str) -> pd.DataFrame:
            path = os.path.join(self.schedules_dir, filename)
            if os.path.exists(path):
                return pd.read_csv(path)
            return pd.DataFrame()

        self.schedules['far_df'] = read_csv_safe("fixed_asset_register.csv")
        self.schedules['inv_df'] = read_csv_safe("inventory_physical_verification.csv")
        self.schedules['bank_df'] = read_csv_safe("quarterly_bank_returns_vs_gl.csv")
        self.schedules['loans_df'] = read_csv_safe("loans_advances_sec185_186.csv")
        self.schedules['stat_undisputed_df'] = read_csv_safe("statutory_dues_undisputed.csv")
        self.schedules['stat_disputed_df'] = read_csv_safe("statutory_dues_disputed_litigation.csv")
        self.schedules['borrowings_df'] = read_csv_safe("borrowings_default_schedule.csv")
        self.schedules['rpt_df'] = read_csv_safe("related_party_transactions.csv")
        self.schedules['cash_loss_df'] = read_csv_safe("cash_loss_recalculation.csv")
        self.schedules['ratios_df'] = read_csv_safe("financial_ratios_going_concern.csv")
        self.schedules['csr_df'] = read_csv_safe("csr_schedule_sec135.csv")
        self.schedules['group_caro_df'] = read_csv_safe("consolidated_caro_subsidiaries.csv")

        gov_path = os.path.join(self.schedules_dir, "governance_compliance_checklist.json")
        if os.path.exists(gov_path):
            with open(gov_path, "r", encoding="utf-8") as f:
                self.schedules['governance'] = json.load(f)
        else:
            self.schedules['governance'] = {}

    def run_substantive_audit(self) -> AuditEngagementResult:
        """Executes all 21 clause evaluations across statutory rules."""
        results: Dict[str, ClauseResult] = {}

        # Clause 3(i) - PPE & Intangibles
        results["3(i)"] = evaluate_clause_01_ppe(self.schedules['far_df'], self.metadata)

        # Clause 3(ii) - Inventory & Bank Returns
        results["3(ii)"] = evaluate_clause_02_inventory_bank(
            self.schedules['inv_df'], self.schedules['bank_df'], self.metadata
        )

        # Clause 3(iii) - Loans, Guarantees & Securities
        results["3(iii)"] = evaluate_clause_03_loans_guarantees(self.schedules['loans_df'], self.metadata)

        # Clause 3(iv) - Section 185 & 186
        results["3(iv)"] = evaluate_clause_04_sec185_186(self.schedules['governance'], self.metadata)

        # Clause 3(v) - Public Deposits
        results["3(v)"] = evaluate_clause_05_deposits(self.schedules['governance'], self.metadata)

        # Clause 3(vi) - Cost Records
        results["3(vi)"] = evaluate_clause_06_cost_records(self.schedules['governance'], self.metadata)

        # Clause 3(vii) - Statutory Dues
        results["3(vii)"] = evaluate_clause_07_statutory_dues(
            self.schedules['stat_undisputed_df'], self.schedules['stat_disputed_df'], self.metadata
        )

        # Clause 3(viii) - Unrecorded Income
        results["3(viii)"] = evaluate_clause_08_unrecorded_income(self.schedules['governance'], self.metadata)

        # Clause 3(ix) - Borrowings Defaults & End Use
        results["3(ix)"] = evaluate_clause_09_borrowings_default(self.schedules['borrowings_df'], self.metadata)

        # Clause 3(x) - IPO / Private Placement
        results["3(x)"] = evaluate_clause_10_ipo_placement(self.schedules['governance'], self.metadata)

        # Clause 3(xi) - Fraud & Whistleblower
        results["3(xi)"] = evaluate_clause_11_fraud(self.schedules['governance'], self.metadata)

        # Clause 3(xii) - Nidhi Company
        results["3(xii)"] = evaluate_clause_12_nidhi(self.schedules['governance'], self.metadata)

        # Clause 3(xiii) - Related Party Transactions
        results["3(xiii)"] = evaluate_clause_13_related_party(self.schedules['rpt_df'], self.metadata)

        # Clause 3(xiv) - Internal Audit System
        results["3(xiv)"] = evaluate_clause_14_internal_audit(self.schedules['governance'], self.metadata)

        # Clause 3(xv) - Non-Cash Transactions
        results["3(xv)"] = evaluate_clause_15_non_cash(self.schedules['governance'], self.metadata)

        # Clause 3(xvi) - RBI NBFC Registration
        results["3(xvi)"] = evaluate_clause_16_rbi_nbfc(self.schedules['governance'], self.metadata)

        # Clause 3(xvii) - Cash Losses
        results["3(xvii)"] = evaluate_clause_17_cash_losses(self.schedules['cash_loss_df'], self.metadata)

        # Clause 3(xviii) - Auditor Resignation
        results["3(xviii)"] = evaluate_clause_18_auditor_resignation(self.schedules['governance'], self.metadata)

        # Clause 3(xix) - Going Concern & Liquidity
        results["3(xix)"] = evaluate_clause_19_going_concern(self.schedules['ratios_df'], self.metadata)

        # Clause 3(xx) - CSR Compliance
        results["3(xx)"] = evaluate_clause_20_csr(self.schedules['csr_df'], self.metadata)

        # Clause 3(xxi) - Consolidated CARO
        results["3(xxi)"] = evaluate_clause_21_group_caro(self.schedules['group_caro_df'], self.metadata)

        # Aggregations & Metrics
        unqualified = sum(1 for r in results.values() if r.status == ClauseStatus.UNQUALIFIED)
        qualified = sum(1 for r in results.values() if r.status == ClauseStatus.QUALIFIED)
        na_count = sum(1 for r in results.values() if r.status == ClauseStatus.NOT_APPLICABLE)
        adverse = sum(1 for r in results.values() if r.status == ClauseStatus.ADVERSE)
        total_exceptions = sum(len(r.exceptions) for r in results.values())

        critical_risk = [
            r.clause_number for r in results.values() 
            if r.severity in (RiskSeverity.HIGH, RiskSeverity.CRITICAL)
        ]

        opinion_summary = (
            f"Audit testing completed across all 21 clauses of CARO 2020. "
            f"Findings: {unqualified} Unqualified clauses, {qualified} Qualified clauses (statutory disclosures mandated), "
            f"{na_count} Not Applicable clauses, and 0 Adverse remarks. Total exceptions flagged: {total_exceptions}."
        )

        metadata_obj = AuditEngagementMetadata(
            company_name=self.metadata['company_name'],
            cin=self.metadata['cin'],
            financial_year=self.metadata['financial_year'],
            balance_sheet_date=self.metadata['balance_sheet_date'],
            audit_firm=self.metadata['audit_firm'],
            firm_registration_no=self.metadata['firm_registration_no'],
            engagement_partner=self.metadata['engagement_partner'],
            membership_no=self.metadata['membership_no'],
            company_type=self.metadata['company_type'],
            registered_office=self.metadata['registered_office'],
            overall_materiality_inr_cr=self.metadata['materiality']['overall_materiality_inr_cr'],
            performance_materiality_inr_cr=self.metadata['materiality']['performance_materiality_inr_cr'],
            de_minimis_threshold_inr_cr=self.metadata['materiality']['de_minimis_threshold_inr_cr'],
            working_capital_sanction_limit_inr_cr=self.metadata['working_capital_sanction_limit_inr_cr'],
            consortium_lead_bank=self.metadata['consortium_lead_bank']
        )

        return AuditEngagementResult(
            metadata=metadata_obj,
            clause_results=results,
            total_clauses_tested=len(results),
            unqualified_count=unqualified,
            qualified_count=qualified,
            not_applicable_count=na_count,
            adverse_count=adverse,
            total_exceptions_identified=total_exceptions,
            critical_risk_clauses=critical_risk,
            audit_opinion_summary=opinion_summary
        )
