import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Setting relative paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_path = os.path.join(base_dir, 'models')

# Load saved assets
df = joblib.load(os.path.join(models_path,'ticket_data.pkl'))
embeddings = np.load(os.path.join(models_path,'embeddings.npy'))
nn_model = joblib.load(os.path.join(models_path,'nn_model.pkl'))
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to find similar tickets
def find_similar_tickets(ticket_key, top_k=2):
    ticketFound = True
    # Get the ticket's full text
    row = df[df['Key'] == ticket_key]
    if row.empty:
        ticketFound = False
        return [ticketFound]

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
        assignee = df.iloc[idx]['Assignee']
        status = df.iloc[idx]['Status']
        createdDate = df.iloc[idx]['Created Date']

        
        similar_tickets.append({
            'Key': key,
            'Similarity': round(similarity, 4),
            'Summary': summary,
            'Description': description,
            'Assignee': assignee,
            'Status': status,
            'Created Date': createdDate
        })

        if len(similar_tickets) == top_k:
            break

    return [ticketFound,similar_tickets]


