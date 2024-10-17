import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from timestream_query import query_timestream_data, timestream_response_to_dataframe
from bedrock_insights import generate_insights_with_bedrock

# Streamlit app to display AWS TimeStream data
def timestream_app():
    st.title("AWS TimeStream Data Viewer")

    # Query data from AWS TimeStream
    response = query_timestream_data()
    df = timestream_response_to_dataframe(response)

    if df.empty:
        st.warning("No data found in TimeStream table.")
    else:
        # Generate insights using AWS Bedrock
        st.subheader("Generated Insights from Bedrock")
        insights = generate_insights_with_bedrock(df)
        if insights:
            st.markdown(f"**{insights}**")
        else:
            st.warning("No insights could be generated.")
        
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