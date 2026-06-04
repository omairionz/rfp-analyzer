# app.py
# Run with: streamlit run app.py

import streamlit as st
import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from src.parse_rfp import generate_database, get_first_pages_text, get_relevant_text, find_section_m_pages, tier3_page_content
from src.extract_tier1 import extract_tier1
from src.extract_tier2 import extract_tier2
from src.extract_tier3 import extract_tier3

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
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

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

  .stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'DM Sans', sans-serif;
  }

  [data-testid="stSidebar"] {
    background-color: var(--bg-secondary);
    border-right: 1px solid var(--border);
  }

  #MainMenu, footer, header { visibility: hidden; }

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

  .rfp-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    letter-spacing: 0.04em;
    margin-bottom: 0.5rem;
  }

  .meta-line {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
  }

  .meta-model {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-mono);
  }

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

  .data-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
  }

  .field-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.2rem;
    margin-top: 0.6rem;
  }

  .field-label:first-child { margin-top: 0; }

  .field-value {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    color: var(--text-primary);
    font-weight: 500;
  }

  .field-value-mono {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-mono);
  }

  .field-null {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-style: italic;
  }

  .badge-high   { background:#1a3a2a; color:#3fb950; border:1px solid #3fb950; padding:2px 10px; border-radius:20px; font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700; letter-spacing:0.08em; }
  .badge-medium { background:#2d2a1a; color:#e3b341; border:1px solid #e3b341; padding:2px 10px; border-radius:20px; font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700; letter-spacing:0.08em; }
  .badge-low    { background:#3a1a1a; color:#f85149; border:1px solid #f85149; padding:2px 10px; border-radius:20px; font-family:'Space Mono',monospace; font-size:0.7rem; font-weight:700; letter-spacing:0.08em; }
  .badge-yes    { background:#1a3a2a; color:#3fb950; border:1px solid #3fb950; padding:2px 8px; border-radius:4px; font-family:'Space Mono',monospace; font-size:0.65rem; font-weight:700; }
  .badge-no     { background:#2a1a1a; color:#8b949e; border:1px solid #30363d; padding:2px 8px; border-radius:4px; font-family:'Space Mono',monospace; font-size:0.65rem; font-weight:700; }

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
    margin-bottom: 0.6rem;
  }

  .factor-card {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border);
    border-left: 3px solid var(--text-mono);
    border-radius: 6px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.4rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: var(--text-primary);
  }

  .missing-tag {
    display: inline-block;
    background: #1a1a2a;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 1px 7px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    margin: 2px 3px 2px 0;
  }

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

  hr { border-color: var(--border); margin: 1.5rem 0; }
  .stAlert { border-radius: 6px; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def val(v, mono=False):
    """Convert a value to styled HTML. Returns null placeholder if empty."""
    if v is None or v == "" or v == []:
        return '<span class="field-null">— not found —</span>'
    if isinstance(v, list):
        return '<span class="field-value">' + ", ".join(str(i) for i in v) + '</span>'
    css = "field-value-mono" if mono else "field-value"
    return f'<span class="{css}">{v}</span>'


def card(*rows):
    """
    Render a single data-card with any number of label/value rows.
    Each row is a tuple: (label, value) or (label, value, mono=True)
    All rows go into ONE st.markdown call — no ghost blocks.
    """
    inner = ""
    for row in rows:
        label = row[0]
        value = row[1]
        mono  = row[2] if len(row) > 2 else False
        inner += f'<div class="field-label">{label}</div><div>{val(value, mono)}</div>'
    st.markdown(f'<div class="data-card">{inner}</div>', unsafe_allow_html=True)


def yn_badge(v):
    """Green YES / grey NO badge."""
    if not v:
        return '<span class="field-null">— not found —</span>'
    css = "badge-yes" if str(v).strip().lower() == "yes" else "badge-no"
    return f'<span class="{css}">{str(v).upper()}</span>'


def confidence_badge(level):
    if not level:
        return ""
    return f'<span class="badge-{level.lower()}">{level.upper()}</span>'


def missing_tags(fields):
    if not fields:
        return ""
    tags = "".join(f'<span class="missing-tag">{f}</span>' for f in fields)
    return f'<div style="margin-top:0.5rem;">{tags}</div>'


def save_results(t1, t2, t3, sol_number):
    folder = os.path.join("outputs", sol_number)
    os.makedirs(folder, exist_ok=True)
    for name, data in [("tier1", t1), ("tier2", t2), ("tier3", t3)]:
        if data:
            with open(os.path.join(folder, f"{name}.json"), "w") as f:
                json.dump(data, f, indent=2)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="rfp-title">RFP Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="rfp-subtitle">GovCon Intelligence Tool · v0.1</div>', unsafe_allow_html=True)
    st.markdown("---")

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
    force_rebuild = st.toggle("Force DB Rebuild", value=False,
        help="Wipe and rebuild ChromaDB. Use when you add new PDFs.")
    st.markdown("---")
    run = st.button("⚡ ANALYZE RFP")
    st.markdown("---")

    st.markdown('<div class="field-label">Saved Outputs</div>', unsafe_allow_html=True)
    if os.path.exists("outputs"):
        saved = os.listdir("outputs")
        if saved:
            for s in saved:
                st.markdown(f'<div class="field-value" style="font-size:0.8rem;">📁 {s}</div>',
                    unsafe_allow_html=True)
        else:
            st.markdown('<span class="field-null">None yet</span>', unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────

for key in ["tier1", "tier2", "tier3", "error"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ─── RUN PIPELINE ────────────────────────────────────────────────────────────

if run and selected_folder:
    documents = None

    with st.spinner("Loading and embedding documents..."):
        try:
            documents = generate_database(selected_folder, force_rebuild=force_rebuild)
        except Exception as e:
            st.session_state.error = f"Failed to load documents: {e}"

    if documents:
        with st.spinner("Running Tier 1 extraction..."):
            try:
                st.session_state.tier1 = extract_tier1(get_first_pages_text(documents))
            except Exception as e:
                st.session_state.error = f"Tier 1 failed: {e}"

        with st.spinner("Running Tier 2 extraction..."):
            try:
                st.session_state.tier2 = extract_tier2(get_relevant_text(selected_folder))
            except Exception as e:
                st.session_state.error = f"Tier 2 failed: {e}"

        with st.spinner("Running Tier 3 extraction..."):
            try:
                pages = find_section_m_pages(documents, selected_folder)
                st.session_state.tier3 = extract_tier3(tier3_page_content(documents, pages)) if pages else None
            except Exception as e:
                st.session_state.error = f"Tier 3 failed: {e}"

        if st.session_state.tier1:
            sol = st.session_state.tier1.get("solicitation_number", selected_folder)
            save_results(st.session_state.tier1, st.session_state.tier2, st.session_state.tier3, sol)
            st.session_state.error = None


# ─── ERROR ────────────────────────────────────────────────────────────────────

if st.session_state.error:
    st.error(st.session_state.error)


# ─── MAIN DISPLAY ────────────────────────────────────────────────────────────

t1 = st.session_state.tier1
t2 = st.session_state.tier2
t3 = st.session_state.tier3

if not t1:
    st.markdown("""
    <div style="text-align:center; padding:5rem 2rem;">
      <div style="font-family:'Space Mono',monospace;font-size:3rem;color:#30363d;">◈</div>
      <div style="font-family:'Space Mono',monospace;font-size:0.9rem;color:#8b949e;margin-top:1rem;letter-spacing:0.1em;">
        SELECT AN RFP FOLDER AND CLICK ANALYZE
      </div>
      <div style="font-family:'DM Sans',sans-serif;font-size:0.8rem;color:#8b949e;margin-top:0.5rem;">
        Results will appear here
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    sol_number = t1.get("solicitation_number", "—")
    confidence = t1.get("confidence", "—")
    model      = t1.get("model", "—")

    # ── Header ───────────────────────────────────────────────────────────────
    col_title, col_meta = st.columns([5, 1])
    with col_title:
        st.markdown(f'<div class="rfp-title">{sol_number}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="rfp-subtitle">{t1.get("title", "")}</div>', unsafe_allow_html=True)
    with col_meta:
        # Confidence badge + model — both metadata, both in the top-right corner
        st.markdown(f"""
        <div style="text-align:right; padding-top:0.5rem;">
          <div class="field-label">Confidence</div>
          {confidence_badge(confidence)}
          <div class="field-label" style="margin-top:0.6rem;">Model</div>
          <div class="meta-model">{model}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋  AT A GLANCE",
        "📦  SUBMISSION",
        "⚖️  EVALUATION",
        "{ }  RAW JSON"
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — AT A GLANCE (Tier 1)
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="section-header">Key Facts</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            card(("Agency", t1.get("agency")))
            card(("Set-Aside", t1.get("set_aside_type")))
            card(("Notice Type", t1.get("notice_type")))
            card(("NAICS Codes", t1.get("naics_codes"), True))

        with c2:
            card(("Sub-Agency / Office(s)", t1.get("sub_agency_offices")))
            card(("Contract Type", t1.get("contract_type")))
            card(("Procurement Type", t1.get("procurement_type")))
            card(("PSC Codes", t1.get("psc_codes"), True))

        with c3:
            card(("Due Date", t1.get("due_date"), True))
            card(("Period of Performance", t1.get("period_of_performance"), True))

            # Contract ceiling — format as dollar amount
            v_min = t1.get("estimated_value_min")
            v_max = t1.get("estimated_value_max")
            if v_max:
                v_str = f"${v_max:,.0f}" if not v_min else f"${v_min:,.0f} – ${v_max:,.0f}"
            else:
                v_str = None
            card(("Contract Ceiling", v_str, True))

        st.markdown('<div class="section-header">Location & Contact</div>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)

        with c4:
            card(("Place of Performance", t1.get("place_of_performance")))

        with c5:
            co = t1.get("contracting_officer") or {}
            # All three CO subfields in one card — one st.markdown call, no ghost blocks
            card(
                ("Contracting Officer", co.get("name")),
                ("Email", co.get("email"), True),
                ("Phone", co.get("phone"), True),
            )

        # Missing + inferred
        missing1  = t1.get("fields_missing", [])
        inferred1 = t1.get("fields_inferred", [])
        if missing1 or inferred1:
            st.markdown("---")
        if missing1:
            st.markdown(
                f'<div class="field-label">Missing Fields</div>{missing_tags(missing1)}',
                unsafe_allow_html=True)
        if inferred1:
            st.warning(f"⚠ Inferred (verify manually): {', '.join(inferred1)}")

        st.markdown("---")
        st.download_button(
            label="⬇ DOWNLOAD TIER 1 JSON",
            data=json.dumps(t1, indent=2),
            file_name=f"{sol_number}_tier1.json",
            mime="application/json"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — SUBMISSION REQUIREMENTS (Tier 2)
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        if not t2:
            st.info("Tier 2 data not available.")
        else:
            st.markdown('<div class="section-header">Submission Basics</div>', unsafe_allow_html=True)
            c6, c7, c8 = st.columns(3)

            with c6:
                card(("Page Limit (Total)", t2.get("page_limit_total"), True))
                card(("Submission Method", t2.get("submission_method")))
                card(("Submission Email", t2.get("submission_email"), True))
                card(("Submission Deadline", t2.get("submission_deadline"), True))

            with c7:
                card(("Volume Structure", t2.get("volume_structure")))
                card(("Volume Page Limits", t2.get("volume_page_limits")))
                card(("Required Forms", t2.get("required_forms")))
                card(("Required Certifications", t2.get("required_certifications")))

            with c8:
                card(("Q&A Deadline", t2.get("qa_deadline"), True))
                card(("Late Submission Policy", t2.get("late_submission_policy")))

                # Copies — electronic + hard copy in one card
                copies = t2.get("number_of_copies") or {}
                card(
                    ("Copies — Electronic", copies.get("electronic"), True),
                    ("Copies — Hard Copy",  copies.get("hard_copy"),  True),
                )

                # Yes/No flags — one card, two rows, inline HTML for badges
                st.markdown(f"""
                <div class="data-card">
                  <div class="field-label">Amendment Acknowledgement</div>
                  <div>{yn_badge(t2.get("amendment_acknowledgement_required"))}</div>
                  <div class="field-label">Signature Required</div>
                  <div>{yn_badge(t2.get("signature_required"))}</div>
                </div>
                """, unsafe_allow_html=True)

            # Format requirements
            fmt = t2.get("format_requirements")
            if fmt and isinstance(fmt, dict):
                st.markdown('<div class="section-header">Format Requirements</div>', unsafe_allow_html=True)
                cf1, cf2, cf3 = st.columns(3)
                with cf1:
                    card(("Font", fmt.get("font")), ("Font Size", fmt.get("font_size"), True))
                with cf2:
                    card(("Spacing", fmt.get("spacing")), ("Margins", fmt.get("margins")))
                with cf3:
                    card(("File Format", fmt.get("file_format")), ("Naming Convention", fmt.get("naming_convention"), True))

            # Pre-proposal conference
            conf = t2.get("pre_proposal_conference")
            if conf and isinstance(conf, dict):
                st.markdown('<div class="section-header">Pre-Proposal Conference</div>', unsafe_allow_html=True)
                cp1, cp2, cp3 = st.columns(3)
                with cp1:
                    st.markdown(f"""
                    <div class="data-card">
                      <div class="field-label">Required</div>
                      <div>{yn_badge(conf.get("required"))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cp2:
                    card(("Date", conf.get("date"), True))
                with cp3:
                    card(("Location", conf.get("location")))

            # Step requirements
            steps = t2.get("step_requirements")
            if steps and isinstance(steps, dict):
                st.markdown('<div class="section-header">Multiphase Step Requirements</div>', unsafe_allow_html=True)
                for step_key, step_data in steps.items():
                    if step_data:
                        st.markdown(f"""
                        <div class="step-card">
                          <div class="step-title">{step_key.replace("_", " ").upper()}</div>
                          <div class="field-value">{step_data}</div>
                        </div>
                        """, unsafe_allow_html=True)

            missing2  = t2.get("fields_missing", [])
            inferred2 = t2.get("fields_inferred", [])
            if missing2 or inferred2:
                st.markdown("---")
            if missing2:
                st.markdown(
                    f'<div class="field-label">Missing Fields</div>{missing_tags(missing2)}',
                    unsafe_allow_html=True)
            if inferred2:
                st.warning(f"⚠ Inferred (verify manually): {', '.join(inferred2)}")

            st.markdown("---")
            st.download_button(
                label="⬇ DOWNLOAD TIER 2 JSON",
                data=json.dumps(t2, indent=2),
                file_name=f"{sol_number}_tier2.json",
                mime="application/json"
            )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — EVALUATION CRITERIA (Tier 3)
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        if not t3:
            st.info("Tier 3 data not available. Section M may not have been found in this document.")
        else:
            st.markdown('<div class="section-header">Evaluation Approach</div>', unsafe_allow_html=True)
            ea1, ea2 = st.columns(2)

            with ea1:
                card(("Evaluation Criteria", t3.get("evaluation_criteria")))
                card(("Factor Relative Importance", t3.get("factor_relative_importance")))
                card(("Factor Weights", t3.get("factor_weights"), True))

            with ea2:
                # Yes/No badges for boolean fields
                oral = t3.get("oral_presentations_or_demonstrations")
                oral_html = yn_badge(oral) if oral in ["Yes", "No"] else val(oral)
                st.markdown(f"""
                <div class="data-card">
                  <div class="field-label">Past Performance Required</div>
                  <div>{yn_badge(t3.get("past_performance_required"))}</div>
                  <div class="field-label">Oral Presentations / Demos</div>
                  <div>{oral_html}</div>
                </div>
                """, unsafe_allow_html=True)

                card(("Past Performance Reference Count", t3.get("past_performance_reference_count"), True))
                card(("Past Performance Requirements", t3.get("past_performance_requirements")))

            # Evaluation factors — numbered list
            factors = t3.get("evaluation_factors")
            if factors:
                st.markdown('<div class="section-header">Evaluation Factors (In Order of Importance)</div>',
                    unsafe_allow_html=True)
                for i, factor in enumerate(factors, 1):
                    st.markdown(f"""
                    <div class="factor-card">
                      <span style="color:var(--text-secondary);font-family:'Space Mono',monospace;font-size:0.7rem;">#{i}</span>
                      &nbsp; {factor}
                    </div>
                    """, unsafe_allow_html=True)

            # Clearances + certifications
            st.markdown('<div class="section-header">Requirements & Qualifications</div>', unsafe_allow_html=True)
            rq1, rq2 = st.columns(2)
            with rq1:
                card(("Clearance Requirements", t3.get("clearance_requirements")))
            with rq2:
                card(("Certifications / Qualifications Required", t3.get("certifications_or_qualifications_required")))

            missing3  = t3.get("fields_missing", [])
            inferred3 = t3.get("fields_inferred", [])
            if missing3 or inferred3:
                st.markdown("---")
            if missing3:
                st.markdown(
                    f'<div class="field-label">Missing Fields</div>{missing_tags(missing3)}',
                    unsafe_allow_html=True)
            if inferred3:
                st.warning(f"⚠ Inferred (verify manually): {', '.join(inferred3)}")

            st.markdown("---")
            st.download_button(
                label="⬇ DOWNLOAD TIER 3 JSON",
                data=json.dumps(t3, indent=2),
                file_name=f"{sol_number}_tier3.json",
                mime="application/json"
            )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — RAW JSON
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="section-header">Tier 1 — Hard Facts</div>', unsafe_allow_html=True)
        st.json(t1)

        st.markdown('<div class="section-header">Tier 2 — Submission Requirements</div>', unsafe_allow_html=True)
        st.json(t2)

        if t3:
            st.markdown('<div class="section-header">Tier 3 — Evaluation Criteria</div>', unsafe_allow_html=True)
            st.json(t3)