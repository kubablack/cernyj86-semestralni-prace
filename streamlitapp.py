
import streamlit as st

st.set_page_config(
    page_title='Zobrazení dat o počasí', 
    page_icon=None, 
    layout='centered', 
    initial_sidebar_state='expanded')


st.sidebar.title("Parameters")

st.write("**Select box**")

sel_1 = st.sidebar.selectbox(
    'Vyberte proměnnou, kterou chcete zobrazit:',
    options=['Maximální teplota (°C)',
       'Minimální teplota (°C)', 'Náraz větru (km/h)', 'Srážky (mm)',
       'Sněhová pokrývka (cm)', 'Sluneční svit (hod)', 'Nejvyšší tlak (hPa)',
       'Nejvyšší vlhkost (%)'],
    key='selectbox_1')

import geopandas as gpd
import pandas as pd
import plotly.express as px

poly_cze = gpd.read_file('data/poly_cze.shp')
poly_cze = poly_cze.set_index("kod")
df = pd.read_csv("data/df_2021-10-08.csv", index_col="kod")
df["Nejvyšší tlak (hPa)"] = df["Nejvyšší tlak (hPa)"].fillna(df["Nejvyšší tlak (hPa)"].mean())
poly_final = poly_cze.merge(df, how="inner", left_index=True, right_index=True)

fig = px.choropleth(poly_final,
                   geojson=poly_final.geometry,
                   locations=poly_final.index,
                   color=sel_1,
                   custom_data = ["nazev_obec","nazev_obec"],
                   projection="mercator",
                   width=900)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
fig.update_geos(lataxis_range=[48.5,51.1], lonaxis_range=[12,19], visible=False)
#fig.update_coloraxes(showscale=False)
#fig.update_traces(hovertemplate=f'Obec {poly_final["nazev_obec"]}')
fig.update_traces(
    hovertemplate="<br>".join([
        "Col1: %{customdata[0]}",
        "Col2: %{customdata[1]}",
    ])
)

st.plotly_chart(fig, use_container_width=True)
