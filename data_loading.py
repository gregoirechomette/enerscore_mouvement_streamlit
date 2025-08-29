import numpy as np
import pandas as pd
import streamlit as st

from google.cloud import bigquery
from google.oauth2 import service_account

# Create client API.
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)



@st.cache_data(ttl=1000)
def load_carte_identite(query):

    # Perform query
    query_job = client.query("SELECT * FROM " + query)
    rows_raw = query_job.result()

    # Extract data and store it to a dataframe
    rows = [dict(row) for row in rows_raw]
    df = pd.DataFrame(rows)

    # Change the format of code_panonceau and create full_name
    df['code_panonceau'] = df['code_panonceau'].astype(str).str.zfill(4)
    df['full_name'] = df['nom_compte'] + ' (' + df['code_panonceau'].astype(str) + ') - ' + df['activite'].astype(str) 
    df['code_unique'] = df['code_panonceau'] + '_' + df['activite']
    df['gaz_fraction'] = (100 * df['gaz_fraction']).round(1)

    # Sort the dataframe by code_panonceau
    df = df.sort_values(by=['code_panonceau', 'activite'])

    return df



@st.cache_data(ttl=1000)
def load_consos_data_some_codes(query, codes_for_query):
    
    # Perform query
    query_job = client.query("SELECT * FROM " + query + " WHERE code_panonceau IN (" + codes_for_query + ")")
    rows_raw = query_job.result()

    # Extract data and store it to a dataframe
    rows = [dict(row) for row in rows_raw]
    df = pd.DataFrame(rows)

    # Change the format of code_panonceau
    df['code_panonceau'] = df['code_panonceau'].astype(str).str.zfill(4)

    # Sort the dataframe
    dic_fr2en_jours = {'Lundi': 1, 'Mardi': 2, 'Mercredi': 3, 'Jeudi': 4, 'Vendredi': 5, 'Samedi': 6, 'Dimanche': 7}
    df['jour'] = df['clean_hour'].str.split(' ').str[0]
    df['jour'] = df['jour'].map(dic_fr2en_jours)
    df['heure'] = df['clean_hour'].str.split(' ').str[1].str.replace('h', '').astype(int)
    
    df['code_unique'] = df['code_panonceau'] + '_' + df['activite']

    # Sort the dataframe by day and hour
    df.sort_values(by=['jour', 'heure'], inplace=True)

    # Remove columns day and hour
    df.drop(columns=['jour', 'heure'], inplace=True)

    return df

@st.cache_data(ttl=1000)
def load_consos_data_all_codes(query):
    
    # Perform query
    query_job = client.query("SELECT * FROM " + query)
    rows_raw = query_job.result()

    # Extract data and store it to a dataframe
    rows = [dict(row) for row in rows_raw]
    df = pd.DataFrame(rows)

    # Change the format of code_panonceau
    df['code_panonceau'] = df['code_panonceau'].astype(str).str.zfill(4)
    
    df['code_unique'] = df['code_panonceau'] + '_' + df['activite']

    return df



@st.cache_data(ttl=1000)
def load_stats_consos(query):

    # Perform query
    query_job = client.query("SELECT * FROM " + query)
    rows_raw = query_job.result()

    # Extract data and store it to a dataframe
    rows = [dict(row) for row in rows_raw]
    df_stats_conso = pd.DataFrame(rows)

    return df_stats_conso