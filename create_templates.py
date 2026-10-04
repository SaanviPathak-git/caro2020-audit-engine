import json
import zipfile
from pathlib import Path

templates_dir = Path("data/templates")
templates_dir.mkdir(parents=True, exist_ok=True)

# 1. Metadata JSON
metadata = {
  "company_name": "Acme Industries Limited",
  "cin": "L17110MH2018PLC305891",
  "financial_year": "2023-24",
  "audit_period_start": "2023-04-01",
  "audit_period_end": "2024-03-31",
  "lead_partner": "CA Saanvi Pathak, FCA (Membership No. 052419)",
  "firm_name": "Pathak & Associates LLP, Chartered Accountants (Firm Reg No. 102345W)",
  "nature_of_business": "Manufacturing, Engineering & Industrial Solutions",
  "is_listed": True,
  "reporting_currency": "INR",
  "unit_scale": "Crores",
  "standalone_or_consolidated": "Standalone",
  "materiality": {
    "benchmark_name": "Turnover / Revenue from Operations",
    "benchmark_amount": 500.00,
    "overall_materiality_pct": 0.5,
    "performance_materiality_pct": 75.0,
    "clearly_trivial_pct": 5.0
  }
}

# 2. CSV Schedules
csv_files = {
    "fixed_asset_register.csv": (
        "asset_class,gross_block_beg,additions,disposals,revaluation_amount,gross_block_end,accum_depr,net_carrying_amount,physical_verified,revalued_by_registered_valuer,revaluation_pct_change\n"
        "Freehold Land,50.0,0.0,0.0,0.0,50.0,0.0,50.0,Yes,No,0.0\n"
        "Buildings,80.0,5.0,0.0,0.0,85.0,20.0,65.0,Yes,No,0.0\n"
        "Plant & Machinery,150.0,15.0,0.0,0.0,165.0,45.0,120.0,Yes,No,0.0\n"
        "Computers & IT,10.0,2.0,0.0,0.0,12.0,6.0,6.0,Yes,No,0.0\n"
        "Vehicles,5.0,0.5,0.0,0.0,5.5,2.0,3.5,Yes,No,0.0\n"
    ),
    "title_deeds_register.csv": (
        "balance_sheet_line_item,property_description,gross_carrying_value_cr,held_in_name_of,is_promoter_director_relative,period_held_years,reason_for_not_held\n"
        "Freehold Land,Main Manufacturing Plant Plot 42,50.0,Acme Industries Limited,No,8,Title clear and registered in company name\n"
        "Buildings,Corporate Registered Office,35.0,Acme Industries Limited,No,6,Title clear and registered in company name\n"
    ),
    "inventory_physical_verification.csv": (
        "plant_location,inventory_class,book_value_cr,physical_count_value_cr,variance_amount_cr,variance_pct,exceeds_10pct_statutory_threshold,properly_adjusted_in_books,frequency_of_count\n"
        "Main Plant,Raw Materials,25.0,24.8,-0.2,-0.8,No,Yes,Continuous cycle count during the year\n"
        "Main Plant,Finished Goods,18.0,18.1,0.1,0.55,No,Yes,Quarterly physical verification\n"
        "Warehouse North,Components & Spares,8.0,7.95,-0.05,-0.62,No,Yes,Annual physical count at year-end\n"
    ),
    "quarterly_bank_returns.csv": (
        "quarter,bank_name,sanctioned_limit_cr,security_particulars,current_asset_type,amount_per_books_cr,amount_reported_to_bank_cr,difference_cr,variance_pct,reason_for_difference\n"
        "Q1 (June 2023),State Bank of India,40.0,Hypothecation of stocks and receivables,Stock & Book Debts,48.5,48.5,0.0,0.0,In exact agreement with books\n"
        "Q2 (Sept 2023),State Bank of India,40.0,Hypothecation of stocks and receivables,Stock & Book Debts,51.2,51.2,0.0,0.0,In exact agreement with books\n"
        "Q3 (Dec 2023),State Bank of India,40.0,Hypothecation of stocks and receivables,Stock & Book Debts,53.0,53.0,0.0,0.0,In exact agreement with books\n"
        "Q4 (Mar 2024),State Bank of India,40.0,Hypothecation of stocks and receivables,Stock & Book Debts,55.4,55.4,0.0,0.0,In exact agreement with books\n"
    ),
    "loans_investments_guarantees.csv": (
        "party_name,relationship,type,amount_granted_during_year_cr,balance_outstanding_cr,terms_prejudicial,schedule_stipulated,repayment_regular,overdue_gt_90_days_cr,reasonable_steps_taken,renewed_or_extended_cr,repayable_on_demand_or_no_terms\n"
        "Acme Engineering Products Pvt Ltd,Subsidiary,Loan,15.0,12.0,No,Yes,Yes,0.0,Not Applicable,0.0,No\n"
    ),
    "statutory_dues_ledger.csv": (
        "statute_name,nature_of_dues,amount_cr,period_to_which_relates,due_date,payment_date,status,days_overdue_as_of_mar31,exceeds_6_months\n"
        "Central Goods and Services Tax Act 2017,Output CGST & SGST,4.20,March 2024,2024-04-20,2024-04-18,Paid within statutory due date,0,No\n"
        "Employees Provident Funds Act 1952,PF & Pension Contribution,0.85,March 2024,2024-04-15,2024-04-12,Paid within statutory due date,0,No\n"
        "Income Tax Act 1961,TDS Deduction,1.10,March 2024,2024-04-30,2024-04-25,Paid within statutory due date,0,No\n"
    ),
    "litigation_register.csv": (
        "statute_name,nature_of_dues,gross_disputed_amount_cr,amount_paid_under_protest_cr,net_unpaid_amount_cr,period_to_which_relates,forum_where_pending\n"
        "Income Tax Act 1961,Disallowance u/s 14A,1.50,0.30,1.20,AY 2019-20,Income Tax Appellate Tribunal (ITAT)\n"
        "Central Goods and Services Tax Act 2017,ITC Transitional Credit,0.80,0.15,0.65,FY 2017-18,High Court of Judicature\n"
    ),
    "borrowings_default_schedule.csv": (
        "nature_of_borrowing,name_of_lender,sanctioned_amount_cr,outstanding_balance_mar31_cr,default_principal_cr,default_interest_cr,days_delay,remarks\n"
        "Rupee Term Loan,State Bank of India,50.0,38.0,0.0,0.0,0,All principal and interest payments serviced regularly on due dates\n"
        "Working Capital Facility,HDFC Bank,30.0,22.5,0.0,0.0,0,Account regular and compliant with sanctioned limits\n"
    ),
    "term_loans_end_use.csv": (
        "lender_name,loan_facility,sanctioned_amount_cr,stated_purpose,drawn_amount_cr,utilized_for_purpose_cr,unutilized_diverted_amount_cr,audit_verification_procedure\n"
        "State Bank of India,Rupee Term Loan,50.00,Expansion of plant manufacturing line,38.00,38.00,0.00,Verified to machinery supplier invoices and capital work-in-progress ledger entries\n"
    ),
    "related_party_transactions.csv": (
        "related_party_name,relationship,nature_of_transaction,transaction_value_cr,audit_committee_prior_approval,board_approval_sec188,shareholder_approval_sec188,arms_length_basis_tested,disclosed_in_financial_statements_note38\n"
        "Acme Engineering Products Pvt Ltd,Subsidiary,Purchase of component sub-assemblies,12.50,Yes,Yes,Not Applicable,Yes,Yes\n"
    ),
    "csr_schedule.csv": (
        "financial_year,net_profit_avg_3yr_cr,statutory_2pct_obligation_cr,actual_csr_spent_cr,unspent_ongoing_projects_cr,transferred_to_special_unspent_bank_account,special_account_transfer_date,unspent_other_projects_cr,transferred_to_schedule_vii_fund,schedule_vii_transfer_date,shortfall_or_surplus_cr\n"
        "FY 2023-24,35.0,0.70,0.75,0.0,Not Applicable,N/A,0.0,Not Applicable,N/A,0.05\n"
    )
}

# 3. JSON Schedules
cash_flow_and_pnl = {
  "current_year_fy24": {
    "financial_year": "2023-24",
    "profit_loss_before_tax_cr": 45.00,
    "depreciation_and_amortization_cr": 12.00,
    "impairment_loss_cr": 0.00,
    "unrealized_fx_gain_loss_cr": -0.50,
    "other_non_cash_items_cr": 1.20,
    "recalculated_cash_profit_loss_cr": 57.70,
    "has_cash_loss": False
  },
  "preceding_year_fy23": {
    "financial_year": "2022-23",
    "profit_loss_before_tax_cr": 38.00,
    "depreciation_and_amortization_cr": 11.50,
    "impairment_loss_cr": 0.00,
    "unrealized_fx_gain_loss_cr": -0.40,
    "other_non_cash_items_cr": 0.80,
    "recalculated_cash_profit_loss_cr": 49.90,
    "has_cash_loss": False
  }
}

balance_sheet_ratios = {
  "financial_ratios": {
    "current_ratio": {
      "numerator_name": "Current Assets",
      "numerator_value_cr": 125.00,
      "denominator_name": "Current Liabilities",
      "denominator_value_cr": 95.00,
      "ratio_current_year": 1.32,
      "ratio_prior_year": 1.25,
      "variance_pct": 5.60,
      "threshold_benchmark": 1.00,
      "is_healthy": True
    },
    "debt_equity_ratio": {
      "numerator_name": "Total Debt",
      "numerator_value_cr": 60.50,
      "denominator_name": "Total Equity (Net Worth)",
      "denominator_value_cr": 140.00,
      "ratio_current_year": 0.43,
      "ratio_prior_year": 0.52,
      "variance_pct": -17.31,
      "threshold_benchmark": 2.00,
      "is_healthy": True
    },
    "debt_service_coverage_ratio": {
      "numerator_name": "EBITDA - Tax",
      "numerator_value_cr": 58.00,
      "denominator_name": "Debt Service (Interest + Principal)",
      "denominator_value_cr": 18.50,
      "ratio_current_year": 3.14,
      "ratio_prior_year": 2.85,
      "variance_pct": 10.18,
      "threshold_benchmark": 1.25,
      "is_healthy": True
    },
    "return_on_equity_pct": {
      "numerator_name": "Net Profit after Tax",
      "numerator_value_cr": 32.50,
      "denominator_name": "Average Shareholder Equity",
      "denominator_value_cr": 135.00,
      "ratio_current_year": 24.07,
      "ratio_prior_year": 21.50,
      "variance_pct": 11.95,
      "threshold_benchmark": 10.00,
      "is_healthy": True
    },
    "inventory_turnover_ratio": {
      "numerator_name": "Cost of Goods Sold",
      "numerator_value_cr": 310.00,
      "denominator_name": "Average Inventory",
      "denominator_value_cr": 51.00,
      "ratio_current_year": 6.08,
      "ratio_prior_year": 5.80,
      "variance_pct": 4.83,
      "threshold_benchmark": 4.00,
      "is_healthy": True
    },
    "trade_receivables_turnover_ratio": {
      "numerator_name": "Revenue from Operations",
      "numerator_value_cr": 500.00,
      "denominator_name": "Average Trade Receivables",
      "denominator_value_cr": 42.00,
      "ratio_current_year": 11.90,
      "ratio_prior_year": 11.20,
      "variance_pct": 6.25,
      "threshold_benchmark": 6.00,
      "is_healthy": True
    },
    "trade_payables_turnover_ratio": {
      "numerator_name": "Total Purchases",
      "numerator_value_cr": 260.00,
      "denominator_name": "Average Trade Payables",
      "denominator_value_cr": 52.00,
      "ratio_current_year": 5.00,
      "ratio_prior_year": 4.80,
      "variance_pct": 4.17,
      "threshold_benchmark": 2.00,
      "is_healthy": True
    },
    "net_capital_turnover_ratio": {
      "numerator_name": "Revenue from Operations",
      "numerator_value_cr": 500.00,
      "denominator_name": "Working Capital",
      "denominator_value_cr": 30.00,
      "ratio_current_year": 16.67,
      "ratio_prior_year": 15.20,
      "variance_pct": 9.67,
      "threshold_benchmark": 5.00,
      "is_healthy": True
    },
    "net_profit_margin_pct": {
      "numerator_name": "Net Profit after Tax",
      "numerator_value_cr": 32.50,
      "denominator_name": "Revenue from Operations",
      "denominator_value_cr": 500.00,
      "ratio_current_year": 6.50,
      "ratio_prior_year": 5.80,
      "variance_pct": 12.07,
      "threshold_benchmark": 2.00,
      "is_healthy": True
    },
    "return_on_capital_employed_pct": {
      "numerator_name": "EBIT",
      "numerator_value_cr": 55.00,
      "denominator_name": "Capital Employed",
      "denominator_value_cr": 200.50,
      "ratio_current_year": 27.43,
      "ratio_prior_year": 24.10,
      "variance_pct": 13.82,
      "threshold_benchmark": 8.00,
      "is_healthy": True
    }
  },
  "one_year_liquidity_gap_analysis": {
    "financial_assets_realizable_within_1_year_cr": {
      "cash_and_cash_equivalents": 22.50,
      "bank_balances_other": 8.00,
      "current_investments_treasury": 15.00,
      "trade_receivables": 42.00,
      "other_current_financial_assets": 5.50,
      "total_realizable_financial_assets_cr": 93.00
    },
    "financial_liabilities_maturing_within_1_year_cr": {
      "current_borrowings_and_maturities": 12.00,
      "trade_payables": 52.00,
      "other_current_financial_liabilities": 6.50,
      "total_maturing_financial_liabilities_cr": 70.50
    },
    "net_liquidity_surplus_deficit_cr": 22.50,
    "undrawn_sanctioned_credit_lines_cr": 18.00,
    "total_effective_liquidity_cushion_cr": 40.50,
    "going_concern_material_uncertainty_identified": False
  }
}

governance_check_responses = {
  "clause_iv_sec185_186": {
    "loans_to_directors_sec185_compliant": True,
    "loans_guarantees_investments_sec186_compliant": True,
    "special_resolution_passed_if_exceeding_limits": True,
    "register_maintained_in_form_mbp2": True,
    "remarks": "The Company has complied with the provisions of Sections 185 and 186 of the Act in respect of loans, investments, guarantees and security."
  },
  "clause_v_public_deposits": {
    "has_accepted_public_deposits": False,
    "directives_issued_by_rbi_complied": True,
    "provisions_of_sections_73_to_76_complied": True,
    "clb_or_nclt_orders_outstanding": False,
    "remarks": "The Company has not accepted any deposits or deemed deposits within the meaning of Sections 73 to 76 of the Act and the rules made thereunder."
  },
  "clause_vi_cost_records": {
    "cost_records_mandated_by_central_govt": True,
    "specified_under_section_148_1": True,
    "cost_accounts_and_records_maintained": True,
    "substantive_audit_check": "We have broadly reviewed the books of account maintained by the Company pursuant to the rules made by the Central Government for the maintenance of cost records under Section 148(1) of the Act and are of the opinion that, prima facie, the prescribed accounts and records have been made and maintained."
  },
  "clause_viii_undisclosed_income": {
    "unrecorded_transactions_surrendered_as_income": False,
    "search_or_survey_under_income_tax_act": False,
    "previously_unrecorded_income_recorded_in_books": False,
    "remarks": "No transactions have been surrendered or disclosed as income during the year in the tax assessments under the Income Tax Act, 1961."
  },
  "clause_x_ipo_preferential_allotment": {
    "moneys_raised_by_ipo_or_fpo": False,
    "preferential_allotment_or_private_placement": False,
    "section_42_and_62_complied": True,
    "funds_used_for_intended_purposes": True,
    "remarks": "The Company did not raise any money by way of initial public offer or further public offer or preferential allotment or private placement during the year."
  },
  "clause_xi_fraud_reporting": {
    "fraud_by_company_noticed_or_reported": False,
    "fraud_on_company_noticed_or_reported": False,
    "form_adt4_filed_with_central_govt": False,
    "whistleblower_complaints_received": 0,
    "whistleblower_complaints_considered_by_auditor": True,
    "substantive_audit_check": "No fraud by the Company or any fraud on the Company has been noticed or reported during the year. No report under Section 143(12) in Form ADT-4 has been filed."
  },
  "clause_xii_nidhi_company": {
    "is_nidhi_company": False,
    "remarks": "The Company is not a Nidhi company as per the provisions of the Companies Act, 2013. Accordingly, clause 3(xii) is not applicable."
  },
  "clause_xiv_internal_audit": {
    "internal_audit_system_in_place": True,
    "commensurate_with_size_and_nature": True,
    "internal_audit_reports_reviewed_by_statutory_auditor": True,
    "substantive_audit_check": "In our opinion, the Company has an internal audit system commensurate with the size and the nature of its business per SA 610."
  },
  "clause_xv_non_cash_transactions": {
    "non_cash_transactions_with_directors": False,
    "provisions_of_section_192_complied": True,
    "remarks": "In our opinion, the Company has not entered into any non-cash transactions with its directors or persons connected with them within the meaning of Section 192."
  },
  "clause_xvi_rbi_nbfc_registration": {
    "required_to_be_registered_under_45_ia": False,
    "has_conducted_nbfc_activities": False,
    "is_core_investment_company_cic": False,
    "group_cic_count": 0,
    "remarks": "The Company is not required to be registered under Section 45-IA of the Reserve Bank of India Act, 1934."
  },
  "clause_xviii_auditor_resignation": {
    "resignation_of_statutory_auditor_during_year": False,
    "form_adt3_inspected": False,
    "issues_or_objections_raised": "None",
    "remarks": "There has been no resignation of the statutory auditors during the year. Accordingly, clause 3(xviii) is not applicable."
  },
  "clause_xxi_cfs_qualifications": {
    "is_consolidated_audit": False,
    "subsidiary_caro_qualifications": [],
    "remarks": "This standalone audit report does not include consolidated statements. Accordingly, clause 3(xxi) is not applicable for the standalone report."
  }
}

readme_instructions = """CARO 2020 CLIENT SCHEDULE TEMPLATES & INSTRUCTIONS
===================================================

This package contains standard financial schedules and registers required for
automated substantive testing under Companies (Auditor's Report) Order, 2020.

HOW TO USE:
1. Edit any or all CSV and JSON files in Excel, LibreOffice, or any text editor with your company's data.
2. In the CARO 2020 Web Engine, select 'Upload Your Company's Data (Custom Audit)'.
3. Enter your company's Name, CIN, Financial Year, and Revenue Turnover Benchmark.
4. Upload your modified CSV / JSON files or re-zip this entire folder and upload the .zip file!
5. Any schedule you do not upload will automatically use compliant baseline values.

SCHEDULES INCLUDED:
1. metadata.json                       - Company details, CIN, FY, SA 320 materiality benchmark
2. fixed_asset_register.csv            - Clause 3(i)(a)-(d): Gross block, revaluations >10%, physical verification
3. title_deeds_register.csv            - Clause 3(i)(c): Immovable property title deeds not held in company name
4. inventory_physical_verification.csv - Clause 3(ii)(a): Physical verification, >10% discrepancies per class
5. quarterly_bank_returns.csv          - Clause 3(ii)(b): Working capital >Rs. 5 Cr statements vs books
6. loans_investments_guarantees.csv    - Clause 3(iii)(a)-(f): Loans to subsidiaries/associates/others, terms, overdue >90 days
7. statutory_dues_ledger.csv           - Clause 3(vii)(a): Undisputed statutory dues >6 months overdue as of March 31
8. litigation_register.csv             - Clause 3(vii)(b): Disputed statutory dues pending before appellate forums
9. borrowings_default_schedule.csv     - Clause 3(ix)(a): Default in repayment of loans or borrowings to banks/lenders
10. term_loans_end_use.csv             - Clause 3(ix)(c): End-use verification of term loans for stated purpose
11. related_party_transactions.csv     - Clause 3(xiii): Sec 177/188 compliance, arm's length test, Note 38 disclosures
12. csr_schedule.csv                   - Clause 3(xx)(a)-(b): Sec 135 CSR obligations, unspent transfers within statutory timelines
13. cash_flow_and_pnl.json             - Clause 3(xvii): Recalculated cash profit / cash loss for current & preceding FY
14. balance_sheet_ratios.json          - Clause 3(xix): 10 Schedule III financial ratios & 1-year asset-liability liquidity gap
15. governance_check_responses.json    - Clauses 3(iv), (v), (vi), (viii), (x), (xi), (xii), (xiv), (xv), (xvi), (xviii), (xxi)
"""

# Save individual files to data/templates/
(templates_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
(templates_dir / "cash_flow_and_pnl.json").write_text(json.dumps(cash_flow_and_pnl, indent=2), encoding="utf-8")
(templates_dir / "balance_sheet_ratios.json").write_text(json.dumps(balance_sheet_ratios, indent=2), encoding="utf-8")
(templates_dir / "governance_check_responses.json").write_text(json.dumps(governance_check_responses, indent=2), encoding="utf-8")
(templates_dir / "README_INSTRUCTIONS.txt").write_text(readme_instructions, encoding="utf-8")

for filename, content in csv_files.items():
    (templates_dir / filename).write_text(content, encoding="utf-8")

# Create zip archive
zip_path = templates_dir / "caro_audit_blank_templates.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(templates_dir / "README_INSTRUCTIONS.txt", arcname="README_INSTRUCTIONS.txt")
    zipf.write(templates_dir / "metadata.json", arcname="metadata.json")
    zipf.write(templates_dir / "cash_flow_and_pnl.json", arcname="cash_flow_and_pnl.json")
    zipf.write(templates_dir / "balance_sheet_ratios.json", arcname="balance_sheet_ratios.json")
    zipf.write(templates_dir / "governance_check_responses.json", arcname="governance_check_responses.json")
    for filename in csv_files.keys():
        zipf.write(templates_dir / filename, arcname=filename)

print(f"Generated complete template repository and archive at {zip_path}")
