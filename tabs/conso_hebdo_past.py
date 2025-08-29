import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


# def plot_conso_hebdo(df_consos_all, df_base, df_stats_dimanche_ouvert, df_stats_dimanche_ferme, code_panonceau=104, magasins_comparatifs=[101,103], color_mean='blue', color_filled='blue'):
def plot_conso_hebdo(df_consos_stats, df_carte_identite):

    st.write(" ")
    st.markdown("<p style='text-align: center;'> Profil des consommations électriques de l'ensemble des magasins sur des semaines moyennes.  Possibilité de choisir le mois et un sous-ensemble des activités (HYPER, SUPER, EXPRESS).</p>", unsafe_allow_html=True)
    st.write(" ")
    
    
    # Define the options for the month
    options_mois_2 = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    # Create two columns
    col1, col_1_5, col2 = st.columns([4, 1, 4])
    
    with col1:
        # Provide a slider to select the month
        mois = st.select_slider("Sélectionner le mois", options=options_mois_2, value=('Janvier'), label_visibility='collapsed', key='mois_select_slider_autocomparaison')
    with col2:

        # Filter by activity
        filtre_activite = st.selectbox("Choisir une activité", ['Toutes les activités'] + list(df_carte_identite.sort_values(by='activite')['activite'].unique()), label_visibility="collapsed", key='activite_selectbox_autocomparaison')
    
    df_filtered = df_consos_stats.copy()
    surf_totale = df_carte_identite['surface_com_m2'].sum()
    if filtre_activite != 'Toutes les activités':
        df_filtered = df_filtered[df_filtered['activite'] == filtre_activite]
        surf_totale = df_carte_identite[df_carte_identite['activite'] == filtre_activite]['surface_com_m2'].sum()
        
        
    # Filter the dataframe to keep only the month
    df_consos_stats = df_filtered[df_filtered['clean_month'].str.contains(mois)]
    df_consos_stats = df_consos_stats.groupby(['clean_month', 'clean_hour'], as_index=False).agg({'p_w_m2_mean': 'mean'})
    
    # Donnees pour chaque année
    df_consos_stats_2021 = df_consos_stats[df_consos_stats['clean_month'].str.contains('2021')]
    df_consos_stats_2022 = df_consos_stats[df_consos_stats['clean_month'].str.contains('2022')]
    df_consos_stats_2023 = df_consos_stats[df_consos_stats['clean_month'].str.contains('2023')]
    df_consos_stats_2024 = df_consos_stats[df_consos_stats['clean_month'].str.contains('2024')]
    df_consos_stats_2025 = df_consos_stats[df_consos_stats['clean_month'].str.contains('2025')]
    
    # Order conso weekly
    df_consos_stats_2021 = order_df_consos_weekly(df_consos_stats_2021)
    df_consos_stats_2022 = order_df_consos_weekly(df_consos_stats_2022)
    df_consos_stats_2023 = order_df_consos_weekly(df_consos_stats_2023)
    df_consos_stats_2024 = order_df_consos_weekly(df_consos_stats_2024)
    df_consos_stats_2025 = order_df_consos_weekly(df_consos_stats_2025) 
    
     
    
    

    # Just define a px plot, add things later only with fig.add_scatter
    fig = px.scatter()
    fig.add_scatter(x=df_consos_stats_2021['clean_hour'], y=round(surf_totale * 1e-6 * df_consos_stats_2021['p_w_m2_mean'],1), mode='lines', name='2021', line=dict(color="#ad0d0d", width=2))
    fig.add_scatter(x=df_consos_stats_2022['clean_hour'], y=round(surf_totale * 1e-6 * df_consos_stats_2022['p_w_m2_mean'],1), mode='lines', name='2022', line=dict(color="#C76969", width=2))
    fig.add_scatter(x=df_consos_stats_2023['clean_hour'], y=round(surf_totale * 1e-6 * df_consos_stats_2023['p_w_m2_mean'],1), mode='lines', name='2023', line=dict(color="#b1baf6", width=2))
    fig.add_scatter(x=df_consos_stats_2024['clean_hour'], y=round(surf_totale * 1e-6 * df_consos_stats_2024['p_w_m2_mean'],1), mode='lines', name='2024', line=dict(color='#005abb', width=2))
    fig.add_scatter(x=df_consos_stats_2025['clean_hour'], y=round(surf_totale * 1e-6 * df_consos_stats_2025['p_w_m2_mean'],1), mode='lines', name='2025', line=dict(color="#040931", width=2))

    fig.update_xaxes(title_text=" ", title_font=dict(size=12), showticklabels=True, tickfont=dict(size=16), 
                     ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                     tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'], side='bottom')


    # Define the y limits
    y_max = max(df_consos_stats_2021['p_w_m2_mean'].max(), df_consos_stats_2022['p_w_m2_mean'].max())
    fig.update_yaxes(range=[0, 1.2 * 1e-6 * surf_totale * y_max], title='Puissance [MW]')
    
    # Update layout
    fig.update_layout(title=' ', title_x=0.5, height=500, showlegend=True, margin=dict(l=20, r=20, t=60, b=20),
                      legend=dict(orientation='h', yanchor="top", y=1.05, xanchor="right", x=0.99), hovermode='x unified')
    
    st.plotly_chart(fig)

    return


def order_df_consos_weekly(df_raw):

    df = df_raw.copy()

    # Sort the dataframe
    dic_fr2en_jours = {'Lundi': 1, 'Mardi': 2, 'Mercredi': 3, 'Jeudi': 4, 'Vendredi': 5, 'Samedi': 6, 'Dimanche': 7}
    df['jour'] = df['clean_hour'].str.split(' ').str[0]
    df['jour'] = df['jour'].map(dic_fr2en_jours)
    df['heure'] = df['clean_hour'].str.split(' ').str[1].str.replace('h', '').astype(int)

    # Sort the dataframe by day and hour
    df.sort_values(by=['jour', 'heure'], inplace=True)
    
    return df