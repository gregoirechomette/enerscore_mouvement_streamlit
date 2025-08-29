import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import folium
from streamlit_folium import st_folium


import sys
import toml
sys.path.append('./tabs')
import data_loading as dl
import resume, carte, nuage_points, nuage_points_gaz, conso_hebdo_past, tendances, tendances_sca

# Load the configuration and access key settings
config = toml.load(".streamlit/config.toml")
project_name = config["project"]["project_name"]
expo_space_name = config["project"]["expo_space_name"]


# Global configuration
st.set_page_config(layout="wide", page_title=project_name)


# Load most data tables
df_carte_identite = dl.load_carte_identite(expo_space_name + "." + config["tables"]["table_carte_identite"])
df_consos_stats = dl.load_stats_consos(expo_space_name + "." + config["tables"]["table_stats_consos"])
df_radar = dl.load_consos_data_all_codes(expo_space_name + "." + config["tables"]["table_radar"])
df_tendances = dl.load_consos_data_all_codes(expo_space_name + "." + config["tables"]["table_consos_elec_gaz_mois_ready"])


st.markdown("""<style>.css-o18uir.e16nr0p33 {margin-top: -275px;}</style>""", unsafe_allow_html=True)
st.sidebar.image('./pictures/Leclerc-energies_logo_RVB.png')


# Tabs
tab_id, tab_carte, tab_nuage, tab_nuage_gaz, tab_conso_hebdo_past, tab_tendances, tab_tendances_sca = st.tabs(["Résumé \u2001\u2001", 
                                                                                "Carte \u2001\u2001",                                    
                                                                                "Benchmark efficacité \u2001\u2001", 
                                                                                "Part du gaz \u2001\u2001", 
                                                                                'Profil de consommation \u2001\u2001',
                                                                                'Tendances globales \u2001\u2001',
                                                                                'Comparaison des SCA \u2001\u2001'])

with tab_id:
    resume.resume(df_carte_identite)    
    
    
with tab_carte:
    carte.plot_carte(df_carte_identite)
    pass


with tab_nuage:
    st.text("")
    euros_par_mwh = 180; tC02_par_gwh = 32
    filtre_sca, filtre_activite = nuage_points.big_numbers_nuage_points(df_carte_identite)
    nuage_points.figure_nuage_points(df_carte_identite, seuil=0.2, col_y='conso_elec_mwh_par_m2_corrigee', filtre_sca=filtre_sca, filtre_activite=filtre_activite)
    nuage_points.expander_nuage_points(euros_par_mwh, tC02_par_gwh)

with tab_nuage_gaz:
    st.text("")
    filtre_sca_gaz, filtre_activite_gaz = nuage_points_gaz.big_numbers_nuage_points(df_carte_identite)
    nuage_points_gaz.figure_nuage_points(df_carte_identite, seuil=0.2, filtre_sca=filtre_sca_gaz, filtre_activite=filtre_activite_gaz)

with tab_conso_hebdo_past:
    conso_hebdo_past.plot_conso_hebdo(df_consos_stats, df_carte_identite)

with tab_tendances:
    tendances.plot_tendances(df_carte_identite, df_tendances)
    
with tab_tendances_sca:
    tendances_sca.plot_tendances_sca(df_carte_identite, df_tendances)
    