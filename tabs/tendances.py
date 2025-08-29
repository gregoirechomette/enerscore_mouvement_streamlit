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

def plot_tendances(df_carte_identite, df_tendances):
    
    st.markdown("<p style='text-align: center;'>  Évolution de la consommation mensuelle moyenne des magasins en éléctricité au cours des 4 dernières années. Possibilité de choisir une SCA et une activité en particulier.</p>", unsafe_allow_html=True)
    st.text("")
    
    # Retrive the information about the magasin
    # df_tendances = pd.read_csv('data/consos_elec_gaz_mois_ready.csv')
    df_tendances['code_panonceau'] = df_tendances['code_panonceau'].astype(str).str.zfill(4)
    df_tendances['code_unique'] = df_tendances['code_panonceau'] + '_' + df_tendances['activite']
    df_tendances = df_tendances.merge(df_carte_identite[['code_unique', 'centrale']], on='code_unique', how='left')
    
    
    # Create the filters and slice the dataframe
    col1, col2 = st.columns([1, 1])
    with col1:
        filtre_sca = st.selectbox("Choisir une SCA",  ['Toutes les SCA'] + list(df_tendances.sort_values(by='centrale')['centrale'].unique()), label_visibility="collapsed", key='sca_selectbox_tendances')
    with col2:
        filtre_activite = st.selectbox("Choisir une activité", ['Toutes les activités'] + list(df_tendances.sort_values(by='activite')['activite'].unique()), label_visibility="collapsed", key='activite_selectbox_tendances')

    df_filtered = df_tendances.copy()
    if filtre_sca != 'Toutes les SCA':
        df_filtered = df_filtered[df_filtered['centrale'] == filtre_sca]
    if filtre_activite != 'Toutes les activités':
        df_filtered = df_filtered[df_filtered['activite'] == filtre_activite]
        
        
    # Compute statistics about consumptions
    df_tendances_stats = df_filtered.groupby(['date_mois']).agg({'conso_elec_kwh_m2': ['mean', 'std'], 'conso_gaz_kwh_m2': ['mean', 'std']}).reset_index()
    df_tendances_stats.columns = ['date_mois', 'conso_elec_kwh_m2_mean', 'conso_elec_kwh_m2_std', 'conso_gaz_kwh_m2_mean', 'conso_gaz_kwh_m2_std']
    df_tendances_stats['conso_elec_kwh_m2_mean'] = df_tendances_stats['conso_elec_kwh_m2_mean'].round(1)
    df_tendances_stats['conso_gaz_kwh_m2_mean'] = df_tendances_stats['conso_gaz_kwh_m2_mean'].round(1)
    df_tendances_stats = df_tendances_stats.sort_values(by=['date_mois'])


    # Create a new graph where we analyse the totla energy consumption, month by month, of the magasin compared to the whole set of magasins. In blue, the whole set has some opacity. Show also the moving average. Only gaz + elec, not other curves
    fig = go.Figure()

    # Plot the mean of all magasins, electricity
    fig.add_trace(go.Scatter(x=df_tendances_stats['date_mois'], y=df_tendances_stats['conso_elec_kwh_m2_mean'], mode='lines', line=dict(color='#005abb', width=2), opacity=0.9, name='Moyenne elec',  showlegend=True))
    fig.add_trace(go.Scatter(x=df_tendances_stats['date_mois'], y=(df_tendances_stats['conso_elec_kwh_m2_mean']).rolling(window=12).mean().round(1), mode='lines', line=dict(color='#005abb', width=2, dash='dash'), opacity=0.9, name='Moyenne glissante elec', showlegend=True))
    
    # Plot the mean of all magasins, gaz
    fig.add_trace(go.Scatter(x=df_tendances_stats['date_mois'], y=df_tendances_stats['conso_gaz_kwh_m2_mean'], mode='lines', line=dict(color='#f18e00', width=2), opacity=0.9, name='Moyenne gaz', showlegend=True))
    fig.add_trace(go.Scatter(x=df_tendances_stats['date_mois'], y=df_tendances_stats['conso_gaz_kwh_m2_mean'].rolling(window=12).mean().round(1), mode='lines', line=dict(color='#f18e00', width=2, dash='dash'), opacity=0.9, name='Moyenne glissante gaz', showlegend=True))
    
    
    # 1️⃣  guarantee datetime
    df_tendances_stats['date_mois']   = pd.to_datetime(df_tendances_stats['date_mois'])

    # Create rolling means for the selected activity
    stats_act = (df_tendances_stats.sort_values('date_mois').copy())
    stats_act['total_mean']       = stats_act['conso_elec_kwh_m2_mean']
    stats_act['total_mean_ma12']  = stats_act['total_mean'].rolling(12).mean()
    stats_act['gaz_mean_ma12']    = stats_act['conso_gaz_kwh_m2_mean'].rolling(12).mean()



    # Create some useful plotly functions to add arrows and labels
    def pct(prev, cur):
        if prev == 0 or prev is None or cur is None or isnan(prev) or isnan(cur):
            return None
        return 100 * (cur - prev) / prev

    def label(prev_y, this_y, delta):
        return f"{prev_y} à {this_y} : {delta:+.0f} %"  # thin NB-space before % to keep it tight

    def add_arrow(x, y, txt, color, ay):
        fig.add_annotation(x=x, y=y, text=txt, showarrow=True, arrowhead=2, arrowsize=1, arrowcolor=color, font=dict(color=color, size=11), ax=0, ay=ay,)



    # Loop over all years
    years = sorted(df_tendances_stats['date_mois'].dt.year.unique())
    for i in range(1, len(years)):
        y_prev, y_now = years[i-1], years[i]

        x_prev_glob  = stats_act.loc[stats_act['date_mois'].dt.year == y_prev, 'date_mois'].max()
        x_now_glob   = stats_act.loc[stats_act['date_mois'].dt.year == y_now,  'date_mois'].max()


        tot_prev = stats_act.loc[stats_act['date_mois'] == x_prev_glob, 'total_mean_ma12'].iloc[0]
        tot_now  = stats_act.loc[stats_act['date_mois'] == x_now_glob,  'total_mean_ma12'].iloc[0]
        gazg_prev = stats_act.loc[stats_act['date_mois'] == x_prev_glob, 'gaz_mean_ma12'].iloc[0]
        gazg_now  = stats_act.loc[stats_act['date_mois'] == x_now_glob,  'gaz_mean_ma12'].iloc[0]

        d_tot  = pct(tot_prev,  tot_now)
        d_gazg = pct(gazg_prev, gazg_now)

        if d_tot is not None:
            add_arrow(x_now_glob, tot_now, label(y_prev, y_now, d_tot), 'rgba(0,90,187,1)',  -70)
        if d_gazg is not None:
            add_arrow(x_now_glob, gazg_now, label(y_prev, y_now, d_gazg), 'rgba(241,142,0,1)', -70)

            
        
    # Update layout of the figure
    fig.update_xaxes(range=['2021-04-01', '2025-03-30'])
    fig.update_yaxes(range=[-5, max(df_tendances_stats['conso_elec_kwh_m2_mean'].max(), df_tendances_stats['conso_gaz_kwh_m2_mean'].max()) + 10])
    
    fig.update_layout(xaxis_title='Date',
                        yaxis_title='Consommation (kWh/m²)',
                        legend = dict(orientation='h', yanchor="top", y=1.05, xanchor="left", x=0.02),
                        height=500, width=2500,
                        margin=dict(l=0, r=0, t=40, b=0),
                        hovermode='x unified')
    
    st.plotly_chart(fig, key='tendances_globales', use_container_width=True)
    

    return