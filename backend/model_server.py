import pandas as pd
import lightgbm as lgb
import shap
import joblib
import os
import networkx as nx # Added as feature_engineering uses it

# --- Content from feature_engineering.py ---
FEATURE_NAMES = [
    'shared_addr_count', 'director_entity_count', 'entity_age_days',
    'filings_per_year', 'employee_mentions', 'domain_age_days',
    'credible_news_count', 'has_cycle_len_4'
]

def get_company_features(G, company_id):
    """Computes features for a single company."""
    features = {}
    company_node = G.nodes[company_id]

    # 1. Shared Address Count
    shared_addr_count = 0
    for neighbor in G.neighbors(company_id):
        if G.nodes[neighbor]['type'] == 'address':
            # Count other companies at the same address
            shared_addr_count += G.degree(neighbor) - 1
    features['shared_addr_count'] = shared_addr_count

    # 2. Director Entity Count (avg number of companies per director)
    director_degrees = []
    for neighbor in G.neighbors(company_id):
        if G.nodes[neighbor]['type'] == 'person':
            director_degrees.append(G.degree(neighbor))
    features['director_entity_count'] = sum(director_degrees) / len(director_degrees) if director_degrees else 0

    # 3. Identity & Web Footprint Features (from node attributes)
    features['entity_age_days'] = company_node.get('entity_age_days', 0)
    features['filings_per_year'] = company_node.get('filings_per_year', 0)
    features['employee_mentions'] = company_node.get('employee_mentions', 0)
    features['domain_age_days'] = company_node.get('domain_age_days', 0)
    features['credible_news_count'] = company_node.get('credible_news_count', 0)

    # 4. Ownership Cycles
    has_cycle = 0
    try:
        # Check for cycles of length up to 4 involving the company node
        for cycle in nx.cycle_basis(G.subgraph(nx.ego_graph(G, company_id, radius=2))):
            if len(cycle) <= 4 and company_id in cycle:
                has_cycle = 1
                break
    except nx.NetworkXError: # ego_graph can fail on isolates
        has_cycle = 0
    features['has_cycle_len_4'] = has_cycle

    return pd.Series(features, index=FEATURE_NAMES)
# --- End of Content from feature_engineering.py ---


MODEL_PATH = 'lgbm_shell_model.pkl'

class ModelServer:
    def __init__(self, G):
        self.G = G
        # Adjust path to data if necessary, based on the new Python path context
        self.companies_df = pd.read_csv('../data/companies.csv')
        self.model = None
        self.explainer = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        if os.path.exists(MODEL_PATH):
            print("Loading pre-trained model...")
            self.model = joblib.load(MODEL_PATH)
        else:
            print("No pre-trained model found. Training a new one...")
            X = self.companies_df['company_id'].apply(lambda cid: get_company_features(self.G, cid))
            y = self.companies_df['is_shell']

            self.model = lgb.LGBMClassifier(objective='binary', random_state=42)
            self.model.fit(X, y)
            joblib.dump(self.model, MODEL_PATH)
            print(f"Model trained and saved to {MODEL_PATH}")

        self.explainer = shap.TreeExplainer(self.model)

    def predict(self, company_id):
        features = get_company_features(self.G, company_id).to_frame().T

        proba = self.model.predict_proba(features)[0, 1]
        score = int(proba * 100)

        if score > 60: verdict = "High Risk"
        elif 30 <= score <= 60: verdict = "Medium Risk"
        else: verdict = "Low Risk"

        shap_vals = self.explainer.shap_values(features)
        if isinstance(shap_vals, list):
            shap_values = shap_vals[0]   # works for binary or multiclass
        else:
            shap_values = shap_vals
        reasons = self._shap_to_reasons(features.iloc[0], shap_values[0])

        return {"score": score, "verdict": verdict, "reasons": reasons}

    def _shap_to_reasons(self, features, shap_values):
        reason_map = {
            'shared_addr_count': "Shares a registered address with {} other firms.",
            'director_entity_count': "Directors are associated with an average of {:.1f} other entities.",
            'entity_age_days': "Company is unusually young ({} days old).",
            'domain_age_days': "Website domain is very new ({} days old).",
            'employee_mentions': "Has a very low web footprint ({} employee mentions).",
            'credible_news_count': "Lacks mentions in credible news sources ({} found).",
            'has_cycle_len_4': "Detected a potential ownership cycle."
        }

        # Get top 3 features contributing to risk
        shap_df = pd.DataFrame({'feature': FEATURE_NAMES, 'shap': shap_values, 'value': features.values})
        shap_df = shap_df.sort_values(by='shap', ascending=False).head(3)

        reasons = []
        for _, row in shap_df.iterrows():
            if row['shap'] > 0.05: # Only include reasons with significant impact
                template = reason_map.get(row['feature'])
                if template:
                    if "{}" in template:
                        reasons.append(template.format(row['value']))
                    else:
                        if row['value'] > 0: # For binary flags like cycles
                            reasons.append(template)

        return reasons if reasons else ["No significant risk factors identified."]