import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# Load saved assets
df = joblib.load("models/ticket_data.pkl")
embeddings = np.load("models/embeddings.npy")
nn_model = joblib.load("models/nn_model.pkl")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to find similar tickets
def find_similar_tickets(ticket_key, top_k=2):
    # Get the ticket's full text
    row = df[df['Key'] == ticket_key]
    if row.empty:
        return f"Ticket {ticket_key} not found."

    query_text = row['full_text'].values[0]
    
    # Embed the query ticket
    query_embedding = model.encode([query_text])

    # Find top K most similar tickets (excluding the query ticket itself)
    distances, indices = nn_model.kneighbors(query_embedding, n_neighbors=top_k + 1)

    similar_indices = indices[0]
    similar_keys = df.iloc[similar_indices]['Key'].tolist()
    
    # Remove the original ticket from the results
    similar_keys = [key for key in similar_keys if key != ticket_key][:top_k]
    
    return df[df['Key'].isin(similar_keys)][['Key', 'Summary', 'Description']]

# 🔍 Example: find top 2 tickets similar to ticket 'SH-5646'
result = find_similar_tickets("SH-5646", top_k=2)
print(result)
