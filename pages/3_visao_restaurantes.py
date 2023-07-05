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

st.set_page_config(page_title='Visão Restaurante', page_icon='👨‍🍳', layout='wide')

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

def tempo_medio_std_festivais(df1, festival, operador):

    """
    festival: 'Yes' ou 'No'
    operador: 'tempo_medio' ou 'tempo_std'
    """
    
    cols = ['Festival','Time_taken(min)']
    df_tempo_entrega = df1[cols].groupby(['Festival']).agg(['mean','std'])
    df_tempo_entrega.columns = ['tempo_medio','tempo_std']
    df_tempo_entrega = df_tempo_entrega.reset_index()
    df_festivais = round(df_tempo_entrega[df_tempo_entrega['Festival'] == festival][operador], 2)

    return df_festivais

def tempo_medio_std_cidade(df1):
    
    cols = ['City','Time_taken(min)']
    df_tempo_entrega = df1[cols].groupby('City').agg(['mean','std'])
    df_tempo_entrega.columns = ['tempo_medio','tempo_std']
    df_tempo_entrega = df_tempo_entrega.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                 x=df_tempo_entrega['City'],
                 y=df_tempo_entrega['tempo_medio'],
                 error_y=dict(type='data', array=df_tempo_entrega['tempo_std'])))
    fig.update_layout(barmode='group')
    
    return fig

def tempo_medio_std_trafego(df1):
    
    cols = ['City','Road_traffic_density','Time_taken(min)']
    df_tempo_entrega = df1[cols].groupby(['City','Road_traffic_density']).agg(['mean','std'])
    df_tempo_entrega.columns = ['tempo_medio','tempo_std']
    df_tempo_entrega = df_tempo_entrega.reset_index()

    fig = px.sunburst(df_tempo_entrega,
              path=['City','Road_traffic_density'],
              values='tempo_medio',
              color='tempo_std',
              color_continuous_scale='bugn',
              color_continuous_midpoint=np.average(df_tempo_entrega['tempo_std']))

    return fig

def tempo_medio_std_cidade_tipo(df1):

    cols = ['City','Type_of_order','Time_taken(min)']
    df_tempo_entrega = df1[cols].groupby(['City','Type_of_order']).agg(['mean','std'])
    df_tempo_entrega.columns = ['tempo_medio','tempo_std']
    df_tempo_entrega = df_tempo_entrega.reset_index()

    return df_tempo_entrega
        
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

st.sidebar.markdown('# Visão Restaurantes')

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
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

        with col1:
            st.markdown('Quantidade de entregadores')
            qtde_entregadores = df1['Delivery_person_ID'].nunique()
            col1.metric(label="", value=qtde_entregadores)
            
        with col2:
            st.markdown('Quantidade de restaurantes')     
            df1['Restaurant_unique'] = df1['Restaurant_latitude'] + df1['Restaurant_longitude']           
            qtde_restaurantes = df1['Restaurant_unique'].nunique()
            col2.metric(label="", value=qtde_restaurantes)
            
        with col3:
            st.markdown('Distância média das entregas:')

            # cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            # df1['distancia'] = df1.loc[:, cols].apply(lambda x: geopy.distance.geodesic(
            #                         (x['Restaurant_latitude'], x['Restaurant_longitude']),
            #                         (x['Delivery_location_latitude'], x['Delivery_location_longitude'])).km, axis=1)
            # dist_media = df1['distancia'].mean()
            # col3.metric(label="", value=dist_media)
            col3.metric(label="", value='27')
     
        with col4:
            st.markdown('Tempo médio em festivais')
            df_festivais = tempo_medio_std_festivais(df1, festival='Yes', operador='tempo_medio')
            col4.metric(label='', value=df_festivais)
            
        with col5:
            st.markdown('Desvio padrão em festivais')
            df_festivais = tempo_medio_std_festivais(df1, festival='Yes', operador='tempo_std')
            col5.metric(label='', value=df_festivais)
            
        with col6:
            st.markdown('Tempo médio não festivais')
            df_festivais = tempo_medio_std_festivais(df1, festival='No', operador='tempo_medio')
            col6.metric(label='', value=df_festivais)
            
        with col7:
            st.markdown('Desvio padrão não festivais')
            df_festivais = tempo_medio_std_festivais(df1, festival='No', operador='tempo_std')
            col7.metric(label='', value=df_festivais)
        st.markdown("""---""")

    with st.container():
        st.title('Tempo médio e desvio padrão de entrega por cidade')
        fig = tempo_medio_std_cidade(df1)
        st.plotly_chart(fig)
        st.markdown("""---""")

    with st.container():
        st.title('Tempo médio e desvio padrão de entrega por trânsito')
        fig = tempo_medio_std_trafego(df1)
        st.plotly_chart(fig)
        st.markdown("""---""")

    with st.container():
        st.title('Tempo médio e desvio padrão de entrega por cidade e tipo de pedido')
        df_tempo_entrega = tempo_medio_std_cidade_tipo(df1)
        st.dataframe(df_tempo_entrega)
        st.markdown("""---""")

        