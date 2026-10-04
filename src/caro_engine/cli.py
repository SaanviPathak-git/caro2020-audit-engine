"""
CARO 2020 Statutory Audit Engine - Command Line Interface (CLI)
Built with Rich for audit engagement teams at Big 4 & top CA firms.
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from .core.engine import CaroAuditEngine
from .core.models import ClauseStatus
from .deliverables.excel_workpaper import generate_excel_workpaper
from .deliverables.draft_caro_report import save_draft_caro_report
from .deliverables.pdf_report import generate_caro_pdf_report
from .utils.formatting import format_crores

console = Console(force_terminal=True)

BANNER = r"""
   ______ ___     ____   ____     ___   ____ ___   ____ 
  / ____//   |   / __ \ / __ \   |__ \ / __ \__ \ / __ \
 / /    / /| |  / /_/ // / / /   __/ // / / /_/ // / / /
/ /___ / ___ | / _, _// /_/ /   / __// /_/ / __// /_/ / 
\____//_/  |_|/_/ |_| \____/   /____/\____/____/\____/  
   AUTOMATED SUBSTANTIVE AUDIT TESTING ENGINE (ICAI & NFRA)
"""

def print_banner():
    console.print(Panel(Text(BANNER, style="bold cyan"), subtitle="[bold yellow]Big 4 & Statutory Audit Automation[/bold yellow]", box=box.DOUBLE))

def run_audit_command(args):
    print_banner()
    client_path = Path(args.client)
    if not client_path.exists():
        console.print(f"[bold red]Error: Client directory not found: {client_path}[/bold red]")
        sys.exit(1)

    console.print(f"[bold green]>> Initializing Substantive Audit Engine for:[/bold green] [bold white]{client_path.name}[/bold white]")
    engine = CaroAuditEngine(client_path)
    summary = engine.run_audit()
    meta = summary.metadata

    # 1. Print Materiality & Engagement Panel
    mat = meta.materiality
    mat_table = Table(title="SA 320 AUDIT MATERIALITY & ENGAGEMENT METRICS", box=box.ROUNDED)
    mat_table.add_column("Parameter", style="bold cyan")
    mat_table.add_column("Basis / Statutory Percentage", style="white")
    mat_table.add_column("Calculated Amount", style="bold green", justify="right")
    
    if mat:
        mat_table.add_row("Client Name", "Entity under audit", f"{meta.company_name} ({meta.cin})")
        mat_table.add_row("Audit Firm", "Independent Statutory Auditor", f"{meta.firm_name}")
        mat_table.add_row("Materiality Benchmark", mat.benchmark_name, f"Rs. {mat.benchmark_amount:,.2f} Cr")
        mat_table.add_row("Overall Materiality (OM)", f"{mat.overall_materiality_pct}% of Benchmark", f"Rs. {mat.overall_materiality:,.2f} Cr")
        mat_table.add_row("Performance Materiality (PM)", f"{mat.performance_materiality_pct}% of OM", f"Rs. {mat.performance_materiality:,.2f} Cr")
        mat_table.add_row("Clearly Trivial Threshold (CTT)", f"{mat.clearly_trivial_pct}% of OM", f"Rs. {mat.clearly_trivial_threshold:,.2f} Cr")

    console.print(mat_table)
    console.print("")

    # 2. Print Clause Matrix Table
    clause_table = Table(title="CARO 2020 SUBSTANTIVE TESTING RESULTS (21 CLAUSES)", box=box.ROUNDED)
    clause_table.add_column("Clause", style="bold cyan", width=12)
    clause_table.add_column("Audit Subject", style="white", width=42)
    clause_table.add_column("Status", justify="center", width=16)
    clause_table.add_column("Tickmarks", justify="center", width=14)
    clause_table.add_column("Exceptions", justify="right", width=12)

    for r in summary.clause_results:
        if r.status == ClauseStatus.CLEAN:
            status_style = "[bold green]CLEAN[/bold green]"
        elif r.status == ClauseStatus.QUALIFIED:
            status_style = "[bold red]QUALIFIED[/bold red]"
        elif r.status == ClauseStatus.OBSERVATION:
            status_style = "[bold yellow]OBSERVATION[/bold yellow]"
        else:
            status_style = "[dim]N/A[/dim]"

        exc_str = f"[bold red]{len(r.exceptions)}[/bold red]" if r.exceptions else "[green]0[/green]"
        tms = " ".join(r.tickmarks_applied)
        clause_table.add_row(f"3({r.clause_num}){r.clause_sub}", r.title, status_style, tms, exc_str)

    console.print(clause_table)
    console.print("")

    # 3. Print Executive Summary
    summary_panel = Panel(
        f"[bold]Total Clauses Tested:[/bold] {summary.total_clauses}\n"
        f"[bold green]Clean Clauses:[/bold green] {summary.clean_count} | "
        f"[bold yellow]Observations:[/bold yellow] {summary.observation_count} | "
        f"[bold red]Qualified / Adverse Clauses:[/bold red] {summary.qualified_count} | "
        f"[bold dim]Not Applicable:[/bold dim] {summary.na_count}\n"
        f"[bold red]Total Audit Exceptions Flagged:[/bold red] {summary.total_exceptions}\n"
        f"[bold red]Total Quantified Financial Exposure:[/bold red] Rs. {summary.total_quantified_exposure_cr:,.2f} Crores",
        title="[bold yellow]EXECUTIVE AUDIT SUMMARY[/bold yellow]",
        box=box.ROUNDED
    )
    console.print(summary_panel)
    console.print("")

    # 4. Generate Deliverables
    output_dir = Path(args.output) if args.output else client_path / "deliverables"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    excel_path = output_dir / f"{meta.company_name.replace(' ', '_')}_CARO_2020_Workpaper.xlsx"
    md_path = output_dir / f"{meta.company_name.replace(' ', '_')}_Draft_CARO_Report.md"
    pdf_path = output_dir / f"{meta.company_name.replace(' ', '_')}_CARO_2020_Report.pdf"

    console.print("[bold cyan]Generating Regulatory Audit Deliverables...[/bold cyan]")
    generate_excel_workpaper(excel_path, meta, summary.clause_results)
    console.print(f"  [bold green]✓ Excel Regulatory Workpaper (Multi-tab):[/bold green] {excel_path}")

    save_draft_caro_report(md_path, meta, summary.clause_results)
    console.print(f"  [bold green]✓ Draft CARO Report (Legal Annexure):[/bold green] {md_path}")

    generate_caro_pdf_report(pdf_path, meta, summary.clause_results)
    console.print(f"  [bold green]✓ Official PDF Deliverable:[/bold green] {pdf_path}")

    console.print("\n[bold green]>> Substantive Audit Run Completed Successfully![/bold green]\n")

def main():
    parser = argparse.ArgumentParser(description="CARO 2020 Automated Substantive Audit Testing Engine")
    subparsers = parser.add_subparsers(dest="command")

    audit_parser = subparsers.add_parser("audit", help="Run substantive audit tests on a client dataset")
    audit_parser.add_argument("--client", "-c", required=True, help="Path to client data folder (e.g. data/sample_clients/tata_motors_fy24)")
    audit_parser.add_argument("--output", "-o", default=None, help="Directory to save generated deliverables")

    args = parser.parse_args()
    if args.command == "audit":
        run_audit_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
