import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

import plotly.express as px
import plotly.graph_objects as go

import matplotlib
import pydeck as pdk

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm


def resume(df_base):
    
    st.markdown("<h4 style='text-align: center;'>Nombre de magasins par activité</h4>", unsafe_allow_html=True)
    st.text("")
    
    # Create three metrics 
    col1, col2, col3, col4  = st.columns(4)
    # Give numbers about the perimeter
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            Nombre de magasins <br>
            <span style="font-size: 22px; font-weight: bold;">{df_base.shape[0]} </span><br>
        </div>
        """, unsafe_allow_html=True)    
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            Nombre de HYPER <br>
            <span style="font-size: 22px; font-weight: bold;">{df_base[df_base['activite'] == 'HYPER'].shape[0]} </span><br>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            Nombre de SUPER <br>
            <span style="font-size: 22px; font-weight: bold;">{df_base[df_base['activite'] == 'SUPER'].shape[0]} </span><br>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="text-align: center;">
            Nombre d'EXPRESS <br>
            <span style="font-size: 22px; font-weight: bold;">{df_base[df_base['activite'] == 'EXPRESS'].shape[0]} </span><br>
        </div>
        """, unsafe_allow_html=True)
        
    st.text("")
    st.text("")
    st.text("")
    st.text("")
        
    st.markdown("<h4 style='text-align: center;'>Nombre de magasins par SCA</h4>", unsafe_allow_html=True)

    
    # Create a histogram of number of stores by centrale
    fig = px.histogram(df_base, x='centrale', color='centrale', 
                       labels={'centrale': 'Centrale', 'count': 'Nombre de magasins'},
                       category_orders={'centrale': df_base['centrale'].value_counts().index.tolist()})
    fig.update_layout(bargap=0.2, xaxis_title="", yaxis_title="Nombre de magasins",
                      legend_title_text="", 
                      height=450,
                      margin=dict(l=20, r=20, t=20, b=20),
                      xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)

    
    
    st.text("")
    st.text("")

        
    st.markdown("<h4 style='text-align: center;'>Surface commerciale selon ACDLEC [m²]</h4>", unsafe_allow_html=True)

    
    # Create a histogram of number of stores by surface commerciale
    fig = px.histogram(df_base, x='surface_com_m2', color='activite', 
                       labels={'surface_com_m2': 'Surface commerciale [m²]', 'count': 'Nombre de magasins'},
                       category_orders={'centrale': df_base['centrale'].value_counts().index.tolist()})
    fig.update_layout(bargap=0.2, xaxis_title="Surface commerciale [m²]", yaxis_title="Nombre de magasins",
                      legend_title_text="", 
                      height=450,
                      margin=dict(l=20, r=20, t=20, b=20),
                      xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig, use_container_width=True)
    st.text("")
    st.text("")
    
    st.markdown("<h4 style='text-align: center;'>Consommation éléctrique par an selon ENERGISME [MWh]</h4>", unsafe_allow_html=True)

    
    # Create a histogram of number of stores by consommation électrique et consommation de gaz sur le meme graphique 
    fig = px.histogram(df_base, x='conso_elec_annee_retenue_mwh',
                       labels={'conso_energie_annee_retenue_mwh': 'Consommation éléctrique par an [MWh]', 'count': 'Nombre de magasins'},
                       category_orders={'centrale': df_base['centrale'].value_counts().index.tolist()})
    fig.update_layout(bargap=0.2, xaxis_title="Consommation éléctrique par an [MWh]", yaxis_title="Nombre de magasins",
                      legend_title_text="", 
                      height=450,
                      margin=dict(l=20, r=20, t=20, b=20),
                      xaxis={'categoryorder':'total descending'})
    # Set x-axis range to 0-8000
    fig.update_xaxes(range=[0, 8000])
    
    # Set number of bins to 20
    fig.update_traces(xbins=dict(size=200))  # Set bin size to 400 MWh
    
    st.plotly_chart(fig, use_container_width=True)  
    st.text("")
    st.text("")
    
    st.markdown("<h4 style='text-align: center;'>Consommation de gaz par an selon ENERGISME [MWh]</h4>", unsafe_allow_html=True)

    
    # Create a histogram of number of stores by consommation électrique et consommation de gaz sur le meme graphique 
    fig = px.histogram(df_base, x='conso_gaz_annee_retenue_mwh',
                       labels={'conso_energie_annee_retenue_mwh': 'Consommation éléctrique par an [MWh]', 'count': 'Nombre de magasins'},
                       category_orders={'centrale': df_base['centrale'].value_counts().index.tolist()})
    fig.update_layout(bargap=0.2, xaxis_title="Consommation de gaz par an [MWh]", yaxis_title="Nombre de magasins",
                      legend_title_text="", 
                      height=450,
                      margin=dict(l=20, r=20, t=20, b=20),
                      xaxis={'categoryorder':'total descending'})
    # Set x-axis range to 0-8000
    fig.update_xaxes(range=[0, 8000])
    fig.update_traces(xbins=dict(size=200))
    
    st.plotly_chart(fig, use_container_width=True)  
    st.text("")
    
    
    # st.dataframe(df_base)

    

    return
        
    