import boto3
import streamlit as st
from langchain_aws import BedrockLLM

# Function to initialize AWS Bedrock client
def get_bedrock_client():
    return boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

# Function to generate insights using AWS Bedrock
def generate_insights_with_bedrock(user_query, data):
    try:
        bedrock_client = get_bedrock_client()
        bedrock_llm = BedrockLLM(model_id="amazon.titan-text-premier-v1:0", client=bedrock_client)
        
        # Create a prompt to generate insights based on the queried data
        prompt = f"full reply to {user_query} : {data.to_string(index=False)}"
        response = bedrock_llm.invoke(prompt)
        return response
    except Exception as e:
        st.error(f"Failed to generate insights using Bedrock: {str(e)}")
        return None