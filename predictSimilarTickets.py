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

    similar_tickets = []
    for idx, dist in zip(indices[0], distances[0]):
        key = df.iloc[idx]['Key']
        if key == ticket_key:
            continue  # skip the query ticket itself

        similarity = 1 - dist  # cosine similarity = 1 - cosine distance
        summary = df.iloc[idx]['Summary']
        description = df.iloc[idx]['Description']
        
        similar_tickets.append({
            'Key': key,
            'Similarity': round(similarity, 4),
            'Summary': summary,
            'Description': description
        })

        if len(similar_tickets) == top_k:
            break

    return similar_tickets

# 🔍 Example: find top 2 tickets similar to ticket 'SH-5646'
result = find_similar_tickets("SH-5700", top_k=5)
for i in result :
    for key in i :
        print(key," : ",i[key])
    print('\n')
