import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY","JIRA")
if JIRA_PROJECT_KEY is None:
    raise ValueError("JIRA_PROJECT_KEY is not set in environment variables.")

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
    ticket_key = JIRA_PROJECT_KEY +"-"+ ticket_key
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

    summaryLimit = 50
    descriptionLimit = 210

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

        # Cleaning the result
        description = ' '.join(description.split())
        if len(description) > descriptionLimit:
            description = description[:descriptionLimit - 3] + '...'
        
        summary = ' '.join(summary.split())
        if len(summary) > summaryLimit:
            summary = summary[:summaryLimit - 3] + '...'
        
        createdDate = createdDate[:10]

        
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

