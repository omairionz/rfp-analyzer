# app.py
# Run with: streamlit run app.py

import streamlit as st
import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from src.parse_rfp import generate_database, get_first_pages_text, get_relevant_text
from src.extract_tier1 import extract_tier1
from src.extract_tier2 import extract_tier2

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="RFP Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
  /* Import fonts */
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  /* Root color variables */
  :root {
    --bg-primary:    #0d1117;
    --bg-secondary:  #161b22;
    --bg-card:       #1c2128;
    --border:        #30363d;
    --amber:         #d4a017;
    --amber-dim:     #9a7310;
    --green:         #3fb950;
    --red:           #f85149;
    --yellow:        #e3b341;
    --text-primary:  #e6edf3;
    --text-secondary:#8b949e;
    --text-mono:     #79c0ff;
  }

  /* Global background */
  .stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: var(--bg-secondary);
    border-right: 1px solid var(--border);
  }

  /* Hide default streamlit header/footer */
  #MainMenu, footer, header { visibility: hidden; }

  /* Main title */
  .rfp-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--amber);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--amber-dim);
    padding-bottom: 0.4rem;
    margin-bottom: 0.2rem;
  }

  /* Subtitle */
  .rfp-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    letter-spacing: 0.04em;
    margin-bottom: 1.5rem;
  }

  /* Section headers */
  .section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--amber);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border-left: 3px solid var(--amber);
    padding-left: 0.6rem;
    margin: 1.5rem 0 0.8rem 0;
  }

  /* Data cards */
  .data-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
  }

  /* Field label */
  .field-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.2rem;
  }

  /* Field value */
  .field-value {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    color: var(--text-primary);
    font-weight: 500;
  }

  /* Mono value (for codes, numbers, dates) */
  .field-value-mono {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-mono);
  }

  /* Null/missing value */
  .field-null {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-style: italic;
  }

  /* Confidence badge */
  .badge-high   { background:#1a3a2a; color:#3fb950; border:1px solid #3fb950; padding:2px 10px; border-radius:20px; font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700; letter-spacing:0.08em; }
  .badge-medium { background:#2d2a1a; color:#e3b341; border:1px solid #e3b341; padding:2px 10px; border-radius:20px; font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700; letter-spacing:0.08em; }
  .badge-low    { background:#3a1a1a; color:#f85149; border:1px solid #f85149; padding:2px 10px; border-radius:20px; font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700; letter-spacing:0.08em; }

  /* Step card */
  .step-card {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-top: 3px solid var(--amber);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
  }

  .step-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--amber);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.8rem;
  }

  /* At-a-glance grid */
  .glance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.6rem;
    margin-bottom: 1rem;
  }

  /* Status bar */
  .status-bar {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.6rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
    display: flex;
    gap: 1.5rem;
  }

  /* Streamlit button override */
  .stButton > button {
    background-color: var(--amber);
    color: #0d1117;
    border: none;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-radius: 4px;
    padding: 0.5rem 1.5rem;
    width: 100%;
  }

  .stButton > button:hover {
    background-color: #e8b520;
    color: #0d1117;
  }

  /* File uploader */
  [data-testid="stFileUploader"] {
    background-color: var(--bg-card);
    border: 1px dashed var(--border);
    border-radius: 6px;
    padding: 0.5rem;
  }

  /* Expander */
  [data-testid="stExpander"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
  }

  /* Divider */
  hr { border-color: var(--border); margin: 1.5rem 0; }

  /* Warning/info boxes */
  .stAlert { border-radius: 6px; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def val(v, mono=False):
    """Render a field value — shows styled null if missing."""
    if v is None or v == "" or v == []:
        return '<span class="field-null">— not found —</span>'
    if isinstance(v, list):
        return '<span class="field-value">' + ", ".join(str(i) for i in v) + '</span>'
    css = "field-value-mono" if mono else "field-value"
    return f'<span class="{css}">{v}</span>'


def field(label, value, mono=False):
    """Render a labeled field inside a card."""
    st.markdown(f"""
    <div>
      <div class="field-label">{label}</div>
      <div>{val(value, mono)}</div>
    </div>
    """, unsafe_allow_html=True)


def confidence_badge(level):
    """Render a green/yellow/red confidence badge."""
    if not level:
        return ""
    css = f"badge-{level.lower()}"
    return f'<span class="{css}">{level.upper()}</span>'


def save_results(t1, t2, sol_number):
    """Save both tier JSONs to outputs folder."""
    folder = os.path.join("outputs", sol_number)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "tier1.json"), "w") as f:
        json.dump(t1, f, indent=2)
    with open(os.path.join(folder, "tier2.json"), "w") as f:
        json.dump(t2, f, indent=2)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="rfp-title">RFP Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="rfp-subtitle">GovCon Intelligence Tool · v0.1</div>', unsafe_allow_html=True)

    st.markdown("---")

    # RFP folder selector
    rfp_folders = []
    if os.path.exists("data"):
        rfp_folders = [f for f in os.listdir("data") if os.path.isdir(os.path.join("data", f))]

    if rfp_folders:
        selected_folder = st.selectbox(
            "SELECT RFP",
            options=rfp_folders,
            help="Choose an RFP folder from your data/ directory"
        )
    else:
        st.warning("No RFP folders found in data/")
        selected_folder = None

    st.markdown("---")

    # Force rebuild toggle
    force_rebuild = st.toggle(
        "Force DB Rebuild",
        value=False,
        help="Wipe and rebuild ChromaDB. Use when you add new PDFs."
    )

    st.markdown("---")

    # Run button
    run = st.button("⚡ ANALYZE RFP")

    st.markdown("---")

    # Previously saved outputs
    st.markdown('<div class="field-label">Saved Outputs</div>', unsafe_allow_html=True)
    if os.path.exists("outputs"):
        saved = os.listdir("outputs")
        if saved:
            for s in saved:
                st.markdown(f'<div class="field-value" style="font-size:0.8rem;">📁 {s}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="field-null">None yet</div>', unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────

# Session state persists data between Streamlit reruns
# Without this, results would disappear every time the user clicks anything
if "tier1" not in st.session_state:
    st.session_state.tier1 = None
if "tier2" not in st.session_state:
    st.session_state.tier2 = None
if "error" not in st.session_state:
    st.session_state.error = None


# ─── RUN PIPELINE ────────────────────────────────────────────────────────────

if run and selected_folder:
    with st.spinner("Loading and embedding documents..."):
        try:
            documents = generate_database(selected_folder, force_rebuild=force_rebuild)
        except Exception as e:
            st.session_state.error = f"Failed to load documents: {e}"
            documents = None

    if documents:
        with st.spinner("Running Tier 1 extraction..."):
            try:
                text = get_first_pages_text(documents)
                st.session_state.tier1 = extract_tier1(text)
            except Exception as e:
                st.session_state.error = f"Tier 1 extraction failed: {e}"

        with st.spinner("Running Tier 2 extraction..."):
            try:
                text2 = get_relevant_text(selected_folder)
                st.session_state.tier2 = extract_tier2(text2)
            except Exception as e:
                st.session_state.error = f"Tier 2 extraction failed: {e}"

        if st.session_state.tier1 and st.session_state.tier2:
            sol = st.session_state.tier1.get("solicitation_number", selected_folder)
            save_results(st.session_state.tier1, st.session_state.tier2, sol)
            st.session_state.error = None


# ─── ERROR DISPLAY ────────────────────────────────────────────────────────────

if st.session_state.error:
    st.error(st.session_state.error)


# ─── MAIN DISPLAY ────────────────────────────────────────────────────────────

t1 = st.session_state.tier1
t2 = st.session_state.tier2

if not t1:
    # Empty state — shown before any analysis is run
    st.markdown("""
    <div style="text-align:center; padding: 5rem 2rem;">
      <div style="font-family:'Space Mono',monospace; font-size:3rem; color:#30363d;">◈</div>
      <div style="font-family:'Space Mono',monospace; font-size:0.9rem; color:#8b949e; margin-top:1rem; letter-spacing:0.1em;">
        SELECT AN RFP FOLDER AND CLICK ANALYZE
      </div>
      <div style="font-family:'DM Sans',sans-serif; font-size:0.8rem; color:#8b949e; margin-top:0.5rem;">
        Results will appear here
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Header ──────────────────────────────────────────────────────────────
    sol_number = t1.get("solicitation_number", "—")
    confidence = t1.get("confidence", "—")

    col_title, col_badge = st.columns([5, 1])
    with col_title:
        st.markdown(f'<div class="rfp-title">{sol_number}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="rfp-subtitle">{t1.get("title", "")}</div>', unsafe_allow_html=True)
    with col_badge:
        st.markdown(f"""
        <div style="text-align:right; padding-top:0.5rem;">
          <div class="field-label">Confidence</div>
          {confidence_badge(confidence)}
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    # Tabs let the user switch between views without scrolling forever
    tab1, tab2, tab3 = st.tabs(["📋  AT A GLANCE", "📦  SUBMISSION", "{ }  RAW JSON"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — AT A GLANCE (Tier 1)
    # ════════════════════════════════════════════════════════════════════════
    with tab1:

        # Row 1: key facts in columns
        st.markdown('<div class="section-header">Key Facts</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Agency", t1.get("agency"))
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Set-Aside", t1.get("set_aside_type"))
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("NAICS Codes", t1.get("naics_codes"), mono=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Sub-Agency / Office", t1.get("sub_agency_office"))
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Contract Type", t1.get("contract_type"))
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("PSC Codes", t1.get("psc_codes"), mono=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Due Date", t1.get("due_date"), mono=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Period of Performance", t1.get("period_of_performance"), mono=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Contract value — show range if both present
            v_min = t1.get("estimated_value_min")
            v_max = t1.get("estimated_value_max")
            if v_max:
                v_str = f"${v_max:,.0f}" if not v_min else f"${v_min:,.0f} – ${v_max:,.0f}"
            else:
                v_str = None
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Contract Ceiling", v_str, mono=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 2: place of performance + CO
        st.markdown('<div class="section-header">Location & Contact</div>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)

        with c4:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Place of Performance", t1.get("place_of_performance"))
            st.markdown("</div>", unsafe_allow_html=True)

        with c5:
            co = t1.get("contracting_officer", {})
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            field("Contracting Officer", co.get("name"))
            field("Email", co.get("email"), mono=True)
            field("Phone", co.get("phone"), mono=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Inferred fields warning
        inferred = t1.get("fields_inferred", [])
        if inferred:
            st.warning(f"⚠ The following fields were inferred (verify manually): {', '.join(inferred)}")

        # Download button for Tier 1 JSON
        st.markdown("---")
        st.download_button(
            label="⬇ DOWNLOAD TIER 1 JSON",
            data=json.dumps(t1, indent=2),
            file_name=f"{sol_number}_tier1.json",
            mime="application/json"
        )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — SUBMISSION REQUIREMENTS (Tier 2)
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        if not t2:
            st.info("Tier 2 data not available.")
        else:
            # Submission basics
            st.markdown('<div class="section-header">Submission Basics</div>', unsafe_allow_html=True)
            c6, c7, c8 = st.columns(3)

            with c6:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                field("Page Limit", t2.get("page_limit_total"), mono=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                field("Submission Method", t2.get("submission_method"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c7:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                field("Volume Structure", t2.get("volume_structure"))
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                field("Required Forms", t2.get("required_forms"))
                st.markdown("</div>", unsafe_allow_html=True)

            with c8:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                field("Q&A Deadline", t2.get("qa_deadline"), mono=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                field("Number of Copies", t2.get("number_of_copies"), mono=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Format requirements
            fmt = t2.get("format_requirements")
            if fmt and isinstance(fmt, dict):
                st.markdown('<div class="section-header">Format Requirements</div>', unsafe_allow_html=True)
                cf1, cf2, cf3 = st.columns(3)
                with cf1:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    field("Font", fmt.get("font"))
                    st.markdown("</div>", unsafe_allow_html=True)
                with cf2:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    field("Margins", fmt.get("margins"))
                    st.markdown("</div>", unsafe_allow_html=True)
                with cf3:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    field("File Type", fmt.get("file_type"))
                    st.markdown("</div>", unsafe_allow_html=True)

            # Step requirements
            steps = t2.get("step_requirements")
            if steps:
                st.markdown('<div class="section-header">Multiphase Step Requirements</div>', unsafe_allow_html=True)
                for step_key, step_data in steps.items():
                    if step_data:
                        st.markdown(f'<div class="step-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="step-title">{step_key.replace("_", " ").upper()}</div>', unsafe_allow_html=True)
                        field("Due Date", step_data.get("due_date"), mono=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        field("Requirements", step_data.get("requirements"))
                        st.markdown("<br>", unsafe_allow_html=True)
                        field("Evaluation Guidance", step_data.get("evaluation_guidance"))
                        st.markdown("</div>", unsafe_allow_html=True)

            # Inferred fields warning
            inferred2 = t2.get("fields_inferred", [])
            if inferred2:
                st.warning(f"⚠ Inferred fields (verify manually): {', '.join(inferred2)}")

            st.markdown("---")
            st.download_button(
                label="⬇ DOWNLOAD TIER 2 JSON",
                data=json.dumps(t2, indent=2),
                file_name=f"{sol_number}_tier2.json",
                mime="application/json"
            )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — RAW JSON
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-header">Tier 1 — Hard Facts</div>', unsafe_allow_html=True)
        st.json(t1)

        st.markdown('<div class="section-header">Tier 2 — Submission Requirements</div>', unsafe_allow_html=True)
        st.json(t2)