import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go



def big_numbers_nuage_points(df_base_magasins):

    st.markdown("<p style='text-align: center;'> Positionnement de la fraction de gaz dans le mix énergétique de mon centre E.Leclerc par rapport aux autres magasins de ma SCA et de l\'ensemble des magasins du parc, sur une année. Evaluation par rapport à la moyenne nationale.</p>", unsafe_allow_html=True)
    st.text("")

    col1, col2 = st.columns([1, 1])
    with col1:
        filtre_sca = st.selectbox("Choisir une SCA",  ['Toutes les SCA'] + list(df_base_magasins.sort_values(by='centrale')['centrale'].unique()), label_visibility="collapsed", key='sca_selectbox')
    with col2:
        filtre_activite = st.selectbox("Choisir une activité", ['Toutes les activités'] + list(df_base_magasins.sort_values(by='activite')['activite'].unique()), label_visibility="collapsed", key='activite_selectbox')

    
    df_filtered = df_base_magasins.copy()
    if filtre_sca != 'Toutes les SCA':
        df_filtered = df_filtered[df_filtered['centrale'] == filtre_sca]
    if filtre_activite != 'Toutes les activités':
        df_filtered = df_filtered[df_filtered['activite'] == filtre_activite]
        
    

    col1_0, col1_1, col1_2, col1_3, col1_4 = st.columns([2,4,4,4,2])

    # Retrieve information about gaz
    fraction_gaz = round(df_filtered['gaz_fraction'].mean())
    consommation_gaz_gwh = round(0.001 * df_filtered['conso_gaz_annee_retenue_mwh'].sum())
    emissions_gaz_ktco2 = round(0.001 * 0.001 * 227 * df_filtered['conso_gaz_annee_retenue_mwh'].sum())
    
    # Show some indicators
    with col1_1:
        st.markdown(f"""
                <div style="text-align: center;">
                    Fraction de gaz (🛢️ vs ⚡)  <br>
                    <span style="font-size: 22px; font-weight: bold;">{fraction_gaz} %</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col1_2:
        st.markdown(f"""
                <div style="text-align: center;">
                    Consommation de gaz 🔥  <br>
                    <span style="font-size: 22px; font-weight: bold;">{consommation_gaz_gwh} GWh</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col1_3:
        st.markdown(f"""
                <div style="text-align: center;">
                    Émissions liées au gaz 🌍  <br>
                    <span style="font-size: 22px; font-weight: bold;">{emissions_gaz_ktco2} ktCO2</span><br>
                </div>
                """, unsafe_allow_html=True)
        

    st.text("")
    return filtre_sca, filtre_activite

def figure_nuage_points(df_base_magasins, seuil=0.2, code_principal_unique=104, codes_comparatifs_uniques=[101,103], filtre_sca = 'Toutes les SCA', filtre_activite='Toutes les activités'):

    
    df_filtered = df_base_magasins.copy()
    if filtre_sca != 'Toutes les SCA':
        df_filtered = df_filtered[df_filtered['centrale'] == filtre_sca]
    if filtre_activite != 'Toutes les activités':
        df_filtered = df_filtered[df_filtered['activite'] == filtre_activite]
    
    
    # Pick the appropriate column
    col_y = 'gaz_fraction'
    
    # Create an empty figure
    fig = go.Figure()
    

    fig.add_hline(y=df_filtered[col_y].mean(), line_dash='dash', line_color='grey',
                  annotation_text=f'Moyenne: {round(df_filtered[col_y].mean(), 1)} %', annotation_position='top right')
    
    
    
    # Create df_other_magasins with only the magasins that are not in df_filtered
    df_other_magasins = df_base_magasins[~df_base_magasins['code_unique'].isin(df_filtered['code_unique'].unique())]
    
    # Plot points for 'others'
    fig.add_trace(go.Scatter(
        x=df_other_magasins['surface_com_m2'],
        y=df_other_magasins[col_y],
        mode='markers',
        marker=dict(size=7, color='grey', opacity=0.2, line=dict(width=0.5, color='grey')),
        customdata=df_other_magasins[['full_name', 'centrale', 'surface_com_m2', col_y]],
        name='Autres magasins',
        hovertemplate="<b>Nom du Compte</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface de vente [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Fraction de gaz dans le mix énergétique (%)</b>: %{customdata[3]}<br>" 
    ))
    
    # Plot points for 'SCA'
    fig.add_trace(go.Scatter(
        x=df_filtered['surface_com_m2'],
        y=df_filtered[col_y],
        mode='markers',
        marker=dict(size=8, color='#005abb', opacity=0.9, line=dict(width=0.5, color='grey')),
        customdata=df_filtered[['full_name', 'centrale', 'surface_com_m2', col_y]],
        name='Magasins filtrés',
        hovertemplate="<b>Nom du Compte</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface de vente [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Fraction de gaz dans le mix énergétique (%)</b>: %{customdata[3]}<br>" 
    ))

    
    # Update layout
    fig.update_layout(
        xaxis=dict(showgrid=True,gridcolor='LightPink',  gridwidth=1, title=dict(text='Surface de vente [m²]', font=dict(size=16))),
        yaxis=dict(showgrid=True,gridcolor='LightGray', gridwidth=1, title=dict(text='Fraction de gaz dans le mix énergétique [%]', font=dict(size=16))),
        height=550,
        margin=dict(l=20, r=20, t=0, b=100),
        plot_bgcolor='#F6F6F6',
        legend=dict(orientation="v", xanchor='right', x=1.0, y=0.9, font=dict(size=14)),
        hovermode='closest',
        coloraxis_colorbar=dict(title='Économies annuelles potentielles [GWh]', xanchor='right', x=1.15),
        legend_traceorder="reversed",
    )
    
    # Add annotation for horizontal legend
    fig.add_annotation(dict(font=dict(color="black", size=12),
                            x=1.06, y=0.5, showarrow=False,
                            text='Économies annuelles potentielles [GWh]', textangle=-90,
                            xref="paper", yref="paper", font_size=15))
    
    fig.update_coloraxes(colorscale='Reds')
    
    # Setting the y-axis range
    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(range=[-5, 55], gridcolor='lightgrey')

    st.plotly_chart(fig)

    return
