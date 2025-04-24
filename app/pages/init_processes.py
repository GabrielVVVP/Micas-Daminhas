import streamlit as st

def init_processes():
    st.title("Início - Funil de Registros Micas Daminhas")
    st.write("O Funil de Registros é o fluxo de operações que o setor de vendas realiza!")
    st.write("Abaixo segue o diagrama dos passos da loja.")
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("assets/Img/diagram.png", use_container_width=True)