import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import joblib
import numpy as np
import os

# Load the JIRA ticket data
df = pd.read_csv("jira_tickets_all.csv")

# Clean and fill missing values
df['Summary'] = df['Summary'].fillna('')
df['Description'] = df['Description'].fillna('')

# Combine summary and description
df['full_text'] = df['Summary'] + ' ' + df['Description']

# Load Sentence-BERT model (lightweight and accurate)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode the combined text into embeddings
print("Generating embeddings...")
embeddings = model.encode(df['full_text'].tolist(), show_progress_bar=True)

# Train a Nearest Neighbors model for similarity search
nn_model = NearestNeighbors(n_neighbors=5, metric='cosine')
nn_model.fit(embeddings)

# Save model and data
os.makedirs("models", exist_ok=True)
joblib.dump(nn_model, "models/nn_model.pkl")
joblib.dump(df, "models/ticket_data.pkl")
np.save("models/embeddings.npy", embeddings)

print("✅ Model training and saving complete.")
