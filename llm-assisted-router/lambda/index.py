# Import required libraries
import json
import time
import boto3
import logging

# Initialize the logger to track execution and errors
logger = logging.getLogger()
logger.setLevel("INFO")

# Create a Bedrock Runtime client for accessing LLMs
client = boto3.client('bedrock-runtime')

def classify_question(question):
    """
    Classifies an input question as either history or math using Titan model
    Args:
        question (str): The question text to classify
    Returns:
        str: Classification result - 'history', 'math', or 'unsure'
    """
    
    prompt = f"Classify the following question as either 'history' or 'math'. If unsure, classify as 'unsure':\n{question}\nClassification:"
    model_id = 'amazon.titan-text-express-v1'
    request=json.dumps({
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 10,
            "stopSequences": [],
            "temperature": 0.1,
            "topP": 1
        },
    })
    try:
        response = client.invoke_model(modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=request,
        )
        classifier_response = json.loads(response['body'].read())  
        return classifier_response["results"][0]["outputText"].lower().strip()
    except Exception as e:
        logger.error(f"Failed to classify question: {str(e)}")
        return "unsure"

def answer_question(question, model_id):
    """
    Generates an answer to the question using specified Claude model
    Args:
        question (str): The question to answer
        model_id (str): ID of the Claude model to use
    Returns:
        str: Generated answer text
    Raises:
        Exception: If answer generation fails
    """

    prompt = f"You are an AI assistant to help students with their schools' math and history questions. Your role is to provide detailed information to improve students' understanding of the topic at hand. Keep your answer short and to the point. If the question is of any topic other than history or math, or if you don't know the answer to a question, just say you cannot answer the question. Now answer the following question:\n\n{question}\n\nAnswer:"
    
    request=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 128,
        "temperature": 0.5,
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
        logger.error(f"Failed to generate answer: {str(e)}")
        raise

def handler(event, context):

    # Start timing the full request
    start_time = time.time()
    
    try:
        # Extract the question from the request body
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
                'classifier_LLM': 'amazon.titan-text-express-v1',
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
