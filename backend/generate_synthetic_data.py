import pandas as pd
import numpy as np
from faker import Faker
import random
import networkx as nx
from datetime import datetime, timedelta
import os
def generate_synthetic_data():
    """Generates synthetic data for companies, people, addresses, and their relationships."""
    fake = Faker()

    # Configuration
    NUM_COMPANIES = 2000
    NUM_PEOPLE = 3000
    NUM_ADDRESSES = 1000
    SHELL_PERCENTAGE = 0.15

    # Create output directory
    if not os.path.exists('../data'):
        os.makedirs('../data')

    # --- Generate Base Entities ---
    print("Generating base entities...")
    companies = [{'company_id': f'C{i}', 'company_name': fake.company()} for i in range(NUM_COMPANIES)]
    people = [{'person_id': f'P{i}', 'person_name': fake.name()} for i in range(NUM_PEOPLE)]
    addresses = [{'address_id': f'A{i}', 'address': fake.address().replace('\n', ', ')} for i in range(NUM_ADDRESSES)]

    df_companies = pd.DataFrame(companies)
    df_people = pd.DataFrame(people)
    df_addresses = pd.DataFrame(addresses)

    # --- Generate Relationships ---
    print("Generating relationships...")
    # Director of
    director_of = []
    for i in range(NUM_PEOPLE):
        num_directorships = int(np.random.exponential(1.2)) + 1
        comps = random.sample(companies, min(num_directorships, len(companies)))
        for comp in comps:
            director_of.append({'person_id': f'P{i}', 'company_id': comp['company_id']})

    # Registered at
    registered_at = []
    for i in range(NUM_COMPANIES):
        addr = random.choice(addresses)
        registered_at.append({'company_id': f'C{i}', 'address_id': addr['address_id']})

    df_director_of = pd.DataFrame(director_of)
    df_registered_at = pd.DataFrame(registered_at)

    # --- Generate Company Features & Plant Shells ---
    print("Generating features and planting shell companies...")
    df_companies['is_shell'] = 0
    df_companies['entity_age_days'] = [random.randint(30, 3650) for _ in range(NUM_COMPANIES)]
    df_companies['filings_per_year'] = [round(random.uniform(1, 12), 2) for _ in range(NUM_COMPANIES)]
    df_companies['domain_age_days'] = df_companies['entity_age_days'] - np.random.randint(0, 25, size=NUM_COMPANIES)
    df_companies['employee_mentions'] = [random.randint(1, 500) for _ in range(NUM_COMPANIES)]
    df_companies['credible_news_count'] = [random.randint(0, 50) for _ in range(NUM_COMPANIES)]

    shell_indices = df_companies.sample(frac=SHELL_PERCENTAGE).index
    df_companies.loc[shell_indices, 'is_shell'] = 1

    # --- Apply Shell Characteristics ---
    # Pattern 1: Shared addresses (hubs)
    num_address_hubs = int(len(shell_indices) * 0.3)
    address_hubs = df_addresses.sample(num_address_hubs).address_id.tolist()
    for i, shell_idx in enumerate(shell_indices):
        if i < len(shell_indices) * 0.5:
            hub = random.choice(address_hubs)
            df_registered_at.loc[df_registered_at['company_id'] == f'C{shell_idx}', 'address_id'] = hub

    # Pattern 2: Hyper-active directors
    num_risky_directors = int(len(shell_indices) * 0.2)
    risky_directors = df_people.sample(num_risky_directors).person_id.tolist()
    for i, shell_idx in enumerate(shell_indices):
        if i < len(shell_indices) * 0.4:
            director = random.choice(risky_directors)
            if not ((df_director_of['person_id'] == director) & (df_director_of['company_id'] == f'C{shell_idx}')).any():
                df_director_of = pd.concat([df_director_of, pd.DataFrame([{'person_id': director, 'company_id': f'C{shell_idx}'}])], ignore_index=True)

    # Pattern 3: Low web footprint & young age
    for shell_idx in shell_indices:
        df_companies.loc[shell_idx, 'entity_age_days'] = random.randint(10, 200)
        df_companies.loc[shell_idx, 'domain_age_days'] = df_companies.loc[shell_idx, 'entity_age_days'] - random.randint(0, 9)
        df_companies.loc[shell_idx, 'employee_mentions'] = random.randint(0, 3)
        df_companies.loc[shell_idx, 'credible_news_count'] = random.randint(0, 2)
        df_companies.loc[shell_idx, 'filings_per_year'] = round(random.uniform(0.1, 2), 2)

    # Save to CSV
    print("Saving data to CSV files...")
    df_companies.to_csv('../data/companies.csv', index=False)
    df_people.to_csv('../data/people.csv', index=False)
    df_addresses.to_csv('../data/addresses.csv', index=False)
    df_director_of.to_csv('../data/director_of.csv', index=False)
    df_registered_at.to_csv('../data/registered_at.csv', index=False)

    print("\nSynthetic data generation complete!")
    print(f"Generated {NUM_COMPANIES} companies, with {len(shell_indices)} marked as shells.")