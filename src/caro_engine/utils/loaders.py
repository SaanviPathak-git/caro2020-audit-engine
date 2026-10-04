"""
Client Schedule Loaders & Validation Utilities
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
from ..core.models import ClientMetadata, MaterialityConfig

class ClientDataLoader:
    """Loads and validates client financial schedules for CARO 2020 testing."""
    
    def __init__(self, client_dir: Path):
        self.client_dir = Path(client_dir)
        if not self.client_dir.exists():
            raise FileNotFoundError(f"Client directory not found: {self.client_dir}")

    def load_metadata(self) -> ClientMetadata:
        meta_file = self.client_dir / "metadata.json"
        if not meta_file.exists():
            raise FileNotFoundError(f"metadata.json missing in {self.client_dir}")
        with open(meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        meta = ClientMetadata(**data)
        if meta.materiality:
            meta.materiality.calculate()
        return meta

    def load_csv_schedule(self, filename: str) -> pd.DataFrame:
        csv_file = self.client_dir / filename
        if not csv_file.exists():
            return pd.DataFrame()
        return pd.read_csv(csv_file)

    def load_json_schedule(self, filename: str) -> Dict[str, Any]:
        json_file = self.client_dir / filename
        if not json_file.exists():
            return {}
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_all_client_schedules(self) -> Dict[str, Any]:
        meta = self.load_metadata()
        far_df = self.load_csv_schedule("fixed_asset_register.csv")
        title_deeds_df = self.load_csv_schedule("title_deeds_register.csv")
        inventory_df = self.load_csv_schedule("inventory_physical_verification.csv")
        bank_returns_df = self.load_csv_schedule("quarterly_bank_returns.csv")
        loans_df = self.load_csv_schedule("loans_investments_guarantees.csv")
        statutory_dues_df = self.load_csv_schedule("statutory_dues_ledger.csv")
        litigation_df = self.load_csv_schedule("litigation_register.csv")
        borrowings_df = self.load_csv_schedule("borrowings_default_schedule.csv")
        term_loans_df = self.load_csv_schedule("term_loans_end_use.csv")
        rpt_df = self.load_csv_schedule("related_party_transactions.csv")
        csr_df = self.load_csv_schedule("csr_schedule.csv")
        cash_flow_data = self.load_json_schedule("cash_flow_and_pnl.json")
        ratios_data = self.load_json_schedule("balance_sheet_ratios.json")
        gov_data = self.load_json_schedule("governance_check_responses.json")

        return {
            "metadata": meta,
            "fixed_asset_register": far_df,
            "title_deeds_register": title_deeds_df,
            "inventory_physical_verification": inventory_df,
            "quarterly_bank_returns": bank_returns_df,
            "loans_investments_guarantees": loans_df,
            "statutory_dues_ledger": statutory_dues_df,
            "litigation_register": litigation_df,
            "borrowings_default_schedule": borrowings_df,
            "term_loans_end_use": term_loans_df,
            "related_party_transactions": rpt_df,
            "csr_schedule": csr_df,
            "cash_flow_and_pnl": cash_flow_data,
            "balance_sheet_ratios": ratios_data,
            "governance_check_responses": gov_data,
        }
