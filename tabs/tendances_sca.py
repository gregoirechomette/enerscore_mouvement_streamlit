import numpy as np
import pandas as pd

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go

import math
from math import isnan


# Create a function to plot the evolution of the consumption of a store in a monthly basis

def plot_tendances_sca(df_carte_identite):
    
    st.markdown("<p style='text-align: center;'>  Comparaison des SCAs selon leurs consommations d'énergie (éléctricité + gaz) mensuelles moyennes au cours des 4 dernières années.</p>", unsafe_allow_html=True)
    st.text("")
    
    # Retrive the information about the magasin
    df_tendances = pd.read_csv('data/consos_elec_gaz_mois_ready.csv')
    df_tendances['code_panonceau'] = df_tendances['code_panonceau'].astype(str).str.zfill(4)
    df_tendances['code_unique'] = df_tendances['code_panonceau'] + '_' + df_tendances['activite']
    df_tendances = df_tendances.merge(df_carte_identite[['code_unique', 'centrale']], on='code_unique', how='left')
        
    # Compute statistics about consumptions
    df_tendances_stats = df_tendances.groupby(['centrale', 'date_mois']).agg({'conso_elec_kwh_m2': ['mean', 'std'], 'conso_gaz_kwh_m2': ['mean', 'std']}).reset_index()
    df_tendances_stats.columns = ['centrale', 'date_mois', 'conso_elec_kwh_m2_mean', 'conso_elec_kwh_m2_std', 'conso_gaz_kwh_m2_mean', 'conso_gaz_kwh_m2_std']
    df_tendances_stats['conso_totale_kwh_m2_mean'] = df_tendances_stats['conso_elec_kwh_m2_mean'] + df_tendances_stats['conso_gaz_kwh_m2_mean'].round(1)
    df_tendances_stats = df_tendances_stats.sort_values(by=['centrale', 'date_mois'])
    df_tendances_stats['date_mois']   = pd.to_datetime(df_tendances_stats['date_mois'])
    


    # Plot for each SCA, using the rolling mean of the last 12 months
    fig = go.Figure()
    
    for centrale in df_tendances_stats.groupby(by=['centrale'], as_index=False).agg({'conso_totale_kwh_m2_mean':'mean'}).sort_values(by='conso_totale_kwh_m2_mean', ascending=False)['centrale'].unique():
        
        df_centrale = df_tendances_stats[df_tendances_stats['centrale'] == centrale].sort_values(by='date_mois')
        fig.add_trace(go.Scatter(x=df_centrale['date_mois'], y=(df_centrale['conso_totale_kwh_m2_mean']).rolling(window=12).mean().round(1), mode='lines', line=dict(width=2), opacity=0.9, name=f'{centrale}',  showlegend=True))

        
    # Update layout of the figure
    fig.update_xaxes(range=['2022-01-01', '2025-03-30'])
    fig.update_yaxes(range=[25,65])
    
    fig.update_layout(xaxis_title='Date',
                        yaxis_title='Consommation (kWh/m²)',
                        legend = dict(orientation='v', yanchor="top", y=0.85, xanchor="left", x=1.02),
                        height=500, width=2500,
                        margin=dict(l=0, r=0, t=40, b=0))
    
    st.plotly_chart(fig, key='tendances_globales_comp', use_container_width=True)
    

    return