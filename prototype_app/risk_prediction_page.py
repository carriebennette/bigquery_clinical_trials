import streamlit as st
import time
import matplotlib.pyplot as plt
import matplotlib as mpl

st.markdown("""
<style>
html, body, [class*="css"], .stMarkdown, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: Arial, -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# Matplotlib font to match
mpl.rcParams.update({
    "font.family": "Arial",
    "font.size": 14,
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
})

def show_risk_page():
    st.title("🏗️ Trial Design")
    st.markdown("""
    This tool predicts the probability that a cancer clinical trial will experience low accrual, 
    based on key trial design, disease context, and intervention characteristics. 
    """)

    # --- initialize session state ---
    if "risk" not in st.session_state:
        st.session_state.risk = None   # no prediction yet
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # --- SIDEBAR INPUTS ---
    st.sidebar.header("Trial Details")
    title = st.sidebar.text_area("Title")
    eligibility = st.sidebar.text_area("Eligibility Criteria")
    description = st.sidebar.text_area("Trial Description")

    # --- SUBMIT BUTTON ---
    if st.sidebar.button("Submit"):
        with st.spinner("Sending input to BigQuery for feature engineering..."):
            time.sleep(2)
        with st.spinner("Running inference on BigQuery..."):
            time.sleep(2)

        # set initial prediction
        st.session_state.risk = 76
        st.session_state.submitted = True
        st.session_state.applied = False

    # --- MAIN CONTENT ---
    if st.session_state.submitted:
        # Always render the current chart first (single bar if not applied; overlay if applied)
        if not st.session_state.applied:
            st.write("#### Risk of low accrual (%):")
            # single bar
            fig, ax = plt.subplots(figsize=(6, 0.8))
            ax.barh([""], [st.session_state.risk], height=0.18, color="#d9534f", alpha=0.85)
            fig.patch.set_alpha(0)
            ax.set_facecolor("none")
            ax.set_xlim(0, 100)
            ax.set_yticks([])
            ax.spines[:].set_visible(False)
            ax.tick_params(left=False, bottom=False)
            ax.xaxis.set_label_position("top")
            ax.xaxis.tick_top()
            ax.tick_params(axis="x", labeltop=True, labelbottom=False, colors="white")
            ax.xaxis.set_tick_params(colors="white")
            ax.bar_label(ax.containers[0], fmt="%.0f%%", label_type="center", color="white", fontsize=12)
            st.pyplot(fig, transparent=True)

            # Suggestions + Apply All button (ensure unique key)
            with st.spinner("Getting suggestions to lower risk..."):
                time.sleep(1)
            st.write("#### Suggestions to improve enrollment:")
            st.markdown("""
            - Use RECIST or imaging-based response instead of requiring pathologic confirmation, which simplifies the primary endpoint and aligns with oncology standards.
            - Make the 6-week biopsy optional, allow archival tissue at baseline, and substitute ctDNA or blood biomarkers to reduce invasiveness and patient burden.
            - Broaden eligibility by shortening the secondary malignancy exclusion window to 2 years and allowing indolent cancers without affecting melanoma outcomes.
            - Relax lab cutoffs (ANC ≥1.0, platelets ≥75, AST/ALT ≤3× ULN, creatinine clearance ≥40) and allow transfusion support to include patients with borderline labs while maintaining safety.
            """)

            if st.button("✅  Apply all", key="apply_all"):
                # set new risk and hide suggestions on next render
                st.session_state.applied = True
                st.session_state.baseline_risk = 76
                st.session_state.risk = 42   # new value for demo
            
        else:
            with st.spinner("Re-running model with applied changes..."):
                time.sleep(2)
            
            st.write("#### Risk of low accrual (%):")
            fig, ax = plt.subplots(figsize=(6, 0.8))

            # Example values – replace with your own state variables
            original_risk = 76
            new_risk = 32

            # Draw original risk with low opacity
            ax.barh([""], [original_risk], height=0.18, color="#d9534f", alpha=0.25)

            # Draw new risk with higher opacity
            ax.barh([""], [new_risk], height=0.18, color="#d9534f", alpha=0.85)

            # Transparent background
            fig.patch.set_alpha(0)
            ax.set_facecolor("none")
            ax.set_xlim(0, 100)
            ax.set_yticks([])
            ax.xaxis.set_label_position("top")
            ax.xaxis.tick_top()
            ax.tick_params(axis="x", labeltop=True, labelbottom=False, colors="white")
            ax.spines[:].set_visible(False)
            ax.tick_params(left=False, bottom=False)

            # White text
            ax.xaxis.set_tick_params(colors="white")

            # Add labels (only for new risk to avoid clutter)
            ax.bar_label(ax.containers[1], fmt="%.0f%%", label_type="center", color="white", fontsize=12)
            st.pyplot(fig, transparent=True)

            st.write("#### Suggestions applied:")
            st.markdown("""
            - Use RECIST or imaging-based response instead of requiring pathologic confirmation, which simplifies the primary endpoint and aligns with oncology standards.
            - Make the 6-week biopsy optional, allow archival tissue at baseline, and substitute ctDNA or blood biomarkers to reduce invasiveness and patient burden.
            - Broaden eligibility by shortening the secondary malignancy exclusion window to 2 years and allowing indolent cancers without affecting melanoma outcomes.
            - Relax lab cutoffs (ANC ≥1.0, platelets ≥75, AST/ALT ≤3× ULN, creatinine clearance ≥40) and allow transfusion support to include patients with borderline labs while maintaining safety.
            """)
            if st.button("↩️  Undo suggestions", key="undo_all"):
                # set new risk and hide suggestions on next render
                st.session_state.applied = True
                st.session_state.baseline_risk = 76
                st.session_state.risk = 42   # new value for demo

    else:
        st.info("Fill out trial details in the sidebar, then click **Submit** to see results.")
