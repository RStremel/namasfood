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

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

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

def top_entregadores(df1, top_asc):
    
    cols = ['Delivery_person_ID','City','Time_taken(min)']
    df2 = df1[cols].groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending=top_asc).reset_index()
    df2_metro = df2[df2['City'] == 'Metropolitian'].head(10)
    df2_urban = df2[df2['City'] == 'Urban'].head(10)
    df2_semiurban = df2[df2['City'] == 'Semi-Urban'].head(10)
    df2 = pd.concat([df2_metro, df2_urban, df2_semiurban]).reset_index(drop=True)

    return df2

def avaliacao_media_std(df1, coluna):

    """
        coluna: 'Road_traffic_densiy' ou 'Weatherconditions'
    """
                
    cols = [coluna,'Delivery_person_Ratings']
    df2 = df1[cols].groupby(coluna).agg(['mean','std'])
    df2.columns = ['delivery_mean','delivery_std']
    df2 = df2.reset_index()

    return df2

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

st.sidebar.markdown('# Visão Entregadores')

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

weather_selection = st.sidebar.multiselect(
    'Qual a condição de clima?',
    ['Sunny', 'Stormy', 'Sandstorm', 'Cloudy', 'Fog', 'Windy'],
    default=['Sunny', 'Stormy', 'Sandstorm', 'Cloudy', 'Fog', 'Windy']
)

st.sidebar.markdown('## Criado por Rodolfo Stremel')

# filtro de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_selection)
df1 = df1.loc[linhas_selecionadas, :]

# filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(weather_selection)
df1 = df1.loc[linhas_selecionadas, :]

# =========================================================================
# Layout no Streamlit
# =========================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title('Métricas gerais')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric(label="Maior idade de entregador:", value=maior_idade)

        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric(label="Menor idade de entregador:", value=menor_idade)

        with col3:
            melhor_cond = df1['Vehicle_condition'].max()
            col3.metric(label="Melhor condição de veículo:", value=melhor_cond)

        with col4:
            pior_cond = df1['Vehicle_condition'].min()
            col4.metric(label="Pior condição de veículo:", value=pior_cond)

        st.markdown("""---""")

    with st.container():
        st.title('Avaliações')
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Avaliação média por entregador')
            cols = ['Delivery_person_ID','Delivery_person_Ratings']
            aval_media_entr = df1[cols].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(aval_media_entr)

        with col2:

            st.markdown('##### Avaliação média por trânsito')
            df2 = avaliacao_media_std(df1, coluna='Road_traffic_density')
            st.dataframe(df2)
            
            st.markdown('##### Avaliação média por clima')
            df2 = avaliacao_media_std(df1, coluna='Weatherconditions')
            st.dataframe(df2)

        st.markdown("""---""")
        
    with st.container():
        st.title('Média de velocidade de entrega')
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Entregadores mais rápidos por cidade')
            df2 = top_entregadores(df1, top_asc=True)
            st.dataframe(df2)

        with col2:
            st.markdown('##### Entregadores mais lentos por cidade')
            df2 = top_entregadores(df1, top_asc=False)            
            st.dataframe(df2)