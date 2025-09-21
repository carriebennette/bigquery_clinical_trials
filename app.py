
import streamlit as st

# Set dark theme globally via config.toml or below
st.set_page_config(page_title="Clinical Trials App", layout="centered")
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = None

if st.session_state.page is None:
    st.markdown("<h2 style='text-align: center;'>Choose one of the options below to get started.</p>", unsafe_allow_html=True)

    # Two column layout for better visual presentation
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    col1, spacer, col2 = st.columns([1, 0.3, 1])

    with col1:
        st.markdown("### 🏗️ Trial Design")
        st.markdown(
            "<p style='font-size: 0.9rem;'>Predict the risk of low enrollment and improve your trial design.</p>",
            unsafe_allow_html=True
        )
        if st.button("Go to Trial Design"):
            st.session_state.page = "risk"

    with col2:
        st.markdown("### 🔍 Trial Search")
        st.markdown(
            "<p style='font-size: 0.9rem;'>Find cancer clinical trials with AI-powered semantic search.</p>",
            unsafe_allow_html=True
        )
        if st.button("Go to Trial Search"):
            st.session_state.page = "finder"


if st.session_state.page == "risk":
    from risk_prediction_page import show_risk_page
    show_risk_page()
    

elif st.session_state.page == "finder":
    from trial_finder_page import show_finder_page
    show_finder_page()