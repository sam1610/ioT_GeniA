import streamlit as st
import boto3
import json

# --- AWS Configuration ---
AWS_REGION = "us-east-1"
LAMBDA_FUNCTION_NAME = "LmbdBedrock"  # Replace with your Lambda function name
BEDROCK_MODEL_ID = "amazon.titan-embed-text-v1"  # For embeddings

# --- Initialize Bedrock client ---
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# --- Initialize Lambda client ---
lambda_client = boto3.client("lambda", region_name=AWS_REGION)

# --- Streamlit App ---
st.title("IoT Data Q&A with AWS Bedrock")

# User query
query = st.text_input("Ask a question about your IoT data:")
if query:
    # Invoke the Lambda function
    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps({"query": query})
        )

        # Parse the response
        response_payload = json.loads(response["Payload"].read().decode("utf-8"))
        if "body" in response_payload:
            llm_response = response_payload["body"]
            st.write(llm_response)  # Display the LLM response
        else:
            st.error(f"Error from Lambda function: {response_payload.get('error')}")

    except Exception as e:
        st.error(f"Error invoking Lambda function: {e}")