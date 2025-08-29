import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go



def big_numbers_nuage_points(df_base):

    st.markdown("<p style='text-align: center;'> Positionnement de la performance énergétique au m² de l\'ensemble des magasins du parc, sur une année. Evaluation par rapport à la moyenne nationale, et calcul des économies potentielles en se basant sur la performance du 20% des magasins les plus performants.</p>", unsafe_allow_html=True)
    st.text("")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        filtre_sca = st.selectbox("Choisir une SCA",  ['Toutes les SCA'] + list(df_base.sort_values(by='centrale')['centrale'].unique()), label_visibility="collapsed")
    with col2:
        filtre_activite = st.selectbox("Choisir une activité", ['Toutes les activités'] + list(df_base.sort_values(by='activite')['activite'].unique()), label_visibility="collapsed")


    df_filtered = df_base.copy()
    if filtre_sca != 'Toutes les SCA':
        df_filtered = df_filtered[df_filtered['centrale'] == filtre_sca]
    if filtre_activite != 'Toutes les activités':
        df_filtered = df_filtered[df_filtered['activite'] == filtre_activite]
        
    
    
    # Create columns
    col1_0, col1_1, col1_2, col1_3, col1_4 = st.columns([2,4,4,4,2])
    
    
    potentiel_economies_gwh_energie = round(0.001 * df_filtered['potentiel_economies_mwh_energie'].sum())
    potentiel_economies_meuros_energie = round(0.001 * df_filtered['potentiel_economies_keuros_energie'].sum(),1)
    potentiel_economies_ktC02_energie = round(0.001 * df_filtered['potentiel_economies_tC02_energie'].sum(),1)
    percent_value = round(-100 * potentiel_economies_gwh_energie / (0.001 * df_filtered['conso_energie_annee_retenue_mwh'].sum()))
    
    # Show the potential savings
    with col1_1:
        st.markdown(f"""
        <div style="text-align: center;">
            Économies ⚡ <br>
            <span style="font-size: 22px; font-weight: bold;">{potentiel_economies_gwh_energie} GWh/an</span><br>
            <span style="font-size: 14px; color: gray;">{percent_value} %</span>
        </div>
        """, unsafe_allow_html=True)

    with col1_2:
        st.markdown(f"""
        <div style="text-align: center;">
            Économies 💰 <br>
            <span style="font-size: 22px; font-weight: bold;">{potentiel_economies_meuros_energie} M€/an</span><br>
            <span style="font-size: 14px; color: gray;">{percent_value} %</span>
        </div>
        """, unsafe_allow_html=True)

    with col1_3:
        st.markdown(f"""
        <div style="text-align: center;">
            Économies 🌍 <br>
            <span style="font-size: 22px; font-weight: bold;">{potentiel_economies_ktC02_energie} ktCO2/an</span><br>
            <span style="font-size: 14px; color: gray;">{percent_value} %</span>
        </div>
        """, unsafe_allow_html=True)
            
    st.text("")
    st.text("")

    return filtre_sca, filtre_activite

def figure_nuage_points(df_base_magasins, seuil=0.2, col_y='conso_elec_mwh_par_m2_corrigee', filtre_sca='Toutes les SCA', filtre_activite='Toutes les activités'):


    col_y = 'conso_energie_annee_retenue_mwh_par_m2_corrigee'
    col_y_economies = 'potentiel_economies_mwh_energie'
    
    
    df_filtered = df_base_magasins.copy()
    if filtre_sca != 'Toutes les SCA':
        df_filtered = df_filtered[df_filtered['centrale'] == filtre_sca]
    if filtre_activite != 'Toutes les activités':
        df_filtered = df_filtered[df_filtered['activite'] == filtre_activite]

    # Calculate the quantile and mean
    quantile_value = df_filtered[col_y].quantile(seuil)
    mean_value = df_filtered[col_y].mean()

    
    # Create df_other_magasins with only the magasins that are not in df_filtered
    df_other_magasins = df_base_magasins[~df_base_magasins['code_unique'].isin(df_filtered['code_unique'].unique())]
    
    
    
    # Create an empty figure
    fig = go.Figure()

    # Add horizontal lines to the figure
    fig.add_hline(y=quantile_value, line_dash='dash', line_color='grey',
                annotation_text=f'Limite top 20%: {round(quantile_value, 2)} MWh/m²', annotation_position='top right')
    fig.add_hline(y=mean_value, line_dash='dash', line_color='grey',
                annotation_text=f'Moyenne: {round(mean_value, 2)} MWh/m²', annotation_position='top right')
    
    # Plot points for 'others'
    fig.add_trace(go.Scatter(
        x=df_other_magasins['surface_com_m2'],
        y=df_other_magasins[col_y],
        mode='markers',
        marker=dict(size=7, color='grey', opacity=0.2, line=dict(width=0.5, color='grey')),
        customdata=df_other_magasins[['full_name', 'centrale', 'surface_com_m2', col_y, col_y_economies]],
        name='Autres magasins',
        hovertemplate="<b>Nom du Compte</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface de vente [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Conso énergétique annuelle normalisée corrigée [MWh/m²]</b>: %{customdata[3]}<br>" \
                      "<b>Potentielles économies [MWh]</b>: %{customdata[4]}<br>"
    ))
    
    # Plot points for magasins filtrés
    fig.add_trace(go.Scatter(
        x=df_filtered['surface_com_m2'],
        y=df_filtered[col_y],
        mode='markers',
        marker=dict(size=8, color='#005abb', opacity=0.9, line=dict(width=0.5, color='grey')),
        customdata=df_filtered[['full_name', 'centrale', 'surface_com_m2', col_y, col_y_economies]],
        name='Magasins filtrés',
        hovertemplate="<b>Nom du Compte</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface de vente [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Conso énergétique annuelle normalisée corrigée [MWh/m²]</b>: %{customdata[3]}<br>" \
                      "<b>Potentielles économies [MWh]</b>: %{customdata[4]}<br>"
    ))

    
    
    # Update layout
    fig.update_layout(
        xaxis=dict(showgrid=True,gridcolor='LightPink',  gridwidth=1, title=dict(text='Surface de vente [m²]', font=dict(size=16))),
        yaxis=dict(showgrid=True,gridcolor='LightGray', gridwidth=1, title=dict(text='Consommation annuelle [MWh/m²][2]', font=dict(size=16))),
        height=500,
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
    fig.update_yaxes(range=[0, 1.2], gridcolor='lightgrey')
    
    st.plotly_chart(fig)

    return

def expander_nuage_points(euros_mwh, tCO2_gwh):

    with st.expander("Hypothèses"):
        st.write('[1] En suppposant que le magasin arrive à baisser sa consommation au niveau du top 20%, et avec des hypothèses d\'un prix de 162 €/MWh électrique, 121 €/MWh de gaz, un facteur d\'émission de 32 tCO2/GWh électrique et 227 tCO2/GWh pour le gaz. Pour arriver au niveau du top 20%, on suppose que le magasin baisse autant sa consommation electrique que sa consommation de gaz.')
        st.write('[2] Les consommations ont été corrigées pour prendre trois facteurs en considération: 1) la surface de vente: pour chaque chaque 1000 m² supplémentaire de surface de vente, la consommation énergétique diminue de 0.00005 [MWh/m²]; 2) le climat: pour chaque degré de température extérieure annuelle moyenne en plus, la consommation énergétique augmente de 0.005 [MWh/m²]; 3) l\'ouverture le dimanche: pour les magasins ouverts le dimanche, la consommation énergétique augmente en moyenne de 3%.')

    return