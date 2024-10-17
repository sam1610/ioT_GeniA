import streamlit as st
import boto3
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from botocore.exceptions import ClientError
  
# Function to initialize AWS TimeStream client
def get_timestream_client():
    return boto3.client('timestream-query', region_name='us-east-1')

# Function to query data from AWS TimeStream
def query_timestream_data():
    query_string = """
    SELECT * FROM "ioTestDB"."ioTestTB"
    """
    try:
        timestream_client = get_timestream_client()
        response = timestream_client.query(QueryString=query_string)
        return response
    except ClientError as e:
        st.error(f"Failed to query TimeStream: {e.response['Error']['Message']}")
        return None

# Function to convert TimeStream query response to DataFrame
def timestream_response_to_dataframe(response):
    if response is None:
        return pd.DataFrame()
    
    columns = [column['Name'] for column in response['ColumnInfo']]
    rows = []
    for row in response['Rows']:
        data = [col.get('ScalarValue', None) for col in row['Data']]
        rows.append(data)
    
    df = pd.DataFrame(rows, columns=columns)
    
    # Transpose the data to put measure names as features
    if 'measure_name' in df.columns and 'measure_value::varchar' in df.columns:
        df = df.pivot(index='time', columns='measure_name', values='measure_value::varchar').reset_index()
    
    return df
    
    columns = [column['Name'] for column in response['ColumnInfo']]
    rows = []
    for row in response['Rows']:
        data = [col.get('ScalarValue', None) for col in row['Data']]
        rows.append(data)
    
    df = pd.DataFrame(rows, columns=columns)
    return df

# Streamlit app to display AWS TimeStream data
def timestream_app():
    st.title("AWS TimeStream Data Viewer")

    # Query data from AWS TimeStream
    response = query_timestream_data()
    df = timestream_response_to_dataframe(response)

    if df.empty:
        st.warning("No data found in TimeStream table.")
    else:
        # Configure AgGrid to display the data
        st.subheader("TimeStream Data Table")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=False, groupable=True)
        gb.configure_selection('single', use_checkbox=True)
        grid_options = gb.build()

        AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            fit_columns_on_grid_load=True,
            height=400,
            width='100%'
        )

if __name__ == "__main__":
    timestream_app()