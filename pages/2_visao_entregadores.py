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

st.set_page_config(page_title="Visao Entregadores", page_icon='🛵', layout='wide')

###___________________________###
#           FUNCOES             #
###___________________________###


def top_delivers(df1, top_asc):
    df2 = (
        df1.loc[:, ["Delivery_person_ID", "City", "Time_taken(min)"]]
        .groupby(["City", "Delivery_person_ID"])
        .mean()
        .sort_values(["City", "Time_taken(min)"], ascending=top_asc)
        .reset_index()
    )

    df_aux01 = df2.loc[df2["City"] == "Metropolitian", :].head(10)
    df_aux02 = df2.loc[df2["City"] == "Urban", :].head(10)
    df_aux03 = df2.loc[df2["City"] == "Semi-Urban", :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3


def clean_code(df1):
    """Esta Funcao tem a responsabilidade de limpar o DataFrame

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
    df1["Delivery_person_Age"] = (
        df1["Delivery_person_Age"].replace("NaN", "0").astype(int)
    )

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

    df1["Time_taken(min)"] = df1["Time_taken(min)"].apply(
        lambda x: x.split("(min) ")[1]
    )
    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)

    return df1


# ----------------- Inicio da Estrutura do codigo------------------------------------------
# --------------------

# Import Data Set
df = pd.read_csv("../dataset/train.csv").reset_index()

# Limpando dados
df1 = clean_code(df)

# ===============================
# Barra Lateral do StreamLit
# ===============================

st.header("Marketplace - Visao Entregadores", divider="rainbow")

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
    format="DD-MM-YYYY",
)

st.sidebar.markdown("""___""")


traffic_options = st.sidebar.multiselect(
    "Quais as condicoes de Tarfego?",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"],
)

st.sidebar.markdown("""___""")


wheather_options = st.sidebar.multiselect(
    "Quais as condicoes de Clima?",
    [
        "conditions Sunny",
        "conditions Stormy",
        "conditions Sandstorms",
        "conditions Cloudy",
        "conditions Fog",
        "conditions Windy",
    ],
    default=[
        "conditions Sunny",
        "conditions Stormy",
        "conditions Sandstorms",
        "conditions Cloudy",
        "conditions Fog",
        "conditions Windy",
    ],
)


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

tab1, tab2, tab3 = st.tabs(["Visao Entregadores", "_", "_"])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap="large")

        with col1:
            # A Maior idade dos entregadores
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            col1.metric("Maior Idade", maior_idade)

        with col2:
            # A Menor idade dos entregadores
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            col2.metric("Menor Idade", menor_idade)

        with col3:
            # A Melhor condicao dos veiculos
            melhor_condicao = df1.loc[:, "Vehicle_condition"].max()
            col3.metric("Melhor Condicao", melhor_condicao)

        with col4:
            # A Pior condicao dos veiculos
            pior_condicao = df1.loc[:, "Vehicle_condition"].min()
            col4.metric("Pior Condicao", pior_condicao)

    with st.container():
        st.markdown("""___""")
        st.title(" Avaliacoes")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Avaliacao media por entregadores")
            df_avg_delivery_person = (
                df1.loc[
                    :,
                    [
                        "Delivery_person_ID",
                        "Delivery_person_Ratings",
                    ],
                ]
                .groupby("Delivery_person_ID")
                .mean()
                .reset_index()
            )

            st.dataframe(df_avg_delivery_person)

        with col2:
            st.markdown("##### Media e Desvio por trafego")
            df_std_mean_por_trafego = (
                df1.loc[:, ["Delivery_person_Ratings", "Road_traffic_density"]]
                .groupby("Road_traffic_density")
                .agg({"Delivery_person_Ratings": ["mean", "std"]})
            )

            # Mudanca de nome de coluna
            df_std_mean_por_trafego.columns = ["delivery_mean", "delivery_std"]

            # Resetar o index
            df_std_mean_por_trafego = df_std_mean_por_trafego.reset_index()
            st.dataframe(df_std_mean_por_trafego)

            st.markdown("##### Media e Desvio por condicao clima")
            df_std_mean_por_condicao_clima = (
                df1.loc[:, ["Delivery_person_Ratings", "Weatherconditions"]]
                .groupby("Weatherconditions")
                .agg({"Delivery_person_Ratings": ["mean", "std"]})
            )
            # Mudanca de nome da coluna
            df_std_mean_por_condicao_clima.columns = ["wheather_mean", "wheather_std"]

            # Resetar o index
            df_std_mean_por_condicao_clima = (
                df_std_mean_por_condicao_clima.reset_index()
            )
            st.dataframe(df_std_mean_por_condicao_clima)

    with st.container():
        st.markdown("""___""")
        st.title(" Velocidade de Entrega")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Top 10 entregador mais rapido")
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.markdown("##### Top 10 entregador mais lento")
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)

        st.markdown("""___""")
