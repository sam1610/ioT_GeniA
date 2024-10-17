import json
import boto3
from langchain.llms import Bedrock
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.docstore.document import Document

# --- AWS Configuration ---
AWS_REGION = "us-east-1" 
TIMESTREAM_DATABASE_NAME = "ioTestDB"  
TIMESTREAM_TABLE_NAME = "ioTestTB"  
BEDROCK_MODEL_ID = "amazon.titan-embed-text-v1"

# --- Initialize Bedrock clients ---
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
embeddings = BedrockEmbeddings(client=bedrock_client, model_id=BEDROCK_MODEL_ID)
llm = Bedrock(client=bedrock_client, model_id="amazon.titan-text-express-v1")

# --- Function to query TimeStream ---
def query_timestream(query_string):
    timestream_client = boto3.client("timestream-query", region_name=AWS_REGION)
    try:
        response = timestream_client.query(QueryString=query_string)
        return response['Rows']
    except Exception as e:
        print(f"Error querying TimeStream: {e}")
        return None

# --- Lambda handler ---
def lambda_handler(event, context):
    user_query = event.get("query", "")

    if user_query:
        # Construct TimeStream query (Adapt this based on your data and user query)
        ts_query = f"""
            SELECT time, measure_value::double AS temperature 
            FROM "{TIMESTREAM_DATABASE_NAME}"."{TIMESTREAM_TABLE_NAME}" 
            WHERE measure_name = 'temperature' 
            AND time BETWEEN ago(100d) AND now() 
        """

        ts_data = query_timestream(ts_query)

        if ts_data:
            # Format data for LangChain (Adapt this based on your needs)
            docs = []
            for row in ts_data:
                if 'Data' in row and len(row['Data']) > 0:
                    try:
                        doc = Document(
                            page_content=json.dumps(row['Data']),
                            metadata={"time": row['Data'][0]['ScalarValue']}
                        )
                        docs.append(doc)
                    except (KeyError, IndexError) as e:
                        print(f"Error creating document from row: {row}, Error: {e}")
                else:
                    print(f"Skipping row with missing or empty 'Data': {row}")

            if docs:
                # Create FAISS index
                vectorstore = FAISS.from_documents(docs, embeddings)

                # Use RetrievalQAWithSourcesChain to get sources
                chain = RetrievalQAWithSourcesChain.from_chain_type(
                    llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever()
                )
                response = chain.run(user_query)

                return {
                    "statusCode": 200,
                    "body": json.dumps(response)
                }
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": "No valid documents created from TimeStream data"})
                }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Error querying TimeStream or no data returned"})
            }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing query parameter"})
        }