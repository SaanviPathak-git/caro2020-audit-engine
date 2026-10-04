"""
CARO 2020 Statutory Audit Engine - Interactive Web Application
Built with Streamlit for Audit Engagement Teams at Big 4 & Top CA Firms.
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Add parent path so imports work
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from caro_engine.core.engine import CaroAuditEngine
from caro_engine.core.models import ClauseStatus
from caro_engine.deliverables.excel_workpaper import generate_excel_workpaper
from caro_engine.deliverables.draft_caro_report import generate_draft_caro_report_markdown, save_draft_caro_report
from caro_engine.deliverables.pdf_report import generate_caro_pdf_report
from caro_engine.core.tickmarks import TICKMARK_LEGEND

st.set_page_config(
    page_title="CARO 2020 Statutory Audit Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1B365D;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 18px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .status-badge-clean {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
    }
    .status-badge-qualified {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
    }
    .status-badge-obs {
        background-color: #FEF9C3;
        color: #854D0E;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
    }
    .tickmark-box {
        background: #F1F5F9;
        border-left: 3px solid #1B365D;
        padding: 8px 12px;
        margin: 4px 0px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Institute_of_Chartered_Accountants_of_India_logo.svg/300px-Institute_of_Chartered_Accountants_of_India_logo.svg.png", width=70)
st.sidebar.markdown("### 🏛️ Audit Engagement Setup")

sample_dir = current_dir.parent / "data" / "sample_clients"
client_options = {
    "Tata Motors Limited (FY 2023-24) - Real Listed Entity": sample_dir / "tata_motors_fy24",
    "Zenith Infra & Power Ltd (FY 2023-24) - Stressed / Qualifications": sample_dir / "zenith_infra_fy24"
}

selected_client_label = st.sidebar.selectbox("Select Audit Client", list(client_options.keys()))
client_path = client_options[selected_client_label]

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ SA 320 Materiality Parameters")
custom_om_pct = st.sidebar.slider("Overall Materiality (% of Turnover)", 0.25, 2.0, 0.5, 0.05)
custom_pm_pct = st.sidebar.slider("Performance Materiality (% of OM)", 50, 85, 75, 5)
custom_ctt_pct = st.sidebar.slider("Clearly Trivial Threshold (% of OM)", 1, 10, 5, 1)

# Initialize Engine
@st.cache_data(show_spinner=False)
def run_cached_audit(c_path_str: str, om_p: float, pm_p: float, ctt_p: float):
    eng = CaroAuditEngine(Path(c_path_str))
    data = eng.load_data()
    # Apply user overrides if present
    if data["metadata"].materiality:
        data["metadata"].materiality.overall_materiality_pct = om_p
        data["metadata"].materiality.performance_materiality_pct = pm_p
        data["metadata"].materiality.clearly_trivial_pct = ctt_p
        data["metadata"].materiality.calculate()
    res_summary = eng.run_audit()
    return eng, res_summary

engine, summary = run_cached_audit(str(client_path), custom_om_pct, custom_pm_pct, custom_ctt_pct)
meta = summary.metadata
mat = meta.materiality

# -------------------------------------------------------------
# HEADER & MATERIALITY BANNER
# -------------------------------------------------------------
st.markdown("<div class='main-title'>CARO 2020 Statutory Audit Testing Engine</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>Automated Substantive Audit Testing across all 21 Clauses | Client: <b>{meta.company_name}</b> (CIN: {meta.cin}) | FY: <b>{meta.financial_year}</b></div>", unsafe_allow_html=True)

# Top Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Clauses", f"{summary.total_clauses}")
with col2:
    st.metric("Clean Clauses", f"{summary.clean_count}", delta="Unmodified")
with col3:
    st.metric("Observations", f"{summary.observation_count}", delta="Procedural", delta_color="off")
with col4:
    st.metric("Qualified / Adverse", f"{summary.qualified_count}", delta=f"{summary.total_exceptions} Exceptions", delta_color="inverse")
with col5:
    st.metric("Quantified Exposure", f"₹{summary.total_quantified_exposure_cr:,.2f} Cr", delta="Statutory Arrears/Breaches", delta_color="inverse")

st.markdown("---")

# -------------------------------------------------------------
# NAVIGATION TABS
# -------------------------------------------------------------
tab_matrix, tab_inspector, tab_deliverables, tab_interview = st.tabs([
    "📊 CARO Clause Matrix (21 Clauses)",
    "🔍 Clause Deep-Dive & Substantive Tests",
    "📥 Regulatory Deliverables (Excel / Report / PDF)",
    "🎓 Statutory Audit Interview Masterclass"
])

# -------------------------------------------------------------
# TAB 1: CLAUSE MATRIX
# -------------------------------------------------------------
with tab_matrix:
    st.markdown("### 📋 Executive CARO 2020 Compliance Matrix")
    st.write(
        "Each clause is independently tested against statutory thresholds, general ledger records, and external bank/government confirmations. "
        "Audit status follows ICAI Guidance Note rules."
    )
    
    matrix_records = []
    for r in summary.clause_results:
        status_str = "CLEAN" if r.status == ClauseStatus.CLEAN else (
            "QUALIFIED" if r.status == ClauseStatus.QUALIFIED else (
                "OBSERVATION" if r.status == ClauseStatus.OBSERVATION else "NOT APPLICABLE"
            )
        )
        matrix_records.append({
            "Clause": f"Clause 3({r.clause_num}){r.clause_sub}",
            "Subject Matter": r.title,
            "Status": status_str,
            "Exceptions Flagged": len(r.exceptions),
            "Tickmarks": " ".join(r.tickmarks_applied),
            "Key Observation": r.observations[0] if r.observations else (r.exceptions[0].headline if r.exceptions else "Tested per ICAI SA")
        })
        
    df_matrix = pd.DataFrame(matrix_records)
    
    # Styled dataframe
    def color_status(val):
        if val == "CLEAN":
            return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
        elif val == "QUALIFIED":
            return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
        elif val == "OBSERVATION":
            return "background-color: #FEF9C3; color: #854D0E; font-weight: bold;"
        return "background-color: #F3F4F6; color: #6B7280;"

    st.dataframe(df_matrix.style.map(color_status, subset=["Status"]), use_container_width=True, height=520)

    # SA 320 Materiality Explainer Card
    with st.expander("📌 View SA 320 Materiality Calculation Details"):
        if mat:
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1:
                st.write(f"**Benchmark:** {mat.benchmark_name}")
                st.write(f"**Benchmark Amount:** ₹{mat.benchmark_amount:,.2f} Cr")
            with c_m2:
                st.write(f"**Overall Materiality (OM) ({mat.overall_materiality_pct}%):** ₹{mat.overall_materiality:,.2f} Cr")
                st.write(f"**Performance Materiality (PM) ({mat.performance_materiality_pct}%):** ₹{mat.performance_materiality:,.2f} Cr")
            with c_m3:
                st.write(f"**Clearly Trivial Threshold (CTT) ({mat.clearly_trivial_pct}%):** ₹{mat.clearly_trivial_threshold:,.2f} Cr")
                st.write(f"**Auditor Lead Partner:** {meta.lead_partner}")

# -------------------------------------------------------------
# TAB 2: CLAUSE DEEP-DIVE INSPECTOR
# -------------------------------------------------------------
with tab_inspector:
    st.markdown("### 🔍 Substantive Audit Inspector & Evidentiary Trail")
    
    clause_choices = [f"Clause 3({r.clause_num}){r.clause_sub}: {r.title}" for r in summary.clause_results]
    selected_clause_str = st.selectbox("Select Clause to Inspect", clause_choices)
    
    sel_res = next(r for r in summary.clause_results if f"Clause 3({r.clause_num}){r.clause_sub}" in selected_clause_str)
    
    # Clause Header Box
    st_c1, st_c2, st_c3 = st.columns([3, 1, 1])
    with st_c1:
        st.subheader(f"{sel_res.title}")
    with st_c2:
        badge_cls = "clean" if sel_res.status == ClauseStatus.CLEAN else (
            "qualified" if sel_res.status == ClauseStatus.QUALIFIED else "obs"
        )
        st.markdown(f"<span class='status-badge-{badge_cls}'>Status: {sel_res.status.value}</span>", unsafe_allow_html=True)
    with st_c3:
        st.markdown(f"**Exceptions:** {len(sel_res.exceptions)}")

    # Procedures & Tickmarks
    col_p, col_t = st.columns([2, 1])
    with col_p:
        st.markdown("##### 🔬 Substantive Procedures Executed (SA 500 / SA 230):")
        for test in sel_res.substantive_tests:
            st.markdown(f"- {test}")
            
    with col_t:
        st.markdown("##### 🏷️ Evidentiary Tickmarks Applied:")
        for tm in sel_res.tickmarks_applied:
            meaning = TICKMARK_LEGEND.get(tm, "Verified")
            st.markdown(f"<div class='tickmark-box'><b>{tm}</b> : {meaning}</div>", unsafe_allow_html=True)

    # Exceptions Display if any
    if sel_res.exceptions:
        st.markdown("---")
        st.markdown("##### 🚨 Audit Exceptions & Regulatory Violations Flagged:")
        for exc in sel_res.exceptions:
            with st.container():
                st.error(
                    f"**[{exc.severity}] {exc.headline}**\n\n"
                    f"{exc.description}\n\n"
                    f"• **Quantified Amount:** ₹{exc.amount_involved:,.2f} Cr | "
                    f"• **Variance:** {f'{exc.variance_pct:.2f}%' if exc.variance_pct else 'N/A'}"
                )

    # Statutory Disclosure Table if present
    if sel_res.disclosure_table_headers and sel_res.disclosure_table_rows:
        st.markdown("---")
        st.markdown("##### 📊 Mandatory Statutory Disclosure Table (ICAI Format):")
        df_tbl = pd.DataFrame(sel_res.disclosure_table_rows, columns=sel_res.disclosure_table_headers)
        st.dataframe(df_tbl, use_container_width=True)

    # ICAI Draft Legal Text
    st.markdown("---")
    st.markdown("##### 📜 Official ICAI Draft Legal Annexure Text:")
    st.info(sel_res.icai_report_text)

# -------------------------------------------------------------
# TAB 3: REGULATORY DELIVERABLES
# -------------------------------------------------------------
with tab_deliverables:
    st.markdown("### 📥 Regulatory Audit Deliverables Center")
    st.write("Generate and download audit deliverables required for engagement file completion and NFRA inspections.")

    deliv_dir = client_path / "deliverables"
    deliv_dir.mkdir(parents=True, exist_ok=True)
    
    excel_file = deliv_dir / f"{meta.company_name.replace(' ', '_')}_CARO_2020_Workpaper.xlsx"
    md_file = deliv_dir / f"{meta.company_name.replace(' ', '_')}_Draft_CARO_Report.md"
    pdf_file = deliv_dir / f"{meta.company_name.replace(' ', '_')}_CARO_2020_Report.pdf"

    # Ensure generated
    generate_excel_workpaper(excel_file, meta, summary.clause_results)
    save_draft_caro_report(md_file, meta, summary.clause_results)
    generate_caro_pdf_report(pdf_file, meta, summary.clause_results)

    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        st.markdown("#### 📗 Excel Workpaper")
        st.write("Multi-tab audit workpaper complete with SA 320 materiality, tickmark legends, testing matrices, and audit sign-off blocks.")
        with open(excel_file, "rb") as f:
            st.download_button(
                label="⬇️ Download Excel Workpaper (.xlsx)",
                data=f.read(),
                file_name=excel_file.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_excel"
            )

    with col_d2:
        st.markdown("#### 📄 Draft CARO Report")
        st.write("Final legal annexure to Independent Auditor's Report drafted in official ICAI Guidance Note wording with all statutory tables.")
        with open(md_file, "r", encoding="utf-8") as f:
            st.download_button(
                label="⬇️ Download Draft Report (.md)",
                data=f.read(),
                file_name=md_file.name,
                mime="text/markdown",
                key="btn_md"
            )

    with col_d3:
        st.markdown("#### 📑 Official PDF Report")
        st.write("Printable PDF annexure suitable for submission to Audit Committee and Board of Directors.")
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF Report (.pdf)",
                data=f.read(),
                file_name=pdf_file.name,
                mime="application/pdf",
                key="btn_pdf"
            )

    st.markdown("---")
    st.markdown("#### 👁️ Report Preview:")
    with open(md_file, "r", encoding="utf-8") as f:
        st.markdown(f.read())

# -------------------------------------------------------------
# TAB 4: INTERVIEW MASTERCLASS
# -------------------------------------------------------------
with tab_interview:
    st.markdown("### 🎓 Big 4 Statutory Audit Interview Masterclass: CARO 2020")
    st.write(
        "Everything you need to master statutory audit, CARO 2020, NFRA regulatory inspections, "
        "and technical technical interview rounds at PwC, Deloitte, EY, KPMG, BDO, and Grant Thornton."
    )
    
    qa_items = [
        {
            "q": "1. What is CARO 2020, which section governs it, and who is exempt?",
            "a": """**Statutory Provision:** Section 143(11) of the Companies Act, 2013. Notified by the MCA on February 25, 2020. Applicable from FY 2021-22 onwards.
**Applicability:** Applies to every company including foreign companies, EXCEPT:
1. Banking companies (Banking Regulation Act, 1949)
2. Insurance companies (Insurance Act, 1938)
3. Section 8 companies (non-profit entities)
4. One Person Companies (OPCs) and Small Companies (Section 2(85))
5. Private limited companies that meet ALL three criteria:
   - Paid up share capital + Reserves & Surplus <= ₹1 Crore
   - Total borrowings from banks/FIs <= ₹1 Crore at ANY point during the FY
   - Total revenue (including other income) <= ₹10 Crore."""
        },
        {
            "q": "2. Explain Clause (ii)(b): Working capital bank statements vs books reconciliation.",
            "a": """**Statutory Threshold:** Sanctioned working capital limits exceeding **₹5 Crore** in aggregate from banks or FIs on the basis of security of current assets.
**Testing Procedure:**
1. Obtain sanction letters and compute aggregate limits.
2. Obtain quarterly statements/returns (stock statements, book debt statements, QIS returns) submitted to banks.
3. Compare line items against the internal books of account / trial balance as of that quarter-end.
4. Calculate differences and reasons (e.g. inventory valuation standard cost vs actual FIFO, goods-in-transit timing, ECL provisions).
5. **Mandatory ICAI Disclosure Table:** Quarter, Bank Name, Securities provided, Amount per books, Amount per bank return, Difference, Reason."""
        },
        {
            "q": "3. How is Cash Loss recalculated under Clause (xvii)?",
            "a": """**Statutory Rule:** Whether the company incurred cash losses in the financial year and immediately preceding financial year.
**Recalculation Formula (ICAI Guidance Note Para 17):**
`Cash Profit / (Loss) = Operating / Net Profit (Loss) Before Tax + Depreciation + Amortization + Asset Impairment + Non-cash FX - Unrealized Gains`
If the adjusted figure is negative, a Cash Loss exists and MUST be disclosed for current and preceding FY!"""
        },
        {
            "q": "4. What does NFRA check during audit inspections regarding SA 230 and CARO?",
            "a": """**NFRA Inspection Focus Areas:**
1. **SA 230 (Audit Documentation):** Can an experienced auditor having no previous connection with the audit understand the nature, timing, extent of procedures, evidence obtained, and conclusions reached?
2. **Mathematical Proofs:** Did the audit team independently verify mathematical casts, revaluations > 10%, aging of tax dues, and bank reconciliations, or merely accept management checklists?
3. **Tickmarks & Audit Trail:** Are workpapers annotated with standardized tickmarks tied to underlying vouchers?"""
        },
        {
            "q": "5. What are the key checks under Clause (xix) regarding Going Concern?",
            "a": """**Statutory Requirement:** Auditor's opinion whether material uncertainty exists regarding capability to meet liabilities existing at balance sheet date falling due within 1 year.
**Auditor's Evidence Base:**
1. **10 Schedule III Financial Ratios:** Current Ratio, Debt-Equity, DSCR, ROE, Inventory Turnover, Debtors Turnover, Payables Turnover, Working Capital Turnover, Net Profit Margin, ROCE.
2. **1-Year Asset-Liability Maturity Gap:** Liquid financial assets realizable within 12 months vs maturing liabilities.
3. **Undrawn Credit Lines:** Available headroom under sanctioned consortium facilities.
4. **Management Plans:** Forecasted operating cash flows evaluated per SA 570."""
        }
    ]
    
    for item in qa_items:
        with st.expander(f"💡 {item['q']}"):
            st.markdown(item["a"])
