import datetime
import folium
import geopandas as gpd
import geopy
import joblib 
import networkx as nx
import osmnx as ox
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
import time

from folium.features import DivIcon
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Omdena Philippines Smart Farming",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.set_option('deprecation.showPyplotGlobalUse', False)

st.markdown(
    """
    <style>
    .css-1d391kg {
        background-color:  #a9dfbf  !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown('<h1 style="margin-left:8%; color:#1a5276">Omdena Philippines <br> Smart Farming</h1>', unsafe_allow_html=True)

add_selectbox = st.sidebar.radio(
    "",
    ("About the Project", "Dataset", "Modelling", "Collaborators")
)

if add_selectbox == 'About the Project':
    st.markdown('<h3>Utilizing AI/ML and Satellite Imagery to Increase Water Efficiency for Rice Farming </h3>', unsafe_allow_html=True)
    
    st.markdown('<h4>The Background</h4>', unsafe_allow_html=True)
    st.markdown('<p>According to World Bank Group, The Philippines is one of the most natural hazard-prone countries in the world. The social and economic cost of natural disasters in the country is increasing due to population growth, change in land-use patterns, migration, unplanned urbanization, environmental degradation, and global climate change. Agriculture, specifically rice farms which are one of the most important crops in the Philippines are no exception to climate change such as drought that could lead to wide food insecurity for the next decades.</p>', unsafe_allow_html=True)
    st.markdown('<h4>The Problem</h4>', unsafe_allow_html=True)
    st.markdown('The goal of the project is to build an open-source AI-driven interactive map that predicts the required water for a rice farm. The tool will be a low-cost alternative for expensive sensors to aid rice farmers to consume water irrigation efficiently. <br><br> Having the tool available to rice farmers and other related stakeholders will help them save an irrigation cost and adapt to the impacts of climate change.', unsafe_allow_html=True)

    HtmlFile = open("map_malolos.html", 'r', encoding='utf-8')
    heatmap_html = HtmlFile.read() 

    components.html(heatmap_html, height= 500, width=900)

elif add_selectbox == 'Dataset':
    
    st.markdown('<h4>Dataset</h4>', unsafe_allow_html=True)
    dataset_selectbox = st.selectbox(
    "",
            ("Introduction", "ETo", "Crop Water Need (ETcrop)", "Irrigation Water Need")
    )
    
    if dataset_selectbox == "Introduction":
        st.markdown('<b>Evapotranspiration (ET)</b> is a combination of the water evaporated from the soil surface and transpired through the plant. ET can be measured using evaporation pans and atmometers or calculated using climate data.', unsafe_allow_html=True)
        
        st.markdown('The following nomenclature is often used for reference ET data:', unsafe_allow_html=True)
                    
        st.markdown('<ul><li>ETo - ET calculated using grass as the reference crop </li>\
        <li>ETr - ET calculated using alfalfa as the reference crop</li><li>ETp - ET measured from a pan or atmometer</li></ul>', unsafe_allow_html=True)
        
        st.markdown('Once the reference ET has been determined, a crop coefficient must be applied to adjust the reference ET value for local conditions and the type of crop being irrigated.', unsafe_allow_html=True)
    
    elif dataset_selectbox == "ETo":
        eto_expander = st.expander(label='About ETo')
        with eto_expander:
            st.markdown('<b>ETo</b> represents the evapotranspiration rate from a reference surface, not short of water.', unsafe_allow_html=True)
            st.markdown('<b>Formula:</b>  ETo = p (0.46 T mean + 8)', unsafe_allow_html=True)
            col1, col2 = st.columns([8, 4])
            col1.markdown('<b>Getting P Values:</b>', unsafe_allow_html=True)
            col1.markdown('<ul><li>Latitude: 15° North</li><li>Month: (Given Month)</li></ul>', unsafe_allow_html=True)
            image = Image.open('ETo_mean_chart.PNG')
            col1.image(image,width=500)

            col2.markdown('<b>T Mean Computation:</b>', unsafe_allow_html=True)
            image = Image.open('ETo_t_mean_computation.PNG')
            col2.image(image,width=300)

            col2.markdown('<b>References:</b>', unsafe_allow_html=True)
            col2.markdown('<ul><li>https://www.fao.org/3/s2022e/s2022e07.htm</li></ul>', unsafe_allow_html=True)
        
        daily_eto_expander = st.expander(label='Daily', expanded=True)
        with daily_eto_expander:
            final_daily_melt = pd.read_csv('data/final_daily_melt_eto.csv',  parse_dates=['time'])

            fig = px.line(final_daily_melt, x='time', y='value', color='variable', title='ETo Daily Variables', width=1000, height=500)
            fig.update_layout(title_text='ETo Daily Variables', title_x=0.5)
            st.write(fig)
        
        weekly_eto_expander = st.expander(label='Weekly', expanded=True)
        with weekly_eto_expander:
            final_weekly_melt = pd.read_csv('data/final_weekly_melt_eto.csv')

            fig = px.line(final_weekly_melt[(final_weekly_melt['variable']=='T_mean')].sort_values(by=['week']), x='week', y='value', color='year', title='T_Mean Weekly', width=1000, height=500)
            fig.update_layout(title_text='T_Mean Weekly', title_x=0.5)
            st.write(fig)

            fig = px.line(final_weekly_melt[(final_weekly_melt['variable']=='T_min')].sort_values(by=['week']), x='week', y='value', color='year', title='T_min Weekly', width=1000, height=500)
            fig.update_layout(title_text='T_min Weekly', title_x=0.5)
            st.write(fig)


            fig = px.line(final_weekly_melt[(final_weekly_melt['variable']=='T_max')].sort_values(by=['week']), x='week', y='value', color='year', title='T_max Weekly', width=1000, height=500)
            fig.update_layout(title_text='T_max Weekly', title_x=0.5)
            st.write(fig)
            
        monthly_eto_expander = st.expander(label='Monthly', expanded=True)
        with monthly_eto_expander:
            final_monthly_melt = pd.read_csv('data/final_monthly_melt_eto.csv')
            
            fig = px.line(final_monthly_melt[(final_monthly_melt['variable']=='T_mean')].sort_values(by=['month']), x='month', y='value', color='year', title='T_Mean Monthly', width=1000, height=500)
            fig.update_layout(title_text='T_Mean Monthly', title_x=0.5)
            st.write(fig)

            fig = px.line(final_monthly_melt[(final_monthly_melt['variable']=='T_min')].sort_values(by=['month']), x='month', y='value', color='year', title='T_min Monthly', width=1000, height=500)
            fig.update_layout(title_text='T_min Monthly', title_x=0.5)
            st.write(fig)


            fig = px.line(final_monthly_melt[(final_monthly_melt['variable']=='T_max')].sort_values(by=['month']), x='month', y='value', color='year', title='T_max Monthly', width=1000, height=500)
            fig.update_layout(title_text='T_max Monthly', title_x=0.5)
            st.write(fig)
            
        
    elif dataset_selectbox == "Crop Water Need (ETcrop)":
        eto_crop_expander = st.expander(label='About ETcrop')
        with eto_crop_expander:
            st.markdown('The <b>crop water need (ET crop) </b> is defined as the depth (or amount) of water needed to meet the water loss through evapotranspiration. In other words, it is the amount of water needed by the various crops to grow optimally. ', unsafe_allow_html=True)

            st.markdown('The crop’s water use can be determined by multiplying the reference ETo by a crop coefficient (Kc). The crop coefficient adjusts the calculated reference ETo to obtain the crop evapotranspiration ETcrop. Different crops will have a different crop coefficient and resulting water use.', unsafe_allow_html=True)

            st.markdown('<b>Formula:</b> ETcrop = ETo x Kc', unsafe_allow_html=True)
            st.markdown('Where <br> ETo = calculated reference ET for grass (mm) <br> Kc = crop coefficient or ratio of the actual crop evpotranspiration to its potential evapotranspiration', unsafe_allow_html=True)

            st.markdown('<b>References:</b>', unsafe_allow_html=True)
            st.markdown('<ul><li>http://irrigationtoolbox.com/ReferenceDocuments/Extension/BCExtension/577100-5.pdf</li><li>https://www.fao.org/3/s2022e/s2022e07.htm</li><li>https://www.fao.org/3/s2022e/s2022e08.htm</li><li>https://www.fao.org/3/x0490e/x0490e06.htm#chapter%202%20%20%20fao%20penman%20monteith%20equation</li></ul>', unsafe_allow_html=True)
         
        eto_daily_crop_expander = st.expander(label='Daily', expanded=True)
        with eto_daily_crop_expander:
            daily_crop_expander = pd.read_csv('data/ml_final_df_daily.csv',  parse_dates=['time'])
            
            col_1, col_2 = st.columns(2)
            fig = px.line(daily_crop_expander, x='time', y='INRice', title='INRice Daily', width=480, height=400)
            fig.update_layout(title_text='ETcrop Daily', title_x=0.5)
            col_1.write(fig)
            
            fig = px.line(daily_crop_expander, x='time', y='Kc', title='Kc Daily', width=480, height=400)
            fig.update_layout(title_text='Kc Daily', title_x=0.5)
            col_2.write(fig)
            
            
        eto_weekly_crop_expander = st.expander(label='Weekly', expanded=True)
        with eto_weekly_crop_expander:
            in_rice_weekly = pd.read_csv('data/final_weekly_in_rice.csv')
            
            fig = px.line(in_rice_weekly, x='week', y='INRice', color="year", title='INRice Weekly', width=900, height=400)
            fig.update_layout(title_text='INRice Weekly', title_x=0.5)
            st.write(fig)
            
            kc_weekly = pd.read_csv('data/final_weekly_kc.csv')
            
            fig = px.line(kc_weekly, x='week', y='Kc', color="year", title='Kc Weekly', width=900, height=400)
            fig.update_layout(title_text='Kc Weekly', title_x=0.5)
            st.write(fig)
            
            
        eto_monthly_crop_expander = st.expander(label='Monthly', expanded=True)
        with eto_monthly_crop_expander:
            in_rice_monthly = pd.read_csv('data/final_monthly_in_rice.csv')
            
            fig = px.line(in_rice_monthly, x='month', y='INRice', color="year", title='INRice Monthly', width=900, height=400)
            fig.update_layout(title_text='INRice Monthly', title_x=0.5)
            st.write(fig)
            
            kc_monthly = pd.read_csv('data/final_monthly_kc.csv')
            
            fig = px.line(kc_monthly, x='month', y='Kc', color="year", title='Kc Monthly', width=900, height=400)
            fig.update_layout(title_text='Kc Monthly', title_x=0.5)
            st.write(fig)

    elif dataset_selectbox == "Irrigation Water Need":
        irrigation_expander = st.expander(label='About Irrigation Water Need')
        with irrigation_expander:
            st.markdown('<b>For all field crops Formula:</b> IN = ETcrop - Pe', unsafe_allow_html=True)
            st.markdown('Where <br> IN = Irrigation Needs <br> ETcrop = amount of water needed <br> Pe = effective rainfall', unsafe_allow_html=True)

            st.markdown('<b>Special case, Rice Formula:</b> INrice = ETcrop + SAT + PERC + WL - Pe', unsafe_allow_html=True)

            st.markdown('Where <br> INrice = Irrigation Needs Rice <br> ETcrop = amount of water needed <br> SAT = water needed to saturate soil for land preparation by puddling <br> PERC = percolation and seepage losses <br> WL = amount needed to establish water layer percolation and seepage losses  br> Pe = effective rainfall', unsafe_allow_html=True)

            st.markdown('<b>Reference:</b>', unsafe_allow_html=True)
            st.markdown('<ul><li>https://www.fao.org/3/s2022e/s2022e08.htm#4.4%20irrigation%20water%20need%20of%20rice</li></ul>', unsafe_allow_html=True)
            
            
        irrigation_daily_expander = st.expander(label='Daily Irrigation', expanded=True)
        with irrigation_daily_expander:
            daily_irrigation = pd.read_csv('data/final_daily_irrigation.csv')
            
            fig = px.line(daily_irrigation, x='time', y='value', color="variable", title='Irrigation Daily Variables', width=900, height=400)
            fig.update_layout(title_text='Irrigation Daily Variables', title_x=0.5)
            st.write(fig)
    
elif add_selectbox == 'Modelling':
    prediction_selectbox = st.selectbox(
    "Prediction Interval",
        ("Overall Process", "Daily", "Weekly", "Monthly")
    )
   
    
    if st.button('Search'):
        for _prediction_variables in prediction_variables:
            fb_prophet_monthly_model = joblib.load('models/fb_prophet_monthly_{}.sav'.format(_prediction_variables))
            monthyly_forecast_data = pd.read_csv('data/fb_prophet_monthly_{}.csv'.format(_prediction_variables))
            monthyly_forecast_data['ds'] = pd.to_datetime(monthyly_forecast_data['ds'])

            fb_prophet_monthly_plot = fb_prophet_monthly_model.plot(monthyly_forecast_data, figsize=(8, 4))
            ax = fb_prophet_monthly_plot.gca()
            ax.set_title("{} Monthly Prediction".format(_prediction_variables) , size=12)
            ax.set_xlabel("Mean", size=10)
            ax.set_ylabel("Dates", size=10)
            ax.tick_params(axis="x", labelsize=10)
            ax.tick_params(axis="y", labelsize=10)
            st.write(fb_prophet_monthly_plot)
            
elif add_selectbox == 'Collaborators':
    
    col1, col2 = st.columns([3,8])
    
    image = Image.open('logo.PNG')
    col1.image(image,width=250)
    col1.markdown('<center><a href="https://omdena.com/omdena-chapter-page-philippines/" target="_blank">Omdena Philippines</a></center>', unsafe_allow_html=True)
    col2.markdown('<br><br><b>Project Manager:</b> <a href="https://www.linkedin.com/in/jester-carlos-3410831a7/" target="_blank">Jester Carlos</a>', unsafe_allow_html=True)
    col2.markdown('<b>Collaborators:</b>', unsafe_allow_html=True)
    col2.markdown('''
    <ul>
    <li><a href="https://www.linkedin.com/in/ameeayco/" target="_blank">Amee Ayco</a></li>
    <li><a href="https://www.linkedin.com/in/drumad/" target="_blank">Drew Maderazo</a></li>
    <li><a href="https://www.linkedin.com/in/gienel/" target="_blank">Gienel Manarang</a></li>
    <li><a href="https://www.linkedin.com/in/jerome-endaya-0928a6111/" target="_blank">Jerome Israel Endaya</a></li>
    <li>John Russel</li>
    <li><a href="https://www.linkedin.com/in/jomaminoza/" target="_blank">Joma Minoza</a></li>
    <li><a href="https://www.linkedin.com/in/nilleth-pontino-aba95a99/" target="_blank">Nilleth Pontino</a> </li>
    <li><a href="https://www.linkedin.com/in/rhey-ann-magcalas-47541490/" target="_blank">Rhey Ann Magcalas</a></li>
    <li><a href="https://www.linkedin.com/in/saiphaniparsa/" target="_blank">Sai Phani Parsa </a></li>
    <li><a href="https://www.linkedin.com/in/zyndlyy/" target="_blank">Zyndly Kent </a></li></ul>''', unsafe_allow_html=True)

