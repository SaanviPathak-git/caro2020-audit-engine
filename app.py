"""
CARO 2020 Statutory Audit Engine - Interactive Web Application
Built with Streamlit for Audit Engagement Teams at Big 4 & Top CA Firms.
"""

import sys
import os
import re
import json
import uuid
import shutil
import zipfile
import html
from pathlib import Path
import pandas as pd
import streamlit as st

# Configure Root and Source Paths
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from caro_engine.core.engine import CaroAuditEngine
from caro_engine.core.models import ClauseStatus
from caro_engine.deliverables.excel_workpaper import generate_excel_workpaper
from caro_engine.deliverables.draft_caro_report import save_draft_caro_report
from caro_engine.deliverables.pdf_report import generate_caro_pdf_report
from caro_engine.core.tickmarks import TICKMARK_LEGEND

st.set_page_config(
    page_title="CARO 2020 Statutory Audit Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Professional audit workstation theme)
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1B365D;
        margin-bottom: 2px;
    }
    .status-badge-clean {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
    }
    .status-badge-qualified {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
    }
    .status-badge-obs {
        background-color: #FEF9C3;
        color: #854D0E;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
    }
    .tickmark-box {
        background: #F1F5F9;
        border-left: 3px solid #1B365D;
        padding: 8px 12px;
        margin: 4px 0px;
        font-size: 0.9rem;
    }
    .upload-card {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 18px 24px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
st.sidebar.markdown("## 🏛️ Audit Engagement Setup")

SAMPLE_DIR = ROOT_DIR / "data" / "sample_clients"
TEMPLATES_DIR = ROOT_DIR / "data" / "templates"
CUSTOM_RUNS_DIR = ROOT_DIR / "data" / "custom_runs"
CUSTOM_RUNS_DIR.mkdir(parents=True, exist_ok=True)

engagement_mode = st.sidebar.radio(
    "Select Engagement Mode",
    ["🏢 Preloaded Listed Companies (Samples)", "📤 Upload Custom Company Data"],
    index=0
)

if engagement_mode == "🏢 Preloaded Listed Companies (Samples)":
    client_options = {
        "Tata Motors Limited (FY 2023-24) - Real Listed Entity": SAMPLE_DIR / "tata_motors_fy24",
        "Zenith Infra & Power Ltd (FY 2023-24) - Stressed / Qualifications": SAMPLE_DIR / "zenith_infra_fy24"
    }
    selected_client_label = st.sidebar.selectbox("Select Audit Client", list(client_options.keys()))
    client_path = client_options[selected_client_label]

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ SA 320 Materiality Parameters")
    custom_om_pct = st.sidebar.slider("Overall Materiality (% of Turnover)", 0.25, 2.0, 0.5, 0.05)
    custom_pm_pct = st.sidebar.slider("Performance Materiality (% of OM)", 50, 85, 75, 5)
    custom_ctt_pct = st.sidebar.slider("Clearly Trivial Threshold (% of OM)", 1, 10, 5, 1)

else:
    # Custom Company Upload Mode
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏢 Custom Company Details")
    custom_co_name = st.sidebar.text_input("Company Name", value="Acme Industries Limited")
    custom_cin = st.sidebar.text_input("Corporate Identity Number (CIN)", value="L17110MH2018PLC305891")
    custom_fy = st.sidebar.text_input("Financial Year", value="2023-24")
    custom_turnover = st.sidebar.number_input("Turnover / Revenue Benchmark (₹ Cr)", min_value=1.0, value=500.0, step=25.0)
    custom_partner = st.sidebar.text_input("Lead Engagement Partner", value="CA Ananya Sharma, FCA")
    custom_firm = st.sidebar.text_input("Audit Firm Name", value="Sharma & Associates LLP, Chartered Accountants")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ SA 320 Materiality Parameters")
    custom_om_pct = st.sidebar.slider("Overall Materiality (% of Turnover)", 0.25, 2.0, 0.5, 0.05)
    custom_pm_pct = st.sidebar.slider("Performance Materiality (% of OM)", 50, 85, 75, 5)
    custom_ctt_pct = st.sidebar.slider("Clearly Trivial Threshold (% of OM)", 1, 10, 5, 1)

    if "custom_session_id" not in st.session_state:
        st.session_state.custom_session_id = uuid.uuid4().hex[:8]

    client_path = CUSTOM_RUNS_DIR / f"session_{st.session_state.custom_session_id}"
    client_path.mkdir(parents=True, exist_ok=True)

    # Initialize client folder with clean baseline files if empty
    if TEMPLATES_DIR.exists():
        for tf in TEMPLATES_DIR.glob("*"):
            if tf.is_file() and not tf.name.endswith(".zip"):
                dest_file = client_path / tf.name
                if not dest_file.exists():
                    shutil.copy(tf, dest_file)

    # Update metadata.json with the user's custom details
    meta_json_path = client_path / "metadata.json"
    meta_data = {}
    if meta_json_path.exists():
        try:
            with open(meta_json_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
        except Exception:
            meta_data = {}

    meta_data["company_name"] = custom_co_name.strip() or "Acme Industries Limited"
    meta_data["cin"] = custom_cin.strip() or "L17110MH2018PLC305891"
    meta_data["financial_year"] = custom_fy.strip() or "2023-24"
    meta_data["lead_partner"] = custom_partner.strip() or "CA Lead Partner"
    meta_data["firm_name"] = custom_firm.strip() or "Chartered Accountants"
    if "materiality" not in meta_data or not isinstance(meta_data["materiality"], dict):
        meta_data["materiality"] = {}
    meta_data["materiality"]["benchmark_name"] = "Turnover / Revenue from Operations"
    meta_data["materiality"]["benchmark_amount"] = float(custom_turnover)
    meta_data["materiality"]["overall_materiality_pct"] = float(custom_om_pct)
    meta_data["materiality"]["performance_materiality_pct"] = float(custom_pm_pct)
    meta_data["materiality"]["clearly_trivial_pct"] = float(custom_ctt_pct)

    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)

# -------------------------------------------------------------
# MAIN VIEW - HEADER & UPLOAD CARD (IF CUSTOM MODE)
# -------------------------------------------------------------
st.markdown("<div class='main-title'>CARO 2020 Statutory Audit Testing Engine</div>", unsafe_allow_html=True)

if engagement_mode == "📤 Upload Custom Company Data":
    st.markdown("""
    <div class='upload-card'>
        <h3 style='margin-top: 0; color: #1B365D;'>📤 Upload Schedules for Custom Company Audit</h3>
        <p style='color: #475569; font-size: 0.95rem; margin-bottom: 8px;'>
            Run substantive audit procedures on any company. Upload your client's CSV schedules (Fixed Asset Register, Bank Statements, Statutory Dues, Borrowings, etc.) or a complete ZIP package.
            <i>Any schedule not uploaded automatically uses compliant baseline values so all 21 clauses test without error.</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_up1, col_up2 = st.columns([1, 2])
    with col_up1:
        st.markdown("##### 📥 Blank CSV & JSON Templates")
        st.caption("Standard schedules formatted to ICAI Guidance Notes:")
        template_zip = TEMPLATES_DIR / "caro_audit_blank_templates.zip"
        if template_zip.exists():
            with open(template_zip, "rb") as f:
                st.download_button(
                    label="⬇️ Download Blank Templates (.zip)",
                    data=f.read(),
                    file_name="caro_audit_blank_templates.zip",
                    mime="application/zip",
                    key="btn_download_templates",
                    help="Contains 11 CSV schedule templates, sample JSONs, and instructions"
                )

    with col_up2:
        st.markdown("##### 📂 Upload Client Schedules")
        uploaded_files = st.file_uploader(
            "Upload CSV / JSON schedules or a ZIP archive",
            type=["csv", "json", "zip"],
            accept_multiple_files=True,
            help="Upload modified CSV schedules (e.g. fixed_asset_register.csv, quarterly_bank_returns.csv, statutory_dues_ledger.csv) or a single .zip file."
        )

        if uploaded_files:
            uploaded_names = []
            for ufile in uploaded_files:
                if ufile.name.endswith(".zip"):
                    with zipfile.ZipFile(ufile) as z:
                        z.extractall(client_path)
                    uploaded_names.append(f"📦 {ufile.name} (extracted)")
                else:
                    dest_file = client_path / ufile.name
                    dest_file.write_bytes(ufile.getbuffer())
                    uploaded_names.append(f"📄 {ufile.name}")
            st.success(f"Loaded {len(uploaded_names)} schedule(s): {', '.join(uploaded_names)}")

# -------------------------------------------------------------
# AUDIT ENGINE EXECUTION
# -------------------------------------------------------------
engine = CaroAuditEngine(client_path)
raw_data = engine.load_data()
if raw_data["metadata"].materiality:
    raw_data["metadata"].materiality.overall_materiality_pct = custom_om_pct
    raw_data["metadata"].materiality.performance_materiality_pct = custom_pm_pct
    raw_data["metadata"].materiality.clearly_trivial_pct = custom_ctt_pct
    raw_data["metadata"].materiality.calculate()

summary = engine.run_audit()
meta = summary.metadata
mat = meta.materiality

safe_co_name = html.escape(meta.company_name)
st.caption(f"Automated Substantive Audit Testing across all 21 Clauses | Client: **{safe_co_name}** (CIN: {meta.cin}) | FY: **{meta.financial_year}**")

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
# NAVIGATION TABS (Executive Matrix, Inspector & Deliverables)
# -------------------------------------------------------------
tab_matrix, tab_inspector, tab_deliverables = st.tabs([
    "📊 CARO Clause Matrix (21 Clauses)",
    "🔍 Clause Deep-Dive & Substantive Tests",
    "📥 Regulatory Deliverables (Excel / Report / PDF)"
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
    
    def color_status(val):
        if val == "CLEAN":
            return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
        elif val == "QUALIFIED":
            return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
        elif val == "OBSERVATION":
            return "background-color: #FEF9C3; color: #854D0E; font-weight: bold;"
        return "background-color: #F3F4F6; color: #6B7280;"

    try:
        styled_df = df_matrix.style.map(color_status, subset=["Status"])
        st.dataframe(styled_df, use_container_width=True, height=520)
    except Exception:
        st.dataframe(df_matrix, use_container_width=True, height=520)

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
    
    clean_name = re.sub(r'[^\w\-_]', '_', meta.company_name)
    excel_file = deliv_dir / f"{clean_name}_CARO_2020_Workpaper.xlsx"
    md_file = deliv_dir / f"{clean_name}_Draft_CARO_Report.md"
    pdf_file = deliv_dir / f"{clean_name}_CARO_2020_Report.pdf"

    # Safely generate deliverables
    try:
        generate_excel_workpaper(excel_file, meta, summary.clause_results)
        save_draft_caro_report(md_file, meta, summary.clause_results)
        generate_caro_pdf_report(pdf_file, meta, summary.clause_results)
    except Exception as e:
        st.warning(f"Note on deliverable generation: {e}")

    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        st.markdown("#### 📗 Excel Workpaper")
        st.write("Multi-tab audit workpaper complete with SA 320 materiality, tickmark legends, testing matrices, and audit sign-off blocks.")
        if excel_file.exists():
            with open(excel_file, "rb") as f:
                st.download_button(
                    label="⬇️ Download Excel Workpaper (.xlsx)",
                    data=f.read(),
                    file_name=excel_file.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"btn_excel_{clean_name}"
                )

    with col_d2:
        st.markdown("#### 📄 Draft CARO Report")
        st.write("Final legal annexure to Independent Auditor's Report drafted in official ICAI Guidance Note wording with all statutory tables.")
        if md_file.exists():
            with open(md_file, "r", encoding="utf-8") as f:
                st.download_button(
                    label="⬇️ Download Draft Report (.md)",
                    data=f.read(),
                    file_name=md_file.name,
                    mime="text/markdown",
                    key=f"btn_md_{clean_name}"
                )

    with col_d3:
        st.markdown("#### 📑 Official PDF Report")
        st.write("Printable PDF annexure suitable for submission to Audit Committee and Board of Directors.")
        if pdf_file.exists():
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF Report (.pdf)",
                    data=f.read(),
                    file_name=pdf_file.name,
                    mime="application/pdf",
                    key=f"btn_pdf_{clean_name}"
                )

    st.markdown("---")
    st.markdown("#### 👁️ Draft Report Preview:")
    if md_file.exists():
        with open(md_file, "r", encoding="utf-8") as f:
            st.code(f.read(), language="markdown")
