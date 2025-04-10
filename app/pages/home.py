import streamlit as st

def home():
    colm1, colm2, colm3 = st.columns([2, 4, 1])
    with colm2:
        st.title("Sistema de Pagamentos - Micas Daminhas")
        st.write("Bem-vindo ao sistema de organização de caixa da Micas Daminhas!")
        st.write("Selecione uma opção no menu lateral para começar.")
        st.write("")
        st.write("")
        st.write("")
        st.write("Desenvolvido por Gabriel Vilaça. Direitos Reservados © 2025")