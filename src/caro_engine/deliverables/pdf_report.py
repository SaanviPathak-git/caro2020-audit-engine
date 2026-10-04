"""
Automated Statutory Audit Deliverable: Regulatory PDF Report Generator
"""

from pathlib import Path
from typing import List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from ..core.models import ClauseResult, ClauseStatus, ClientMetadata

def generate_caro_pdf_report(
    output_path: Path,
    metadata: ClientMetadata,
    clause_results: List[ClauseResult]
) -> Path:
    """Generates an official PDF report of the CARO 2020 Statutory Audit Deliverable."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1B365D')
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1B365D')
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1F2937')
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#4B5563')
    )

    elements = []

    # Title block
    elements.append(Paragraph("INDEPENDENT AUDITOR'S REPORT: ANNEXURE ON CARO 2020", title_style))
    elements.append(Paragraph(f"Statutory Audit Annexure under Section 143(11) of the Companies Act, 2013", meta_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1B365D'), spaceBefore=2, spaceAfter=8))

    # Client Meta Table
    meta_data = [
        [Paragraph(f"<b>Client:</b> {metadata.company_name}", body_style), Paragraph(f"<b>CIN:</b> {metadata.cin}", body_style)],
        [Paragraph(f"<b>Financial Year:</b> {metadata.financial_year}", body_style), Paragraph(f"<b>Audit Date:</b> {metadata.audit_period_end}", body_style)],
        [Paragraph(f"<b>Audit Firm:</b> {metadata.firm_name}", body_style), Paragraph(f"<b>Lead Partner:</b> {metadata.lead_partner}", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F3F4F6')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # Clause results loop
    for res in clause_results:
        status_color = "#166534" if res.status == ClauseStatus.CLEAN else (
            "#991B1B" if res.status == ClauseStatus.QUALIFIED else "#854D0E"
        )
        status_text = f"<font color='{status_color}'><b>[{res.status.value}]</b></font>"
        
        elements.append(Paragraph(f"Clause 3({res.clause_num}){res.clause_sub}: {res.title}  {status_text}", h2_style))
        elements.append(Spacer(1, 3))
        
        # Clean up text for PDF flow
        cleaned_text = res.icai_report_text.replace("\n", "<br/>")
        elements.append(Paragraph(cleaned_text, body_style))
        elements.append(Spacer(1, 6))

        # Add table if present
        if res.disclosure_table_headers and res.disclosure_table_rows:
            # Take at most top 5 rows for concise PDF
            display_rows = res.disclosure_table_rows[:5]
            tbl_data = [[Paragraph(f"<b>{h}</b>", meta_style) for h in res.disclosure_table_headers]]
            for r in display_rows:
                tbl_data.append([Paragraph(str(cell), meta_style) for cell in r])
            
            # Auto-calculate col widths
            col_w = 540 / len(res.disclosure_table_headers)
            t = Table(tbl_data, colWidths=[col_w]*len(res.disclosure_table_headers))
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1B365D')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 6))

        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E5E7EB'), spaceBefore=4, spaceAfter=8))

    doc.build(elements)
    return output_path
