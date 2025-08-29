import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components

# --- Configuration ---
st.set_page_config(page_title="Shell Shield", layout="wide")
API_URL = "http://127.0.0.1:8000"

# --- Page Title and Intro ---
st.title("🛡️ Shell Shield")
st.markdown("Analyzing company networks to uncover hidden risks. Enter a company name below to begin.")

# --- Search Bar ---
company_name = st.text_input("Enter Company Name", "Smith Ltd")

if 'company_id' not in st.session_state:
    st.session_state.company_id = None
if 'company_name' not in st.session_state:
    st.session_state.company_name = None

if company_name:
    try:
        response = requests.get(f"{API_URL}/search-companies", params={"query": company_name})
        if response.status_code == 200:
            companies = response.json()
            if companies:
                company_map = {c['company_name']: c['company_id'] for c in companies}
                selected_name = st.selectbox("Select a company to assess:", options=list(company_map.keys()))
                st.session_state.company_id = company_map[selected_name]
                st.session_state.company_name = selected_name
            else:
                st.warning("No companies found matching that name.")
        else:
            st.error("Failed to fetch companies from the backend.")
    except requests.exceptions.ConnectionError:
        st.error("Connection Error: Is the backend server running?")


# --- Assess Button and Results ---
if st.button("Assess Company", disabled=(not st.session_state.company_id)):
    with st.spinner(f"Analyzing {st.session_state.company_name}..."):
        try:
            res = requests.get(f"{API_URL}/assess/{st.session_state.company_id}")
            if res.status_code == 200:
                st.session_state.results = res.json()
            else:
                st.error(f"Error from API: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Is the backend server running?")
            st.session_state.results = None

if 'results' in st.session_state and st.session_state.results:
    results = st.session_state.results
    assessment = results.get('assessment', {})
    
    st.markdown("---")
    st.subheader(f"Assessment for: **{results.get('company_name')}**")
    
    # --- Risk Card and Reasons ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        score = assessment.get('score', 0)
        verdict = assessment.get('verdict', 'Unknown')
        
        if verdict == "High Risk":
            color = "red"
        elif verdict == "Medium Risk":
            color = "orange"
        else:
            color = "green"
            
        st.metric(label="Shell Risk Score", value=f"{score}/100", delta=verdict)
        
        st.download_button(
            label="📄 Download PDF Report",
            data=requests.get(f"{API_URL}/download-report/{results.get('company_id')}").content,
            file_name=f"ShellShield_Report_{results.get('company_id')}.pdf",
            mime="application/pdf"
        )
        
    with col2:
        st.markdown("#### **Why this score?**")
        reasons = assessment.get('reasons', [])
        for reason in reasons:
            st.markdown(f"- {reason}")
            
    st.markdown("---")
    
    # --- Interactive Graph ---
    st.subheader("Interactive Ownership Graph")
    st.info("Explore the company's immediate network. Red node is the target company.")
    graph_html = results.get('graph_html')
    if graph_html:
        components.html(graph_html, height=510)