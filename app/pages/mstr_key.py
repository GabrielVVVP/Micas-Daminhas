import streamlit as st
import os
import time
from data.config import mstr_key

# Path to the config file
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/config.py"))

def save_master_key(new_key):
    """Save the new master key to the config file."""
    with open(config_path, "w") as f:
        f.write(f'mstr_key = "{new_key}"\n')

def change_master_key():
    st.title("Alterar Chave Mestre")
    st.write("Use esta página para alterar a chave mestre do sistema.")

    current_key = mstr_key

    # Input fields
    st.write(f"Chave Mestre Atual: `{current_key}`")
    new_key = st.text_input("Nova Chave Mestre", type="password")
    confirm_key = st.text_input("Confirme a Nova Chave Mestre", type="password")

    if st.button("Alterar Chave Mestre"):
        if not new_key or not confirm_key:
            st.warning("Por favor, preencha todos os campos.")
        elif new_key != confirm_key:
            st.error("As chaves não coincidem.")
        else:
            save_master_key(new_key)
            st.success("Chave Mestre alterada com sucesso!")
            time.sleep(2)
            st.rerun()