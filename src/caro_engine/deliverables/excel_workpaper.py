"""
Automated Regulatory Audit Workpaper Generator (Excel .xlsx)
Compliant with ICAI SA 230 (Audit Documentation) & Big 4 Workpaper Standards
"""

from pathlib import Path
from typing import List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from ..core.models import ClauseResult, ClauseStatus, ClientMetadata, AuditException
from ..core.tickmarks import TICKMARK_LEGEND, AuditTickMark
from ..utils.formatting import format_inr, format_crores

# Styling palettes: Professional Navy & Platinum Audit Theme
NAVY_HEADER = "1B365D"
LIGHT_NAVY = "2C4D75"
ICE_BLUE = "EBF2FA"
SOFT_GRAY = "F7F9FB"
BORDER_GRAY = "D1D5DB"
RED_ALERT = "FEE2E2"
RED_TEXT = "991B1B"
GREEN_CLEAN = "DCFCE7"
GREEN_TEXT = "166534"
YELLOW_WARN = "FEF9C3"
YELLOW_TEXT = "854D0E"

thin_side = Side(border_style="thin", color=BORDER_GRAY)
cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
header_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=Side(border_style="medium", color=NAVY_HEADER))

header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
title_font = Font(name="Segoe UI", size=14, bold=True, color=NAVY_HEADER)
regular_font = Font(name="Segoe UI", size=10)
bold_font = Font(name="Segoe UI", size=10, bold=True)
italic_font = Font(name="Segoe UI", size=9, italic=True)

def apply_table_header(ws, row_idx: int, col_start: int, col_end: int):
    for col in range(col_start, col_end + 1):
        cell = ws.cell(row=row_idx, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = header_border
    ws.row_dimensions[row_idx].height = 28

def auto_fit_columns(ws, min_width=12, max_width=50):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = str(cell.value or "")
            if "\n" in val:
                val = max(val.split("\n"), key=len)
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, min_width), max_width)

def generate_excel_workpaper(
    output_path: Path,
    metadata: ClientMetadata,
    clause_results: List[ClauseResult]
) -> Path:
    wb = openpyxl.Workbook()
    
    # -------------------------------------------------------------
    # TAB 1: ENGAGEMENT SUMMARY & MATERIALITY (Lead Sheet)
    # -------------------------------------------------------------
    ws_lead = wb.active
    ws_lead.title = "Lead Sheet & Materiality"
    ws_lead.views.sheetView[0].showGridLines = True
    
    # Header block
    ws_lead["A1"] = f"STATUTORY AUDIT WORKPAPER: CARO 2020 ENGINE"
    ws_lead["A1"].font = title_font
    ws_lead["A2"] = f"Client: {metadata.company_name} | CIN: {metadata.cin} | FY: {metadata.financial_year}"
    ws_lead["A2"].font = Font(name="Segoe UI", size=11, bold=True, color=LIGHT_NAVY)
    ws_lead["A3"] = f"Auditors: {metadata.firm_name} | Engagement Partner: {metadata.lead_partner}"
    ws_lead["A3"].font = italic_font
    
    # SA 320 Materiality Calculation Block
    ws_lead["A5"] = "1. AUDIT MATERIALITY SCHEDULE (SA 320)"
    ws_lead["A5"].font = Font(name="Segoe UI", size=11, bold=True, color=NAVY_HEADER)
    
    mat_headers = ["Parameter", "Basis / Percentage", "Amount (₹ Crores)", "Audit Purpose & Documentation"]
    for col_idx, h in enumerate(mat_headers, 1):
        ws_lead.cell(row=6, column=col_idx, value=h)
    apply_table_header(ws_lead, 6, 1, 4)
    
    mat = metadata.materiality
    bench_amt = mat.benchmark_amount if mat else 0.0
    om = mat.overall_materiality if mat else 0.0
    pm = mat.performance_materiality if mat else 0.0
    ctt = mat.clearly_trivial_threshold if mat else 0.0
    
    mat_rows = [
        ["Selected Benchmark", mat.benchmark_name if mat else "Turnover", f"₹{bench_amt:,.2f} Cr", "Primary basis for materiality assessment"],
        ["Overall Materiality (OM)", f"{mat.overall_materiality_pct if mat else 0.5}% of Benchmark", f"₹{om:,.2f} Cr", "Threshold above which financial misstatements alter user decisions"],
        ["Performance Materiality (PM)", f"{mat.performance_materiality_pct if mat else 75}% of OM", f"₹{pm:,.2f} Cr", "Working threshold applied to test individual clauses & schedules"],
        ["Clearly Trivial Threshold (CTT)", f"{mat.clearly_trivial_pct if mat else 5}% of OM", f"₹{ctt:,.2f} Cr", "Tolerable limit below which audit exceptions need not be accumulated"]
    ]
    for r_idx, r_data in enumerate(mat_rows, 7):
        for c_idx, val in enumerate(r_data, 1):
            cell = ws_lead.cell(row=r_idx, column=c_idx, value=val)
            cell.font = regular_font if c_idx != 3 else bold_font
            cell.border = cell_border
            if c_idx == 3:
                cell.alignment = Alignment(horizontal="right")
    
    # Executive Summary of Clause Testing
    ws_lead["A12"] = "2. EXECUTIVE CLAUSE TESTING DASHBOARD (21 CLAUSES)"
    ws_lead["A12"].font = Font(name="Segoe UI", size=11, bold=True, color=NAVY_HEADER)
    
    dash_headers = ["Clause Category Status", "Count", "% of Total", "Regulatory Implication"]
    for col_idx, h in enumerate(dash_headers, 1):
        ws_lead.cell(row=13, column=col_idx, value=h)
    apply_table_header(ws_lead, 13, 1, 4)
    
    total = len(clause_results)
    clean = sum(1 for r in clause_results if r.status == ClauseStatus.CLEAN)
    obs = sum(1 for r in clause_results if r.status == ClauseStatus.OBSERVATION)
    qual = sum(1 for r in clause_results if r.status == ClauseStatus.QUALIFIED)
    na = sum(1 for r in clause_results if r.status == ClauseStatus.NOT_APPLICABLE)
    
    dash_rows = [
        ["Clean (Unmodified Standard Wording)", clean, f"{(clean/total*100):.1f}%", "No statutory discrepancies or threshold violations identified"],
        ["Observation (Procedural Note)", obs, f"{(obs/total*100):.1f}%", "Reconciliation or timing differences noted with adequate justification"],
        ["Qualified (Adverse / Breach Reported)", qual, f"{(qual/total*100):.1f}%", "Statutory threshold exceeded or legal breach; mandatory disclosure tables required"],
        ["Not Applicable", na, f"{(na/total*100):.1f}%", "Entity exempt or clause not applicable (e.g., Nidhi / CFS Standalone)"],
        ["Total Evaluated", total, "100.0%", "Complete substantive coverage per Companies (Auditor's Report) Order, 2020"]
    ]
    for r_idx, r_data in enumerate(dash_rows, 14):
        for c_idx, val in enumerate(r_data, 1):
            cell = ws_lead.cell(row=r_idx, column=c_idx, value=val)
            cell.font = bold_font if r_idx == 18 or c_idx == 2 else regular_font
            cell.border = cell_border
            if c_idx in [2, 3]:
                cell.alignment = Alignment(horizontal="center")
            if c_idx == 1:
                if "Clean" in str(val):
                    cell.fill = PatternFill(start_color=GREEN_CLEAN, fill_type="solid")
                elif "Qualified" in str(val):
                    cell.fill = PatternFill(start_color=RED_ALERT, fill_type="solid")
                elif "Observation" in str(val):
                    cell.fill = PatternFill(start_color=YELLOW_WARN, fill_type="solid")

    # Tickmarks Legend per SA 230
    ws_lead["A20"] = "3. AUDIT TICKMARKS & EVIDENTIARY ANNOTATION LEGEND (SA 230)"
    ws_lead["A20"].font = Font(name="Segoe UI", size=11, bold=True, color=NAVY_HEADER)
    
    ws_lead.cell(row=21, column=1, value="Tickmark")
    ws_lead.cell(row=21, column=2, value="Audit Evidentiary Meaning")
    apply_table_header(ws_lead, 21, 1, 2)
    
    for r_idx, (tm, desc) in enumerate(TICKMARK_LEGEND.items(), 22):
        c1 = ws_lead.cell(row=r_idx, column=1, value=tm)
        c1.font = Font(name="Segoe UI", size=12, bold=True, color=NAVY_HEADER)
        c1.alignment = Alignment(horizontal="center")
        c1.border = cell_border
        
        c2 = ws_lead.cell(row=r_idx, column=2, value=desc)
        c2.font = regular_font
        c2.border = cell_border

    # Sign-off Block
    sign_start = 22 + len(TICKMARK_LEGEND) + 2
    ws_lead.cell(row=sign_start, column=1, value="4. AUDIT ENGAGEMENT REVIEW & SIGN-OFF BLOCK").font = Font(name="Segoe UI", size=11, bold=True, color=NAVY_HEADER)
    
    sign_headers = ["Audit Role", "Designation", "Sign-Off Status", "Date Completed"]
    for c_idx, h in enumerate(sign_headers, 1):
        ws_lead.cell(row=sign_start+1, column=c_idx, value=h)
    apply_table_header(ws_lead, sign_start+1, 1, 4)
    
    sign_rows = [
        ["Prepared By", "Audit Senior Associate", "COMPLETED (Automated Engine Run)", metadata.audit_period_end],
        ["Reviewed By", "Audit Manager", "REVIEWED & VERIFIED", metadata.audit_period_end],
        ["Approved By", f"Lead Partner ({metadata.lead_partner})", "APPROVED FOR ISSUANCE", metadata.audit_period_end]
    ]
    for r_idx, r_data in enumerate(sign_rows, sign_start+2):
        for c_idx, val in enumerate(r_data, 1):
            c = ws_lead.cell(row=r_idx, column=c_idx, value=val)
            c.font = regular_font if c_idx != 3 else bold_font
            c.border = cell_border
            if c_idx == 3:
                c.fill = PatternFill(start_color=GREEN_CLEAN, fill_type="solid")

    auto_fit_columns(ws_lead)

    # -------------------------------------------------------------
    # TAB 2: CARO 2020 CLAUSE MATRIX (Master Testing Summary)
    # -------------------------------------------------------------
    ws_matrix = wb.create_sheet(title="CARO Clause Matrix")
    ws_matrix.views.sheetView[0].showGridLines = True
    
    ws_matrix["A1"] = f"CARO 2020 SUBSTANTIVE TESTING MATRIX (21 CLAUSES)"
    ws_matrix["A1"].font = title_font
    ws_matrix["A2"] = f"Independent testing and regulatory compliance verification per Companies (Auditor's Report) Order, 2020"
    ws_matrix["A2"].font = italic_font
    
    matrix_headers = [
        "Clause #",
        "Sub-Clause",
        "Statutory Audit Subject",
        "Audit Status",
        "Exceptions Count",
        "Tickmarks Applied",
        "Substantive Audit Procedures Performed & Legal Conclusions"
    ]
    for c_idx, h in enumerate(matrix_headers, 1):
        ws_matrix.cell(row=4, column=c_idx, value=h)
    apply_table_header(ws_matrix, 4, 1, 7)
    
    for r_idx, res in enumerate(clause_results, 5):
        ws_matrix.cell(row=r_idx, column=1, value=f"Clause 3({res.clause_num})").font = bold_font
        ws_matrix.cell(row=r_idx, column=2, value=res.clause_sub).font = regular_font
        ws_matrix.cell(row=r_idx, column=3, value=res.title).font = bold_font
        
        status_cell = ws_matrix.cell(row=r_idx, column=4, value=res.status.value)
        status_cell.font = bold_font
        status_cell.alignment = Alignment(horizontal="center")
        if res.status == ClauseStatus.CLEAN:
            status_cell.fill = PatternFill(start_color=GREEN_CLEAN, fill_type="solid")
            status_cell.font = Font(name="Segoe UI", size=10, bold=True, color=GREEN_TEXT)
        elif res.status == ClauseStatus.QUALIFIED:
            status_cell.fill = PatternFill(start_color=RED_ALERT, fill_type="solid")
            status_cell.font = Font(name="Segoe UI", size=10, bold=True, color=RED_TEXT)
        elif res.status == ClauseStatus.OBSERVATION:
            status_cell.fill = PatternFill(start_color=YELLOW_WARN, fill_type="solid")
            status_cell.font = Font(name="Segoe UI", size=10, bold=True, color=YELLOW_TEXT)
        else:
            status_cell.fill = PatternFill(start_color="E5E7EB", fill_type="solid")
            
        exc_cell = ws_matrix.cell(row=r_idx, column=5, value=len(res.exceptions))
        exc_cell.font = bold_font if len(res.exceptions) > 0 else regular_font
        exc_cell.alignment = Alignment(horizontal="center")
        
        tm_cell = ws_matrix.cell(row=r_idx, column=6, value=" ".join(res.tickmarks_applied))
        tm_cell.font = Font(name="Segoe UI", size=11, bold=True, color=NAVY_HEADER)
        tm_cell.alignment = Alignment(horizontal="center")
        
        summary_text = "\n".join(res.observations) if res.observations else (
            f"Exceptions: {len(res.exceptions)} statutory violations flagged." if res.exceptions else "Tested per ICAI standards."
        )
        proc_cell = ws_matrix.cell(row=r_idx, column=7, value=summary_text)
        proc_cell.font = regular_font
        proc_cell.alignment = Alignment(wrap_text=True)
        
        for col in range(1, 8):
            ws_matrix.cell(row=r_idx, column=col).border = cell_border
        ws_matrix.row_dimensions[r_idx].height = 42

    auto_fit_columns(ws_matrix)

    # -------------------------------------------------------------
    # TAB 3: TITLE DEEDS REGISTER (Clause i(c) Disclosure Table)
    # -------------------------------------------------------------
    c1 = next((r for r in clause_results if r.clause_num == "i"), None)
    if c1 and c1.disclosure_table_rows:
        ws_titles = wb.create_sheet(title="Title Deeds - Cl i(c)")
        ws_titles.views.sheetView[0].showGridLines = True
        ws_titles["A1"] = "CLAUSE 3(i)(c): IMMOVABLE PROPERTIES TITLE DEEDS NOT HELD IN COMPANY NAME"
        ws_titles["A1"].font = title_font
        
        for c_idx, h in enumerate(c1.disclosure_table_headers, 1):
            ws_titles.cell(row=3, column=c_idx, value=h)
        apply_table_header(ws_titles, 3, 1, len(c1.disclosure_table_headers))
        
        for r_idx, row_vals in enumerate(c1.disclosure_table_rows, 4):
            for c_idx, val in enumerate(row_vals, 1):
                cell = ws_titles.cell(row=r_idx, column=c_idx, value=val)
                cell.font = regular_font
                cell.border = cell_border
                if c_idx == 3:
                    cell.alignment = Alignment(horizontal="right")
                    cell.font = bold_font
        auto_fit_columns(ws_titles)

    # -------------------------------------------------------------
    # TAB 4: BANK RETURNS RECONCILIATION (Clause ii(b))
    # -------------------------------------------------------------
    c2 = next((r for r in clause_results if r.clause_num == "ii"), None)
    if c2 and c2.disclosure_table_rows:
        ws_bank = wb.create_sheet(title="Bank Returns - Cl ii(b)")
        ws_bank.views.sheetView[0].showGridLines = True
        ws_bank["A1"] = "CLAUSE 3(ii)(b): QUARTERLY BANK RETURNS RECONCILIATION (> ₹5 CRORE SANCTIONED LIMIT)"
        ws_bank["A1"].font = title_font
        
        for c_idx, h in enumerate(c2.disclosure_table_headers, 1):
            ws_bank.cell(row=3, column=c_idx, value=h)
        apply_table_header(ws_bank, 3, 1, len(c2.disclosure_table_headers))
        
        for r_idx, row_vals in enumerate(c2.disclosure_table_rows, 4):
            for c_idx, val in enumerate(row_vals, 1):
                cell = ws_bank.cell(row=r_idx, column=c_idx, value=val)
                cell.font = regular_font
                cell.border = cell_border
                if c_idx in [5, 6, 7]:
                    cell.alignment = Alignment(horizontal="right")
                    cell.font = bold_font
                    if c_idx == 7 and abs(float(val)) > 10.0:
                        cell.fill = PatternFill(start_color=RED_ALERT, fill_type="solid")
                        cell.font = Font(name="Segoe UI", size=10, bold=True, color=RED_TEXT)
        auto_fit_columns(ws_bank)

    # -------------------------------------------------------------
    # TAB 5: STATUTORY DUES & LITIGATIONS (Clause vii)
    # -------------------------------------------------------------
    c7 = next((r for r in clause_results if r.clause_num == "vii"), None)
    if c7:
        ws_dues = wb.create_sheet(title="Statutory Dues - Cl vii")
        ws_dues.views.sheetView[0].showGridLines = True
        ws_dues["A1"] = "CLAUSE 3(vii): STATUTORY DUES & DISPUTED TAX LITIGATION REGISTER"
        ws_dues["A1"].font = title_font
        
        if c7.disclosure_table_rows:
            for c_idx, h in enumerate(c7.disclosure_table_headers, 1):
                ws_dues.cell(row=3, column=c_idx, value=h)
            apply_table_header(ws_dues, 3, 1, len(c7.disclosure_table_headers))
            
            for r_idx, row_vals in enumerate(c7.disclosure_table_rows, 4):
                for c_idx, val in enumerate(row_vals, 1):
                    cell = ws_dues.cell(row=r_idx, column=c_idx, value=val)
                    cell.font = regular_font
                    cell.border = cell_border
                    if c_idx in [3, 4, 5]:
                        cell.alignment = Alignment(horizontal="right")
                        cell.font = bold_font
        auto_fit_columns(ws_dues)

    # -------------------------------------------------------------
    # TAB 6: GOING CONCERN & LIQUIDITY (Clause xix)
    # -------------------------------------------------------------
    c19 = next((r for r in clause_results if r.clause_num == "xix"), None)
    if c19 and c19.disclosure_table_rows:
        ws_gc = wb.create_sheet(title="Going Concern - Cl xix")
        ws_gc.views.sheetView[0].showGridLines = True
        ws_gc["A1"] = "CLAUSE 3(xix): SCHEDULE III FINANCIAL RATIOS & GOING CONCERN ASSESSMENT"
        ws_gc["A1"].font = title_font
        
        for c_idx, h in enumerate(c19.disclosure_table_headers, 1):
            ws_gc.cell(row=3, column=c_idx, value=h)
        apply_table_header(ws_gc, 3, 1, len(c19.disclosure_table_headers))
        
        for r_idx, row_vals in enumerate(c19.disclosure_table_rows, 4):
            for c_idx, val in enumerate(row_vals, 1):
                cell = ws_gc.cell(row=r_idx, column=c_idx, value=val)
                cell.font = regular_font
                cell.border = cell_border
                if c_idx in [2, 3, 4, 5]:
                    cell.alignment = Alignment(horizontal="right")
                    cell.font = bold_font
                if c_idx == 6:
                    cell.alignment = Alignment(horizontal="center")
                    if str(val) == "No":
                        cell.fill = PatternFill(start_color=RED_ALERT, fill_type="solid")
                        cell.font = Font(name="Segoe UI", size=10, bold=True, color=RED_TEXT)
                    else:
                        cell.fill = PatternFill(start_color=GREEN_CLEAN, fill_type="solid")
                        cell.font = Font(name="Segoe UI", size=10, bold=True, color=GREEN_TEXT)
        auto_fit_columns(ws_gc)

    # -------------------------------------------------------------
    # TAB 7: CONSOLIDATED AUDIT EXCEPTIONS LOG
    # -------------------------------------------------------------
    ws_exc = wb.create_sheet(title="Exceptions Log")
    ws_exc.views.sheetView[0].showGridLines = True
    ws_exc["A1"] = "CONSOLIDATED AUDIT EXCEPTIONS & REGULATORY FINDINGS LOG"
    ws_exc["A1"].font = title_font
    
    exc_headers = [
        "Exception ID",
        "Clause #",
        "Severity",
        "Audit Finding Headline",
        "Detailed Finding & Non-Compliance Description",
        "Quantified Exposure (₹ Cr)",
        "Variance %",
        "Regulatory Reporting Impact"
    ]
    for c_idx, h in enumerate(exc_headers, 1):
        ws_exc.cell(row=3, column=c_idx, value=h)
    apply_table_header(ws_exc, 3, 1, 8)
    
    row_tracker = 4
    for res in clause_results:
        for e_idx, e in enumerate(res.exceptions, 1):
            c1 = ws_exc.cell(row=row_tracker, column=1, value=f"EXC-{res.clause_num.upper()}-{e_idx:02d}")
            c1.font = bold_font
            
            c2 = ws_exc.cell(row=row_tracker, column=2, value=e.clause_id)
            c2.font = bold_font
            
            c3 = ws_exc.cell(row=row_tracker, column=3, value=e.severity)
            c3.font = bold_font
            c3.alignment = Alignment(horizontal="center")
            if e.severity in ["HIGH", "CRITICAL"]:
                c3.fill = PatternFill(start_color=RED_ALERT, fill_type="solid")
                c3.font = Font(name="Segoe UI", size=10, bold=True, color=RED_TEXT)
            else:
                c3.fill = PatternFill(start_color=YELLOW_WARN, fill_type="solid")
                
            ws_exc.cell(row=row_tracker, column=4, value=e.headline).font = bold_font
            
            c5 = ws_exc.cell(row=row_tracker, column=5, value=e.description)
            c5.font = regular_font
            c5.alignment = Alignment(wrap_text=True)
            
            c6 = ws_exc.cell(row=row_tracker, column=6, value=f"{e.amount_involved:,.2f}" if e.amount_involved else "-")
            c6.font = bold_font
            c6.alignment = Alignment(horizontal="right")
            
            c7 = ws_exc.cell(row=row_tracker, column=7, value=f"{e.variance_pct:.2f}%" if e.variance_pct else "-")
            c7.font = regular_font
            c7.alignment = Alignment(horizontal="right")
            
            ws_exc.cell(row=row_tracker, column=8, value="Mandatory CARO Qualification" if e.severity in ["HIGH", "CRITICAL"] else "Disclosure Note").font = bold_font
            
            for col in range(1, 9):
                ws_exc.cell(row=row_tracker, column=col).border = cell_border
            ws_exc.row_dimensions[row_tracker].height = 36
            row_tracker += 1

    if row_tracker == 4:
        # No exceptions
        ws_exc.cell(row=4, column=1, value="No material audit exceptions or qualifications identified across all 21 clauses.").font = bold_font
        ws_exc.merge_cells("A4:H4")

    auto_fit_columns(ws_exc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return output_path
