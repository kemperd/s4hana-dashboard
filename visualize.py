import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, column
from dotenv import load_dotenv
from urllib.parse import quote
import os
from llama_index import SQLDatabase
from llama_index.indices.struct_store import NLSQLTableQueryEngine
from io import StringIO
import pandas as pd

load_dotenv()
username = str(os.getenv('DB_USER'))
passwd = str(os.getenv('DB_PASS'))
hostname = str(os.getenv('DB_HOST'))
port = str(os.getenv('DB_PORT'))

engine = create_engine("hana+hdbcli://{}:{}@{}:{}".format(username, quote(passwd), hostname, port))

sql_database = SQLDatabase(engine, include_tables=['ekpo'])

def query(query_string):
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["ekpo"],
    )
    query_template = '''{}. 
        Present the output in CSV format with headers. 
        Do not generate SQL statements for exporting to CSV. 
        Do not provide additional descriptions apart from the data. 
        Always display a header row containing the column descriptions.
        '''.format(query_string)
    response = query_engine.query(query_template)
    return response

st.set_page_config(layout="wide")

col1, col2 = st.columns(2)

# Some examples of queries:
#
# - How many purchase orders are there?
# - Sum up the net value of purchase orders
# - Sum up the gross value of purchase orders
# = Sum up the gross value of purchase orders in 2022
# - Aggregate the net purchase order value by article, only display top 10'
# - Aggregate the net purchase order value by month in 2022

with col1:
    input = st.text_input('Enter query')
    if input:
        with st.spinner('Wait for it...'):
            response = query(input)
            df = pd.read_csv(StringIO(response.response))
            st.text(response.metadata['sql_query'])
            st.dataframe(df)
        with col2:
            # Only define X/Y axes when there are actually 2 columns to prevent error
            if len(df.columns) == 2:
                st.bar_chart(data=df, x=df.columns[0], y=df.columns[1])
            else:
                st.bar_chart(data=df)