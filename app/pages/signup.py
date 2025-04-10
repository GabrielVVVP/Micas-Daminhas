import streamlit as st
import time
from app.utils.helpers import is_valid_password, is_valid_email
from app.utils.users import create_user, user_exists

def signup():
    st.title("Sign Up")
    name = st.text_input("Nome")
    email = st.text_input("Email")
    account_type = st.selectbox("Tipo de Conta", ["Vendas","Admin"])
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if not is_valid_email(email):
            st.error("Por favor, insira um email válido.")
        elif not is_valid_password(password):
            st.error("A senha deve ter pelo menos 8 caracteres, incluindo uma letra maiúscula, uma letra minúscula e um número.")
        elif user_exists(email):
            st.error("Email já registrado.")
        else:
            create_user(name, email, account_type, password)
            st.success("A nova conta foi criada! A vendedora já pode logar.")
            time.sleep(2)
            st.rerun()
