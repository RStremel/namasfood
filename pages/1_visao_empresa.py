#importando bibliotecas
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
import geopy.distance
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

# =========================================================================
# Funções
# =========================================================================

def clean_code(df1):
    
    """ Essa funcão tem a responsabilidade de limpar o dataframe.
    
        Tipos de limpeza:
            1. Remocao dos dados NaN
            2. Mudanca do tipo da coluna de dados
            3. Remocao dos espacos das variáveis de texto
            4. Formatacao das colunas de datas
            5. Limpeza das colunas de horário (remocao do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    """
    
    #removendo dados NaN
    df1 = df1[df['Delivery_person_Age'] != 'NaN '].copy()
    df1 = df1[df['City'] != 'NaN '].copy()
    df1 = df1[df['Road_traffic_density'] != 'NaN '].copy()
    df1 = df1[df['Festival'] != 'NaN '].copy()
    df1 = df1[df1['multiple_deliveries'] != 'NaN '].copy()
    
    #convertendo colunas Age e Ratings de texto para número (int e float)
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    #convertendo coluna Order Date para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    #convertendo Time_Orderd e Time_Order_picked para tempo (horário)
    df1['Time_Orderd'] = pd.to_datetime(df1['Time_Orderd']).dt.time
    df1['Time_Order_picked'] = pd.to_datetime(df1['Time_Order_picked'], format='%H:%M:%S')
    
    #convertendo multiple_deliveries para texto
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    #resetando index
    df1 = df1.reset_index(drop=True)
    
    #removendo os espaços em excesso das colunas
    cols_strip = ['ID', 'Delivery_person_ID', 'Road_traffic_density', 'Type_of_order',
                'Type_of_vehicle', 'Festival', 'City']
    
    for col in cols_strip:
      df1.loc[:, col] = df1.loc[:, col].str.strip()
    
    #removendo o texto 'conditions ' da coluna Weatherconditions
    df1['Weatherconditions'] = df1['Weatherconditions'].str.strip('conditions ')
    
    #removendo o texto '(min) ' da coluna Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.strip('(min) ').astype(int)

    return df1
    
def qtde_pedidos_dia(df1):
    
    cols = ['ID','Order_Date']
    df_aux = df1[cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    
    return fig

def pedidos_tipo_trafego(df1):
    
    cols = ['ID','Road_traffic_density']
    df_aux = df1[cols].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_pct'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_pct', names='Road_traffic_density')

    return fig

def pedidos_cidade_trafego(df1):
    
    cols = ['ID','City', 'Road_traffic_density']
    df_aux = df1[cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    
    return fig

def pedidos_semana(df1):    
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID','week_of_year']
    df_aux = df1[cols].groupby('week_of_year').count().reset_index() 
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def media_pedidos_entregador_semana(df1):
    
    df_aux01 = df1[['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1[['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')

    return fig

def mapa_central_trafego(df1):
    
    cols = ['City', 'Delivery_location_latitude', 'Delivery_location_longitude', 'Road_traffic_density']
    df_aux = df1[cols].groupby(['City', 'Road_traffic_density']).median().reset_index()

    #Create base map
    map = folium.Map()
    
    #Loop through each row in the dataframe
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                      popup = location_info[['City', 'Road_traffic_density']]).add_to(map)
        
    folium_static (map)

    return None
    
# ============================ Início da estrutura lógica do código ============================

#importando dataset
df = pd.read_csv('food_delivery_dataset/train.csv')

#criando cópia do dataframe
df1 = df.copy()

#aplicando função de limpeza
df1 = clean_code(df1)

# =========================================================================
# Header no Streamlit
# =========================================================================

st.header('Namasfood')

# =========================================================================
# Sidebar no Streamlit
# =========================================================================

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Visão Empresa')

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',           
    min_value=datetime(2022,2,11),
    max_value=datetime(2022,4,6),
    value=datetime(2022,4,6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_selection = st.sidebar.multiselect(
    'Qual a condição de trânsito?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam']
)

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Criado por Rodolfo Stremel')

# filtro de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_selection)
df1 = df1.loc[linhas_selecionadas, :]

# =========================================================================
# Layout no Streamlit
# =========================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('### Quantidade de pedidos por dia')
        fig = qtde_pedidos_dia(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:            
            st.markdown('### Distribuição dos pedidos por tipo de tráfego')
            fig = pedidos_tipo_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('### Comparação do volume de pedidos por cidade e tipo de tráfego')
            fig = pedidos_cidade_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('### Quantidade de pedidos por semana')
        fig = pedidos_semana(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('### A quantidade média de pedidos por entregador por semana')
        fig = media_pedidos_entregador_semana(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    
    st.markdown('### Localização central de cada tipo por tráfego')
    mapa_central_trafego(df1)