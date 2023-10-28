import streamlit as st
from PIL import Image


st.set_page_config(page_title="Home", page_icon="🍽️")

# image_path = "/Users/user/Documents/repos/glauber/ftc_programacao_python/dataset/DashBoards/"
image = Image.open("logo.png")
st.sidebar.image(image, width=120)


st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## The Fastest Delivery in Town")
st.sidebar.markdown("""___""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """ 
    Growth Dashboard foi construido para acompanhar as metricas de crescimento dos Entregadores e Resturantes.
    ### Como Utilizar esse Growth Dashboard?
    - Visao Empresa:
        - Visao Gerencial: Metricas gerais de comportamento.
        - Visao Tatica: Indicadores semanais de crescimento.
        - Visao Geografica: Insights de geolocalizacao.
        
    - Visao Entregador:
        - Acompanhamento dos indicadores semanis de crescimento.
    - Visao Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help:
        - Time de Data Science no Discord:
            - @glauber1171
"""
)
