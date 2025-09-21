import streamlit as st
import time

def show_finder_page():
    st.title("🔍 Patient Trial Finder")
    st.caption(
        "Describe your clinical situation in plain language in the sidebar to find trials for which you may be eligible. "
        "You may also add preferences (e.g., therapy type, location, or whether the trial is randomized)."
    )

    # --- Sidebar inputs (match Trial Design layout) ---
    st.sidebar.header("Patient Description")
    condition_text = st.sidebar.text_area(
        "Describe your current clinical condition",
        placeholder='e.g., "metastatic EGFR+ NSCLC previously treated with osimertinib; ECOG 1"',
        height=120,
    )

    st.sidebar.header("Optional Preferences")
    prefs_text = st.sidebar.text_area(
        "What are you hoping to find?",
        placeholder='e.g., "immunotherapy only; open near Boston MA; single-arm or not randomized"',
        height=100,
        help="You can include therapy type, location, phase, randomization, masking, biopsy/biomarker requirements, etc.",
    )

    st.sidebar.markdown(
        """
        <div style="opacity:0.85; font-size:0.9rem;">
          <ul style="margin-top:0.25rem;">
            <li>Describe your condition in as much detail as you can. This helps narrow the list of potential trials, particularly for more common cancer types.</li>
            <li>Add any “must-have” or “avoid” aspects of trials as optional preferences.</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Submit ---
    if st.sidebar.button("Submit", use_container_width=True):
        with st.spinner("Finding your trials..."):
            time.sleep(2)
        with st.spinner("Ranking and summarizing trials..."):
            time.sleep(2)

        # --- Mock results (add/modify freely for your demo) ---
        results = [
            {
                "nct_id": "NCT05321044",
                "title": "Pembrolizumab With Chemotherapy for Advanced NSCLC",
                "summary": "Phase III, open-label study evaluating pembrolizumab + platinum doublet in metastatic NSCLC after progression on prior targeted therapy.",
                "link": "https://clinicaltrials.gov/study/NCT05321044",
                "phase": "III",
                "randomized": True,
                "sites": "Boston, MA",
                "score": 0.86,
                "rationale": "Matches EGFR+ NSCLC post-TKI; ECOG 0–1; Boston site within 10 miles.",
            },
            {
                "nct_id": "NCT04711856",
                "title": "Osimertinib and Bevacizumab in EGFR-Mutant Lung Cancer",
                "summary": "Phase II, single-arm trial for EGFR+ NSCLC exploring VEGF inhibition with third-gen EGFR TKI; endpoints include PFS and intracranial response.",
                "link": "https://clinicaltrials.gov/study/NCT04711856",
                "phase": "II",
                "randomized": False,
                "sites": "Providence, RI",
                "score": 0.73,
                "rationale": "EGFR-mutant cohort; non-randomized as requested; accepts prior osimertinib.",
            },
            {
                "nct_id": "NCT05190010",
                "title": "Atezolizumab for PD-L1 High NSCLC (Biomarker-Driven)",
                "summary": "Phase II biomarker-selected cohort assessing atezolizumab in PD-L1 ≥50%; allows prior TKI; streamlined exclusions to broaden access.",
                "link": "https://clinicaltrials.gov/study/NCT05190010",
                "phase": "II",
                "randomized": False,
                "sites": "Boston + Telehealth",
                "score": 0.69,
                "rationale": "PD-L1 ≥50% aligns with profile; flexible visit windows; nearby site.",
            },
            {
                "nct_id": "NCT05900123",
                "title": "Citywide Immunotherapy Access Study (Multi-Site)",
                "summary": "Pragmatic, multi-center study offering checkpoint inhibitor therapy with flexible visit windows; includes Boston and Providence sites with telehealth support.",
                "link": "https://clinicaltrials.gov/study/NCT05900123",
                "phase": "II/III",
                "randomized": True,
                "sites": "Boston & Providence",
                "score": 0.64,
                "rationale": "Immunotherapy preference matched; multiple local sites; broad eligibility.",
            },
        ]

        _render_card_list(results, condition_text, prefs_text)

    else:
        st.info("Enter your description in the sidebar, then click **Submit** to see matching trials.")


# ----------------- UI renderer: card list -----------------
def _render_card_list(results, condition_text, prefs_text):
    # Page header chips / echo of inputs (optional; helps demos)
    st.markdown(
        f"""
        <div style="margin: 6px 0 10px 0; opacity: 0.9;">
            <span style="
                display:inline-block; padding:6px 10px; border-radius:999px;
                background:#374151; border:1px solid rgba(255,255,255,0.15);
                font-size:0.85rem; margin-right:6px;">
                {len(results)} matches
            </span>
            {"<span style='opacity:0.8;'>for your description</span>" if condition_text else ""}
            {"<span style='opacity:0.6;'> • preferences applied</span>" if prefs_text else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Minimal styling for cards/chips (dark theme friendly)
    st.markdown("""
    <style>
      .card:hover { background: rgba(255,255,255,0.09); transform: translateY(-1px); }
      .chip {display:inline-block; padding:4px 10px; border-radius:999px; 
             background:#374151; border:1px solid rgba(255,255,255,0.15); margin-right:6px; font-size:0.85rem;}
      .title {font-weight:700; font-size:1.05rem; margin-bottom:6px;}
      .muted {opacity:0.9; font-size:0.95rem; line-height:1.45;}
      .rightcol a {display:inline-block; text-decoration:none; color:#fff;
                   background:#111827; border:1px solid rgba(255,255,255,0.18);
                   padding:8px 12px; border-radius:8px; font-weight:600;}
      .rightcol a:hover { background:#1f2937; }
      .tiny {opacity:0.8; font-size:0.85rem;}
    </style>
    """, unsafe_allow_html=True)

    for r in results:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            # two-column layout per result
            c1, c2 = st.columns([0.75, 0.25], vertical_alignment="top")

            with c1:
                st.markdown(f"<div class='title'>{r['title']}</div>", unsafe_allow_html=True)
                # chips: phase / randomized / sites
                chips = []
                if r.get("phase"): chips.append(f"<span class='chip'>Phase {r['phase']}</span>")
                if r.get("randomized") is not None:
                    chips.append(f"<span class='chip'>{'Randomized' if r['randomized'] else 'Single-arm'}</span>")
                if r.get("sites"): chips.append(f"<span class='chip'>{r['sites']}</span>")
                if chips:
                    st.markdown(" ".join(chips), unsafe_allow_html=True)

                st.markdown(f"<div class='muted' style='margin-top:8px;'>{r['summary']}</div>", unsafe_allow_html=True)

            with c2:
                # optional match score
                if r.get("score") is not None:
                    st.caption("Match score")
                    st.progress(min(max(int(r['score'] * 100), 0), 100))
                st.markdown(f"<div class='rightcol'><a href='{r['link']}' target='_blank' rel='noopener'>View record</a></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='tiny' style='margin-top:6px;'>{r['nct_id']}</div>", unsafe_allow_html=True)

            with st.expander("Why this matches (AI rationale)"):
                st.write(r.get("rationale", "Placeholder rationale text."))

            st.markdown("</div>", unsafe_allow_html=True)
