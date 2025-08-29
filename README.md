# 🛡️ Shell Shield – AI-Powered Shell Company Detection  

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)  
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-orange.svg)  
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)  
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)  

**Shell Shield** is an AI-driven compliance tool that detects **dummy/shell companies** by analyzing company ownership networks, regulatory filings, and digital footprints.  

It builds a **heterogeneous knowledge graph** (companies, directors, addresses), extracts engineered features (shared addresses, director overlaps, domain/web footprint, ownership cycles), and runs them through a **LightGBM classifier with SHAP explainability**.  

The system generates a **Shell Risk Score (0–100)** with **plain-English reasons**, helping compliance teams and regulators quickly identify suspicious firms.  

---

##  Features
-  **Shell Risk Scoring** – Outputs a 0–100 risk score with verdict (Low/Medium/High).  
-  **Explainable AI** – SHAP-based reason codes in plain English.  
-  **Graph Analytics** – Detects shared addresses, overlapping directors, and circular ownership (cycles ≤ 4).  
-  **Interactive Dashboard** – Built with Streamlit for company search, risk cards, and graph visualization.  
-  **Reporting** – Export investigator-friendly reports in **PDF/CSV**.  
-  **Synthetic Dataset** – Generates realistic company-graph data for training/testing.  

---

## 📂 Project Structure
ShellShield/
│── data/ # Synthetic dataset (companies, directors, addresses)
│── backend/
│ ├── main.py # FastAPI backend service
│ ├── model_server.py # ML model serving (LightGBM + SHAP)
│── frontend/
│ ├── app.py # Streamlit dashboard
│── reports/ # Generated PDFs/CSVs
│── pdf_generator.py # ReportLab-based PDF generator
│── requirements.txt # Python dependencies
│── README.md # Project documentation
