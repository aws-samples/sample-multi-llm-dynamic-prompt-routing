# Import required libraries
import json
import time
import boto3
import faiss
import numpy as np
import logging

# Initialize the logger to track execution and errors
logger = logging.getLogger()
logger.setLevel("INFO")

# Create a Bedrock Runtime client for accessing LLMs
client = boto3.client("bedrock-runtime")

# Load pre-trained FAISS index and corresponding category labels
# FAISS is used for efficient similarity search of embeddings
index = faiss.read_index("/opt/python/reference_index.faiss")
with open("/opt/python/reference_labels.json", "r") as f:
    labels = json.load(f)

def get_embedding(text):
    """
    Generate embedding vector for input text using Titan embedding model
    Args:
        text (str): The question text to generate embedding for
    Returns:
        numpy array: Embedding vector as float32 array
    """
    try:
        response = client.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": text})
        )
        embedding = json.loads(response["body"].read())["embedding"]
        return np.array(embedding).astype("float32")
    except Exception as e:
        print(f"Error in generating embedding for question: {str(e)}")
        raise

def classify_question(question):
    """
    Classify input question as either history or math using FAISS similarity search
    Args:
        question (str): The question text to classify
    Returns:
        str: Classification result - 'history', 'math', or 'unsure'
    """
    try:
        embedding = get_embedding(question)
        _, closest_match_idx = index.search(embedding.reshape(1, -1), 1)
        category = labels[closest_match_idx[0][0]]
        return category
    except Exception as e:
        print(f"Error in classifying question: {str(e)}")
        return "unsure"

def answer_question(question, model_id):
    """
    Generate answer to question using specified Claude model
    Args:
        question (str): The question to answer
        model_id (str): ID of Claude model to use
    Returns:
        str: Generated answer text
    Raises:
        Exception: If answer generation fails
    """
    
    prompt = f"You are an AI assistant to help students with their schools' math and history questions. Your role is to provide detailed information to improve students' understanding of the topic at hand. Keep your answer short and to the point. If the question is of any topic other than history or math, or if you don't know the answer to a question, just say you cannot answer the question. Now answer the following question:\n\n{question}\n\nAnswer:"
    
    request=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 128,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    })

    try:
        response = client.invoke_model(modelId=model_id, body=request)
        model_response = json.loads(response["body"].read())
        return model_response["content"][0]["text"]
    except Exception as e:
        print(f"Error in generating answer: {str(e)}")
        raise

def handler(event, context):

    # Start timing the full request
    start_time = time.time()
    
    try:
        # Extract question from request body
        question = json.loads(event['body'])['question']
 
        # Get question classification and timing
        classify_start = time.time()
        classification = classify_question(question)
        classify_time = time.time() - classify_start
    
        # Select appropriate model based on question type
        if classification == 'history':
            model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
        else:  # math or unsure
            model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    
        # Generate and time the answer
        answer_start = time.time()
        answer = answer_question(question, model_id)
        answer_time = time.time() - answer_start
        
        # Return successful response with answer and metadata
        return {
            'statusCode': 200,
            'body': json.dumps({
                'answer': answer,
                'question_classification': classification,
                'embedding_LLM': 'amazon.titan-embed-text-v2:0',
                'classification_time': classify_time,
                'answerer_LLM': model_id,
                'answer_generation_time': answer_time,
                'total_response_time': time.time() - start_time
            })
        }
    except Exception as e:
        # Log and return any errors that occur
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
