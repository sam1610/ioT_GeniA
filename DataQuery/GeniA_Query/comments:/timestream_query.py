import boto3
import pandas as pd
import streamlit as st
from botocore.exceptions import ClientError

# Function to initialize AWS TimeStream client
def get_timestream_client():
    """
    Initializes a TimeStream client object.

    Returns:
        boto3.client: A TimeStream client object.
    """
    return boto3.client('timestream-query', region_name='us-east-1')  # Using us-east-1 region

# Function to query data from AWS TimeStream
def query_timestream_data():
    """
    Queries data from the specified TimeStream database and table.

    Returns:
        dict: The response from the TimeStream query.
              Returns None if an error occurs.
    """
    query_string = """
    SELECT * FROM "ioTestDB"."ioTestTB" 
    """
    try:
        timestream_client = get_timestream_client()
        response = timestream_client.query(QueryString=query_string)
        return response
    except ClientError as e:
        st.error(f"Failed to query TimeStream: {e.response['Error']['Message']}")  # Display error message in Streamlit
        return None

# Function to convert TimeStream query response to DataFrame
def timestream_response_to_dataframe(response):
    """
    Converts the TimeStream query response to a Pandas DataFrame.

    Args:
        response (dict): The response from the TimeStream query.

    Returns:
        pandas.DataFrame: The data in a DataFrame format.
                          Returns an empty DataFrame if the response is None.
    """
    if response is None:
        return pd.DataFrame()
    
    columns = [column['Name'] for column in response['ColumnInfo']]  # Extract column names
    rows = []
    for row in response['Rows']:
        data = [col.get('ScalarValue', None) for col in row['Data']]  # Extract data from each row
        rows.append(data)
    
    df = pd.DataFrame(rows, columns=columns)  # Create DataFrame
    
    # Transpose the data to put measure names as features (if applicable)
    if 'measure_name' in df.columns and 'measure_value::varchar' in df.columns:
        df = df.pivot(index='time', columns='measure_name', values='measure_value::varchar').reset_index()
    
    return df