# Import required libraries
import json
import boto3
import numpy as np
import faiss

# Initialize AWS Bedrock client for accessing embedding model
client = boto3.client('bedrock-runtime')  

# Define reference prompts organized by category (history and math)
# These will be used as the reference set for similarity matching
questions = {
    "history": [
        "What were the main causes of World War I?",
        "What region of the United States saw the largest economic growth as a result of the Industrial Revolution?",
        "Who was the first man on the moon?",
        "What country gifted the United States with the Statue of Liberty?",
        "What major event sparked the beginning of the Great Depression in 1929?"
    ],
    "math": [
        "Solve the quadratic equation: 2x^2 + 5x - 12 = 0",
        "Find the derivative of f(x) = 3x^4 - 2x^3 + 5x - 7",
        "In a right triangle, if one angle is 30° and the hypotenuse is 10 cm, find the lengths of the other two sides.",
        "Determine the area of the region bounded by y = x^2, y = 4, and the y-axis.",
        "If log_2(x) + log_2(y) = 5 and xy = 64, find the values of x and y."
    ]
}

def get_embedding(text):
    """
    Generate vector embedding for input text using Amazon Titan embedding model
    Args:
        text (str): Input text to generate embedding for
    Returns:
        numpy.array: Vector embedding as float32 array
    """
    response = client.invoke_model(
        modelId='amazon.titan-embed-text-v2:0',
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": text})
    )
    embedding = json.loads(response['body'].read())['embedding']
    return np.array(embedding).astype('float32')

# Initialize empty lists to store embeddings and their corresponding category labels
embeddings = []
labels = []

# Generate embeddings for each question and store with its category label
for category, category_questions in questions.items():
    for question in category_questions:
        embedding = get_embedding(question)
        embeddings.append(embedding)
        labels.append(category)

# Convert embeddings list to numpy array for FAISS indexing
embeddings = np.array(embeddings)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Save the FAISS index and category labels 
faiss.write_index(index, 'reference_index.faiss')
with open('reference_labels.json', 'w') as f:
    json.dump(labels, f)

print("Embeddings generated and saved successfully.")
