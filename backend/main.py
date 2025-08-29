# Assuming the backend files are in the current directory for this hackathon setup
# from graph_builder import build_graph # Removed after merging
# from model_server import ModelServer # Removed after merging
# from pdf_generator import create_pdf_report # Removed after merging
import graph_builder
import model_server
import pdf_generator
import pandas as pd
import networkx as nx
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pyvis.network import Network
from graph_builder import build_graph
from model_server import ModelServer
from pdf_generator import create_pdf_report
from generate_synthetic_data import generate_synthetic_data 

app = FastAPI(title="Shell Shield API")

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Globals (for hackathon simplicity) ---
print("Building graph and loading model...")
G = build_graph() # Now calling the locally defined function
model_server = ModelServer(G) # ModelServer class is now defined in this cell
companies_df = pd.read_csv('../data/companies.csv')
print("API Ready.")
# ---

@app.get("/search-companies")
def search_companies(query: str):
    """Autocomplete for company names."""
    matches = companies_df[companies_df['company_name'].str.contains(query, case=False)]
    return matches.head(10).to_dict('records')

@app.get("/assess/{company_id}")
def assess_company(company_id: str):
    """Run risk assessment for a given company ID."""
    if company_id not in G:
        raise HTTPException(status_code=404, detail="Company ID not found")

    company_name = G.nodes[company_id].get('name', 'Unknown Company')

    # 1. Get Risk Score and Reasons
    prediction = model_server.predict(company_id)

    # 2. Generate Interactive Graph
    subgraph = nx.ego_graph(G, company_id, radius=1)
    net = Network(height="500px", width="100%", notebook=True, cdn_resources='in_line')
    net.from_nx(subgraph)

    # Customize nodes
    for node in net.nodes:
        node_type = G.nodes[node['id']].get('type', 'unknown')
        if node_type == 'company':
            node['color'] = '#FFC107' # Amber
            node['size'] = 25
        elif node_type == 'person':
            node['color'] = '#2196F3' # Blue
            node['shape'] = 'dot'
        elif node_type == 'address':
            node['color'] = '#4CAF50' # Green
            node['shape'] = 'square'

    # Highlight the target company
    for node in net.nodes:
        if node['id'] == company_id:
            node['color'] = '#F44336' # Red
            node['size'] = 40
            break

    # Ensure nodes and edges are added to the pyvis network correctly
    # This part might need adjustment depending on how pyvis.from_nx handles attributes
    # For simplicity in hackathon, relying on default from_nx which usually works for basic attributes

    graph_html = net.generate_html(name=f'graph_{company_id}.html')

    return {
        "company_id": company_id,
        "company_name": company_name,
        "assessment": prediction,
        "graph_html": graph_html
    }

@app.get("/download-report/{company_id}")
def download_report(company_id: str):
    """Generate and return a PDF report."""
    if company_id not in G:
        raise HTTPException(status_code=404, detail="Company ID not found")

    company_name = G.nodes[company_id].get('name', 'Unknown Company')
    prediction = model_server.predict(company_id)

    report_data = {
        "company_id": company_id,
        "company_name": company_name,
        **prediction
    }

    pdf_bytes = create_pdf_report(report_data)

    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        'Content-Disposition': f'attachment; filename="ShellShield_Report_{company_id}.pdf"'
    })