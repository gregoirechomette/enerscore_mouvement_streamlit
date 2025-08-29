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


def plot_carte(df_base):
    
    # Title
    st.markdown("<h4 style='text-align: center;'>Vision géospatiale</h4>", unsafe_allow_html=True)
    st.text("")
    
    # Create two columns for the filters
    col1, col2 = st.columns([1, 1])
    with col1:
        # Create a selectbox to choose a SCA
        option_aggregation_carte = st.selectbox("Sélectionner l'aggrégation", ["Par magasin", "Par SCA"], key='selection_map')
    with col2:
        option_energie = st.selectbox("Sélectionner l'indicateur", ["Énergie par m² corrigée du climat", "Pourcentage de gaz"], key='selection_energie')
    
    
    st.text("")
    
    
    # Create the dataframe for scas
    df_base_sca = df_base.groupby(['centrale']).agg({'conso_energie_annee_retenue_mwh_par_m2_corrigee': 'mean',
                                                     'gaz_fraction': 'mean',
                                                     'surface_com_m2': 'sum', 
                                                     'latitude':'mean', 
                                                     'longitude':'mean'}).reset_index()
    
    # Create all the columns with the good format
    df_base_sca['conso_energie_annee_retenue_mwh_par_m2_corrigee'] = df_base_sca['conso_energie_annee_retenue_mwh_par_m2_corrigee'].round(2)
    df_base_sca['gaz_fraction'] = df_base_sca['gaz_fraction'].round()
    df_base_sca['surface_com_m2_rescaled'] = df_base_sca['surface_com_m2']/8  
    
    
    # Common definitions for the map
    cmap = matplotlib.colormaps["RdYlGn_r"] 
    view_state = pdk.ViewState(latitude=df_base["latitude"].mean(), longitude=df_base["longitude"].mean(), zoom=5.0, pitch=0,)

    
    if option_aggregation_carte == "Par magasin":

        # Copy df_base for pydeck and sort it by surface commerciale
        df_base_pydeck = df_base.copy()
        df_base_pydeck = df_base_pydeck.sort_values(by='surface_com_m2', ascending=False)

    
        # Handle the colors
        if option_energie == "Énergie par m² corrigée du climat":
            norm = mcolors.Normalize(0.2, 0.8)
            df_base_pydeck["color"] = df_base_pydeck["conso_energie_annee_retenue_mwh_par_m2_corrigee"].apply(lambda x: 
                            [int(c*255) for c in cmap(norm(x))[:3]] + [180])  
            
        elif option_energie == "Pourcentage de gaz":
            norm = mcolors.Normalize(0, 25)
            df_base_pydeck["color"] = df_base_pydeck["gaz_fraction"].apply(lambda x: 
                            [int(c*255) for c in cmap(norm(x))[:3]] + [180])  
            
        # Define a Pydeck layer
        layer = pdk.Layer("ScatterplotLayer", data=df_base_pydeck,
            get_position=["longitude", "latitude"], get_radius="surface_com_m2", get_fill_color="color", 
            pickable=True, opacity=0.6, stroked=True,  
            get_line_color=[128, 128, 128], get_line_width=300)
        
        
        st.pydeck_chart(pdk.Deck(layers=[layer],initial_view_state=view_state, map_style='mapbox://styles/mapbox/light-v10',
                                tooltip={"text": 
                                    "Code panonceau: {code_panonceau}\n" +
                                    "Nom de l'adhérent: {adherent}\n" +
                                    "Surface: {surface_com_m2} m²\n " + 
                                    "Conso: {conso_energie_annee_retenue_mwh_par_m2_corrigee} MWh/m²\n " +
                                    "Pourcentage de gaz: {gaz_fraction} %"}), height=600)
        
        
        
        # Create a colorbar
        fig, ax = plt.subplots(figsize=(5, 0.04))  # Wide and short figure
        cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation="horizontal")
        
        # Set the size of colorticks
        colorbar_fontsize = 3.5
        cb.ax.tick_params(labelsize=colorbar_fontsize)
        if option_energie == "Énergie par m² corrigée du climat":
            cb.set_label("Consommation corrigée [MWh/m²]", fontsize=colorbar_fontsize)
        elif option_energie == "Pourcentage de gaz":
            cb.set_label("Pourcentage de gaz [%]", fontsize=colorbar_fontsize)
        cb.ax.xaxis.set_tick_params(width=0.3)
        
        st.pyplot(fig)
        
    else:
        
        
        if option_energie == "Énergie par m² corrigée du climat":
            norm = mcolors.Normalize(0.42, 0.6)
            df_base_sca['color'] = df_base_sca['conso_energie_annee_retenue_mwh_par_m2_corrigee'].apply(lambda x: [int(c*255) for c in cmap(norm(x))[:3]] + [180])
        
        elif option_energie == "Pourcentage de gaz":
            norm = mcolors.Normalize(3, 20)
            df_base_sca['color'] = df_base_sca['gaz_fraction'].apply(lambda x: [int(c*255) for c in cmap(norm(x))[:3]] + [180])
        
        
        
        # Define a Pydeck layer for SCA
        layer_sca = pdk.Layer("ScatterplotLayer", data=df_base_sca,
            get_position=["longitude", "latitude"], get_radius="surface_com_m2_rescaled", get_fill_color="color", 
            pickable=True, opacity=0.6, stroked=True,  
            get_line_color=[128, 128, 128], get_line_width=300)
        

        
        st.pydeck_chart(pdk.Deck(layers=[layer_sca],initial_view_state=view_state, map_style='mapbox://styles/mapbox/light-v10',
                                tooltip={"text": 
                                    "Centrale: {centrale}\n" +
                                    "Surface totale: {surface_com_m2} m²\n " + 
                                    "Conso moyenne: {conso_energie_annee_retenue_mwh_par_m2_corrigee} MWh/m² \n " +
                                    "Pourcentage de gaz: {gaz_fraction} %"
                                    }), height=600)
        
        # Create a colorbar
        fig, ax = plt.subplots(figsize=(5, 0.04))  # Wide and short figure
        cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation="horizontal")
        
        # Set the size of colorticks
        colorbar_fontsize = 3.5
        cb.ax.tick_params(labelsize=colorbar_fontsize)
        cb.set_label("Consommation corrigée [MWh/m²]", fontsize=colorbar_fontsize)
        cb.ax.xaxis.set_tick_params(width=0.3)
        
        st.pyplot(fig)
