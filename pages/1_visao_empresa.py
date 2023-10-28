# Libraries
import datetime
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Bibliotecas necessarias
import folium
import pandas as pd
import streamlit as st
from datetime import date
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(page_title="Visao Empresa", page_icon='🧊', layout='wide')

###___________________________###
#           FUNCOES             #
###___________________________###
def country_maps(df1):
    # Criando colunas a serem interaveis na solucao
    df_aux1 = (df1.loc[:, ["City","Road_traffic_density",
                  "Delivery_location_latitude",
                  "Delivery_location_longitude" ]]
                  .groupby(["City", "Road_traffic_density"])
                  .median()
                  .reset_index())

    # Desenhando grafico tipo "Mapa"
    map = folium.Map()

    for index, location_info in df_aux1.iterrows():
        folium.Marker([location_info["Delivery_location_latitude"],
                       location_info["Delivery_location_longitude" ]],
                       popup=location_info[[ "City", "Road_traffic_density" ]]).add_to(map)

    folium_static(map, width=1024, height=600)

def order_share_by_week(df1):
    # Contando quantidade de entregas por "Semana"
    aux1 = (df1.loc[:, ['ID', 'week_of_Year']]
               .groupby(["week_of_Year"])
               .count()
               .reset_index())
    aux2 = (df1.loc[:, ["Delivery_person_ID", "week_of_Year"]]
               .groupby(["week_of_Year"])
               .nunique()
               .reset_index())

    df_aux = pd.merge(aux1, aux2, how="inner",  on='week_of_Year')
    df_aux['order_by_delivery'] = df_aux["ID"] / df_aux["Delivery_person_ID"]

    fig = px.line(df_aux, x="week_of_Year", y="order_by_delivery")

    return fig

def order_by_week(df1):
    # Selecionando as colunas necessarias...
    coluns = ["ID", "week_of_Year"]

    # Contabilizando total de entregas "ID" por numeros de semanas "Week_of_Year"
    aux01 = df1.loc[:, coluns].groupby(["week_of_Year"]).count().reset_index()

    # Desenhando o grafico em forma de "linha"/
    fig = px.line(aux01, x="week_of_Year", y="ID")
            
    return fig

# Criando variavel com colunas a serem interaveis
# Contando pedidos atraves do 'ID' classificados por 'City' and 'Road_traffic_density'
def traffic_order_city(df1):
    aux3 = (df1.loc[:, ["ID", "City", "Road_traffic_density"]]
               .groupby(["City", "Road_traffic_density"])
               .count()
               .reset_index())

    # Desenhando um grafico de Bolhas
    fig = px.scatter(aux3, x="City", y="Road_traffic_density", size="ID", color="City")
                
    return fig


def traffic_order_share(df1):
    # Criando colunas a serem pecorridas
    coluns1 = ["ID", "Road_traffic_density"]

    # Contando quantidades de pedidos por "Tipos de Trafegos"
    aux1 = (df1.loc[:, coluns1]
               .groupby(["Road_traffic_density"])
               .count()
               .reset_index())

    # Criando coluna de porcentagem de pedidos para tipo de trafego
    aux1["percent_entregas"] = aux1["ID"] / aux1["ID"].sum()

    # Desenhando grafico tipo Pizza
    fig = px.pie(aux1, values="percent_entregas", names="Road_traffic_density")

    return fig


def orders_metric(df1):
    # Order Metric
    aux01 = (df1.loc[:, ["ID", "Order_Date"]]
                        .groupby("Order_Date")
                        .count()
                        .reset_index())
            
            # Desenhar Linhas de Grafico
    fig = px.bar(aux01, x="Order_Date", y="ID")
            
    return fig

## Funcao limpeza dos dados
def clean_code( df1 ):
    """ Esta Funcao tem a responsabilidade de limpar o DataFrame
    
    Tipos de limpeza:
    
    1 - Remocao dos NaN`s ;
    2 - Limpeza dos espaços em branco dos valores na coluna ; 
    3- Convertendo alguns tipos de colunas em Str, Int e Data
    4 - Formatacao da coluna de Data;
    5 - Limpeza da coluna do tempo ( remocao do texto da variavel numerica )
    
    """
    # Limpeza de Dados
    # Removendo todos os NaN de cada coluna
    linhas_selecionadas = df1["Delivery_person_Age"] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas_1 = df1["City"] != "NaN "
    df1 = df1.loc[linhas_selecionadas_1, :].copy()

    linhas_selecionadas_2 = df1["Festival"] != "NaN "
    df1 = df1.loc[linhas_selecionadas_2, :].copy()

    linhas_selecionadas_3 = df1["Weatherconditions"] != "conditions NaN "
    df1 = df1.loc[linhas_selecionadas_3, :].copy()

    linhas_selecionadas_4 = df1["Road_traffic_density"] != "NaN "
    df1 = df1.loc[linhas_selecionadas_4, :].copy()

    linhas_selecionadas_5 = df1["City"] != "NaN "
    df1 = df1.loc[linhas_selecionadas_5, :].copy()


    # Limpe os espaços em branco dos valores na coluna
    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].str.strip()
    # Preencha 'NaN' com zero e converta a coluna para int
    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].replace("NaN", "0").astype(int)

    # 2. Convertendo de texto/ categoria/ string para numeros decimais:
    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)

    # 3. Convertendo de texto para data:
    df1["Order_Date"] = pd.to_datetime(df1["Order_Date"], format="%d-%m-%Y")
    df1["week_of_Year"] = df1["Order_Date"].dt.strftime("%U")

    # 4 Removendo as linhas da coluna Multiple deliveries que tenham NaN
    linhas_selecionadas = df1["multiple_deliveries"] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1["multiple_deliveries"] = df1["multiple_deliveries"].fillna(0).astype(int)

    # 5. Removendo espacos dentro de string/text/object

    df1.loc[:, "ID"] = df1.loc[:, "ID"].str.strip()
    df1.loc[:, "Road_traffic_density"] = df1.loc[:, "Road_traffic_density"].str.strip()
    df1.loc[:, "Type_of_order"] = df1.loc[:, "Type_of_order"].str.strip()
    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, "Type_of_vehicle"].str.strip()
    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()
    df1.loc[:, "Festival"] = df1.loc[:, "Festival"].str.strip()

    # 6. Limpando a coluna do Time_Taken

    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply(lambda x: x.split("(min) ")[1])
    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)

    
    return df1

# ----------------- Inicio da Estrutura do codigo------------------------------------------
#--------------------

# Import Data Set
df = pd.read_csv("../dataset/train.csv").reset_index()

# Limpando dados
df1 = clean_code(df)

# ===============================
# Barra Lateral do StreamLit
# ===============================

st.header("Marketplace - Visao Empresa", divider="rainbow")

#image_path = "logo.png"
image = Image.open("logo.png")
st.sidebar.image(image, width=120)

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## The Fastest Delivery in Town")
st.sidebar.markdown("""___""")

st.sidebar.markdown("## Selecione Uma data limite")
date_slider = st.sidebar.slider(
    "Ate Qual Valor?",
    value=datetime.date(2022, 4, 13),
    min_value=datetime.date(2022, 3, 19),
    max_value=datetime.date(2022, 3, 31),
    format="DD-MM-YYYY")

st.sidebar.markdown("""___""")


traffic_options = st.sidebar.multiselect(
    "What are the Wheather Conditions?",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"])

st.sidebar.markdown("""___""")
st.sidebar.markdown("Created by Comunidade DS")

# Filtro de Data
date_slider = pd.to_datetime(date_slider)
linhas_selecionadas = df1["Order_Date"] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
linhas_selecionadas01 = df1["Road_traffic_density"].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas01, :]

# ===============================
# Layout do StreamLit
# ===============================

tab1, tab2, tab3 = st.tabs(["Visao Gerencial", "Visao Tatica", "Visao Geografica"])

with tab1:
    with st.container():
        # Order Metrics
        fig = orders_metric( df1 )
        st.markdown("# Orders Metrics")
        st.plotly_chart(fig, use_container_width=True)
        
        
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            # Traffic Order Share
            st.markdown("# Traffic Order Share")
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)
            
            

        with col2:
            # Traffic Order City
            st.markdown("# Traffic Order City")
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)
            
            

with tab2:
    with st.container():
        # Order by Week
        fig = order_by_week(df1) 
        st.markdown("# Order by Week")
        st.plotly_chart(fig, use_container_width=True)

    
    with st.container():
        # Order Share by week
        fig = order_share_by_week(df1)
        st.markdown("# Order Share by Week")
        st.plotly_chart(fig, use_container_width=True)
        

# Visao Geografica
with tab3:
    # Country Maps
    st.markdown("# Country Maps")
    fig = country_maps(df1)
    
    
        
        