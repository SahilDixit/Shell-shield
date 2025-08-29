import pandas as pd
import networkx as nx

def build_graph():
    """Builds a heterogeneous graph from CSV data."""
    df_companies = pd.read_csv('../data/companies.csv')
    df_people = pd.read_csv('../data/people.csv')
    df_addresses = pd.read_csv('../data/addresses.csv')
    df_director_of = pd.read_csv('../data/director_of.csv')
    df_registered_at = pd.read_csv('../data/registered_at.csv')

    G = nx.Graph()

    # Add nodes with attributes
    for _, row in df_companies.iterrows():
        G.add_node(row['company_id'], type='company', name=row['company_name'], **row.to_dict())
    
    for _, row in df_people.iterrows():
        G.add_node(row['person_id'], type='person', name=row['person_name'])
        
    for _, row in df_addresses.iterrows():
        G.add_node(row['address_id'], type='address', address=row['address'])

    # Add edges
    for _, row in df_director_of.iterrows():
        G.add_edge(row['person_id'], row['company_id'], type='director_of')
        
    for _, row in df_registered_at.iterrows():
        G.add_edge(row['company_id'], row['address_id'], type='registered_at')
        
    return G