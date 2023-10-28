# Libraries
import datetime
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Bibliotecas necessarias
import folium
import pandas as pd
import numpy as np
import streamlit as st
from datetime import date
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(page_title="Visao Restaurantes", page_icon='🍴', layout='wide')

###___________________________###
#           FUNCOES             #
###___________________________###


def avg_std_time_on_traffic(df1):
    st.markdown("### Distribuicao da Distancia")
    cols = ["City", "Time_taken(min)", "Road_traffic_density"]
    aux03 = (
        df1.loc[:, cols]
        .groupby(["City", "Road_traffic_density"])
        .agg({"Time_taken(min)": ["mean", "std"]})
    )

    # Renomeie as colunas após a agregação
    aux03.columns = ["avg_time", "std_time"]

    aux03 = aux03.reset_index()

    fig = px.sunburst(
        aux03,
        path=["City", "Road_traffic_density"],
        values="avg_time",
        color="std_time",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=np.average(aux03["std_time"]),
    )
    return fig


def avg_std_time_graph(df1):
    st.markdown("### Tempo por Cidade")
    coluns1 = ["City", "Time_taken(min)"]
    aux01 = (
        df1.loc[:, coluns1].groupby("City").agg({"Time_taken(min)": ["mean", "std"]})
    )

    # Renomeie as colunas após a agregação
    aux01.columns = ["avg_time", "std_time"]
    aux01 = aux01.reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Control",
            x=aux01["City"],
            y=aux01["avg_time"],
            error_y=dict(type="data", array=aux01["std_time"]),
        )
    )

    fig.update_layout(barmode="group")

    return fig


def avg_std_time_delivery(df1, festival, op):
    """
    Esta Funcao calcula o tempo medio e o desvio Padrao do tempo de entrega.
    Parametro:
        Input:
            - df: DataFrame com os dados necessarios para o calculo
            - op:Tipo de operacao que precisa ser calculado
                "avg_time" : Calcula o tempo medio
                "std_time": Calcula o desvio padrao do tempo.
        Output:
            - df: Dataframe com 2 coluna e 1 linha
    """

    # coluns1 = ['Time_taken(min)', 'Festival' ]
    df_aux = (
        df1.loc[:, ["Time_taken(min)", "Festival"]]
        .groupby("Festival")
        .agg({"Time_taken(min)": ["mean", "std"]})
    )

    # Renomeie as colunas após a agregação
    df_aux.columns = ["avg_time", "std_time"]
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux["Festival"] == festival, op], 2)

    return df_aux


def distance(df1, fig):
    if fig == False:
        coluns = [
            "Delivery_location_latitude",
            "Delivery_location_longitude",
            "Restaurant_latitude",
            "Restaurant_longitude",
        ]
        df1["distance"] = df1.loc[:, coluns].apply(
            lambda x: haversine(
                (x["Restaurant_latitude"], x["Restaurant_longitude"]),
                (x["Delivery_location_latitude"], x["Delivery_location_longitude"]),
            ),
            axis=1,
        )

        avg_distance_mean = np.round(df1["distance"].mean(), 2)

        return avg_distance_mean

    else:
        st.markdown("### Tempo Medio de entrega por cidade")
        coluns = [
            "Restaurant_latitude",
            "Restaurant_longitude",
            "Delivery_location_latitude",
            "Delivery_location_longitude",
        ]

        df1["distance"] = df1.loc[:, coluns].apply(
            lambda x: haversine(
                (x["Restaurant_latitude"], x["Restaurant_longitude"]),
                (x["Delivery_location_latitude"], x["Delivery_location_longitude"]),
            ),
            axis=1,
        )

        avg_distance_mean = (
            df1.loc[:, ["City", "distance"]].groupby("City").mean().reset_index()
        )

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=avg_distance_mean["City"],
                    values=avg_distance_mean["distance"],
                    pull=[0, 0.1, 0],
                )
            ]
        )

        return fig


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
df = pd.read_csv("dataset/train.csv").reset_index()

# Limpando dados
df1 = clean_code(df)


# ===============================
# Barra Lateral do StreamLit
# ===============================

st.header("Marketplace - Visao Restaurantes", divider="rainbow")

#IMAGE_PATH = "logo.png"
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

tab1, tab2, tab3 = st.tabs(["Visao Gerencial", "_", "_"])

with tab1:
    with st.container():
        st.title("Overal Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap="small")

        with col1:
            # Saida: Apresentar lista com todos entregadores "Unicos"
            # Processo: Selecionar a coluna "delivery_person_id" e usar funcao "nunique()"
            # Entrada :
            qtd_delivery_uniq = df1.loc[:, "Delivery_person_ID"].nunique()
            col1.metric("Drivers Unicos", qtd_delivery_uniq)

        with col2:
            avg_distance_mean = distance(df1, fig=False)
            col2.metric("Distancia Media", avg_distance_mean)

        with col3:
            df_aux = avg_std_time_delivery(df1, "Yes", "avg_time")
            col3.metric("Tempo Medio c/Festival", df_aux)

        with col4:
            df_aux = avg_std_time_delivery(df1, "Yes", "std_time")
            col4.metric("Desvio_P c/Festival", df_aux)

        with col5:
            df_aux = avg_std_time_delivery(df1, "No", "avg_time")
            col5.metric("Tempo Medio s/Festival", df_aux)

        with col6:
            df_aux = avg_std_time_delivery(df1, "No", "std_time")
            col6.metric("Tempo Medio s/Festival", df_aux)

    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2, gap="small")

        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Tempo Medio e Desvio Padrao por cidade e tipo Pedido")
            coluns2 = ["Time_taken(min)", "City", "Type_of_order"]

            # aux01 = df1.loc[:, coluns1].groupby('City')['Time_taken(min)'].agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            aux02 = (
                df1.groupby(["City", "Type_of_order"])["Time_taken(min)"]
                .agg(["mean", "std"])
                .reset_index()
            )
            # Renomeie as colunas após a agregação
            aux02.columns = [
                "City",
                "Type_of_order",
                "Mean_Time_taken(min)",
                "Std_Time_taken(min)",
            ]

            st.dataframe(aux02, use_container_width=True)

with st.container():
    st.markdown("""___""")
    col1, col2 = st.columns(2, gap="small")

    with col1:
        fig = distance(df1, fig=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = avg_std_time_on_traffic(df1)
        st.plotly_chart(fig, use_container_width=True)
